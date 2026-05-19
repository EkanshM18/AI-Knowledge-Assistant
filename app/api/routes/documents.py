from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.api.deps import get_container
from app.core.container import ApplicationContainer
from app.models.schemas import DocumentListResponse, DocumentStatsResponse, UploadResponse

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=UploadResponse)
async def upload_documents(
    files: list[UploadFile] = File(...),
    tags: str = Form(default=""),
    container: ApplicationContainer = Depends(get_container),
) -> UploadResponse:
    tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
    uploaded_files = []

    for file in files:
        content = await file.read()
        file_type = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "unknown"
        storage_path = container.document_store.build_storage_path(file.filename, file_type)

        await container.supabase_client.upload_object(
            storage_path,
            content,
            file.content_type or "application/octet-stream",
        )

        record = await container.document_store.create_document_record(
            filename=file.filename,
            storage_path=storage_path,
            file_type=file_type,
            file_size=len(content),
            mime_type=file.content_type or "application/octet-stream",
            tags=tag_list,
            metadata={
                "original_filename": file.filename,
                "tags": tag_list,
                "supabase_bucket": container.settings.supabase_storage_bucket,
            },
            ingestion_status="uploaded",
        )

        asyncio.create_task(container.ingestion_service.ingest_document(record.id))
        uploaded_files.append(container.document_store.to_upload_response(record))

    return UploadResponse(
        ingested_documents=len(uploaded_files),
        ingested_chunks=0,
        files=uploaded_files,
    )


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    container: ApplicationContainer = Depends(get_container),
) -> DocumentListResponse:
    items = await container.document_store.list_documents(limit=1000)
    return DocumentListResponse(items=items, total=len(items))


@router.get("/stats", response_model=DocumentStatsResponse)
def get_document_stats(
    container: ApplicationContainer = Depends(get_container),
) -> DocumentStatsResponse:
    stats = container.qdrant_service.get_stats()
    return DocumentStatsResponse(**stats)
