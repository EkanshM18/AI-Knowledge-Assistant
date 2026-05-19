from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

import httpx

from app.core.config import Settings


class SupabaseError(RuntimeError):
    pass


@dataclass(frozen=True)
class SupabaseObjectResponse:
    path: str
    content_type: str
    size: int


class SupabaseClient:
    def __init__(self, settings: Settings) -> None:
        if not settings.supabase_url:
            raise ValueError("SUPABASE_URL is required")
        if not settings.supabase_service_role_key:
            raise ValueError("SUPABASE_SERVICE_ROLE_KEY is required")

        self.settings = settings
        self.base_url = settings.supabase_url.rstrip("/")
        self.service_role_key = settings.supabase_service_role_key
        self.storage_bucket = settings.supabase_storage_bucket
        self.documents_table = settings.supabase_documents_table
        self._api_base = f"{self.base_url}/rest/v1"
        self._storage_base = f"{self.base_url}/storage/v1/object"

    def _headers(self, extra: dict[str, str] | None = None) -> dict[str, str]:
        headers = {
            "apikey": self.service_role_key,
            "Authorization": f"Bearer {self.service_role_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }
        if extra:
            headers.update(extra)
        return headers

    async def create_document(self, payload: dict[str, Any]) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.settings.http_timeout_seconds) as client:
            response = await client.post(
                f"{self._api_base}/{self.documents_table}",
                headers=self._headers(),
                json=payload,
            )
        return self._decode_json_response(response, expected_status={200, 201})

    async def update_document(self, document_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.settings.http_timeout_seconds) as client:
            response = await client.patch(
                f"{self._api_base}/{self.documents_table}?id=eq.{quote(document_id)}",
                headers=self._headers(),
                json=payload,
            )
        return self._decode_json_response(response, expected_status={200})

    async def list_documents(self, limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
        params = (
            f"select=*&order=created_at.desc&limit={limit}&offset={offset}"
        )
        async with httpx.AsyncClient(timeout=self.settings.http_timeout_seconds) as client:
            response = await client.get(
                f"{self._api_base}/{self.documents_table}?{params}",
                headers=self._headers({"Content-Type": "application/json"}),
            )
        return self._decode_json_response(response, expected_status={200})

    async def get_document(self, document_id: str) -> dict[str, Any] | None:
        params = f"select=*&id=eq.{quote(document_id)}&limit=1"
        async with httpx.AsyncClient(timeout=self.settings.http_timeout_seconds) as client:
            response = await client.get(
                f"{self._api_base}/{self.documents_table}?{params}",
                headers=self._headers({"Content-Type": "application/json"}),
            )
        rows = self._decode_json_response(response, expected_status={200})
        return rows[0] if rows else None

    async def upload_object(self, object_path: str, content: bytes, content_type: str) -> SupabaseObjectResponse:
        encoded_path = "/".join(quote(part) for part in object_path.split("/"))
        upload_url = f"{self._storage_base}/{self.storage_bucket}/{encoded_path}"

        async with httpx.AsyncClient(timeout=self.settings.http_timeout_seconds * 3) as client:
            response = await client.post(
                upload_url,
                headers=self._headers(
                    {
                        "Content-Type": content_type,
                        "x-upsert": "true",
                    }
                ),
                content=content,
            )

        self._ensure_success(response, expected_status={200, 201})
        return SupabaseObjectResponse(path=object_path, content_type=content_type, size=len(content))

    async def download_object(self, object_path: str) -> bytes:
        encoded_path = "/".join(quote(part) for part in object_path.split("/"))
        download_url = f"{self._storage_base}/{self.storage_bucket}/{encoded_path}"

        async with httpx.AsyncClient(timeout=self.settings.http_timeout_seconds * 3) as client:
            response = await client.get(download_url, headers=self._headers({"Content-Type": "application/json"}))

        self._ensure_success(response, expected_status={200})
        return response.content

    def public_object_url(self, object_path: str) -> str:
        encoded_path = "/".join(quote(part) for part in object_path.split("/"))
        return f"{self.base_url}/storage/v1/object/public/{self.storage_bucket}/{encoded_path}"

    def _ensure_success(self, response: httpx.Response, expected_status: set[int]) -> None:
        if response.status_code in expected_status:
            return
        raise SupabaseError(self._extract_error(response)) from None

    def _decode_json_response(self, response: httpx.Response, expected_status: set[int]) -> Any:
        self._ensure_success(response, expected_status=expected_status)
        if response.status_code == 204 or not response.content:
            return {}
        return response.json()

    def _extract_error(self, response: httpx.Response) -> str:
        try:
            payload = response.json()
            if isinstance(payload, dict):
                return payload.get("message") or payload.get("error_description") or str(payload)
            return str(payload)
        except Exception:
            return response.text or f"Supabase request failed with status {response.status_code}"
