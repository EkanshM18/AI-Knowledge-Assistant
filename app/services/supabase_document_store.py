from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from app.core.config import Settings
from app.models.schemas import DocumentRecord, IngestionStatus, UploadFileResponse
from app.services.supabase_client import SupabaseClient


class SupabaseDocumentStore:
    def __init__(self, settings: Settings, client: SupabaseClient) -> None:
        self.settings = settings
        self.client = client

    def build_storage_path(self, filename: str, file_type: str) -> str:
        safe_name = filename.replace("/", "_").replace("\\", "_")
        return f"documents/{datetime.now(UTC).strftime('%Y/%m/%d')}/{uuid4().hex}_{safe_name}"

    async def create_document_record(
        self,
        *,
        filename: str,
        storage_path: str,
        file_type: str,
        file_size: int,
        mime_type: str,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        ingestion_status: IngestionStatus = "queued",
    ) -> DocumentRecord:
        timestamp = datetime.now(UTC).isoformat()
        payload = {
            "id": uuid4().hex,
            "filename": filename,
            "storage_path": storage_path,
            "file_type": file_type,
            "file_size": file_size,
            "mime_type": mime_type,
            "tags": tags or [],
            "metadata": metadata or {},
            "ingestion_status": ingestion_status,
            "vector_collection": self.settings.qdrant_collection,
            "vector_count": 0,
            "chunk_count": 0,
            "upload_timestamp": timestamp,
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        row = await self.client.create_document(payload)
        if isinstance(row, list) and row:
            return self._to_document_record(row[0])
        if isinstance(row, dict):
            return self._to_document_record(row)
        raise ValueError("Supabase did not return a document record")

    async def update_document_status(
        self,
        document_id: str,
        *,
        ingestion_status: IngestionStatus,
        chunk_count: int | None = None,
        vector_count: int | None = None,
        error_message: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> DocumentRecord | None:
        payload: dict[str, Any] = {
            "ingestion_status": ingestion_status,
            "updated_at": datetime.now(UTC).isoformat(),
        }
        if chunk_count is not None:
            payload["chunk_count"] = chunk_count
        if vector_count is not None:
            payload["vector_count"] = vector_count
        if error_message is not None:
            payload["error_message"] = error_message
        if metadata is not None:
            payload["metadata"] = metadata

        rows = await self.client.update_document(document_id, payload)
        if isinstance(rows, list) and rows:
            return self._to_document_record(rows[0])
        if isinstance(rows, dict) and rows:
            return self._to_document_record(rows)
        return None

    async def get_document(self, document_id: str) -> DocumentRecord | None:
        row = await self.client.get_document(document_id)
        return self._to_document_record(row) if row else None

    async def list_documents(self, limit: int = 100, offset: int = 0) -> list[DocumentRecord]:
        rows = await self.client.list_documents(limit=limit, offset=offset)
        return [self._to_document_record(row) for row in rows]

    def to_upload_response(self, record: DocumentRecord) -> UploadFileResponse:
        return UploadFileResponse(
            id=record.id,
            filename=record.filename,
            storage_path=record.storage_path,
            file_type=record.file_type,
            ingestion_status=record.ingestion_status,
            vector_collection=record.vector_collection,
            created_at=record.created_at,
        )

    def _to_document_record(self, row: dict[str, Any]) -> DocumentRecord:
        return DocumentRecord(
            id=row.get("id", ""),
            filename=row.get("filename", ""),
            storage_path=row.get("storage_path", ""),
            file_type=row.get("file_type", ""),
            created_at=self._parse_datetime(row.get("created_at")),
            updated_at=self._parse_datetime(row.get("updated_at")),
            upload_timestamp=self._parse_datetime(row.get("upload_timestamp")),
            ingestion_status=row.get("ingestion_status", "queued"),
            vector_collection=row.get("vector_collection"),
            vector_count=int(row.get("vector_count") or 0),
            chunk_count=int(row.get("chunk_count") or 0),
            file_size=row.get("file_size"),
            mime_type=row.get("mime_type"),
            error_message=row.get("error_message"),
            tags=row.get("tags") or [],
            metadata=row.get("metadata") or {},
        )

    def _parse_datetime(self, value: Any) -> datetime | None:
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
            return parsed
        except ValueError:
            return None
