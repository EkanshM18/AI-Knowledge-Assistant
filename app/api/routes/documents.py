import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.api.deps import get_container
from app.core.container import ApplicationContainer
from app.models.schemas import DocumentStatsResponse, UploadResponse

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=UploadResponse)
async def upload_documents(
    files: list[UploadFile] = File(...),
    tags: str = Form(default=""),
    container: ApplicationContainer = Depends(get_container),
) -> UploadResponse:
    tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
    saved_files: list[Path] = []

    for file in files:
        target_name = f"{uuid.uuid4().hex}_{file.filename}"
        target_path = container.settings.upload_dir / target_name
        with target_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        saved_files.append(target_path)

    summaries = [container.ingestion_service.ingest_file(path, tag_list) for path in saved_files]

    return UploadResponse(
        ingested_documents=sum(item["documents"] for item in summaries),
        ingested_chunks=sum(item["chunks"] for item in summaries),
        files=[
            {
                "stored_filename": path.name,
                "original_filename": path.name.split("_", 1)[-1],
            }
            for path in saved_files
        ],
    )


@router.get("/stats", response_model=DocumentStatsResponse)
def get_document_stats(
    container: ApplicationContainer = Depends(get_container),
) -> DocumentStatsResponse:
    stats = container.qdrant_service.get_stats()
    return DocumentStatsResponse(**stats)

