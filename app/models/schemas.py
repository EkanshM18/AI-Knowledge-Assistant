from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

BotType = Literal["enterprise", "general"]
IngestionStatus = Literal["queued", "uploading", "uploaded", "processing", "completed", "failed"]


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    bot_type: BotType = "enterprise"
    session_id: str | None = None
    top_k: int | None = Field(default=None, ge=1, le=10)
    metadata_filters: dict[str, Any] | None = None


class SourceCitation(BaseModel):
    chunk_id: str
    filename: str
    source: str
    page_number: int | None = None
    score: float
    tags: list[str] = Field(default_factory=list)
    excerpt: str


class ToolCall(BaseModel):
    tool_name: str
    status: str
    summary: str
    source_label: str
    source_url: str = ""


class ChatResponse(BaseModel):
    session_id: str
    bot_type: BotType = "enterprise"
    route: str
    grounded: bool
    answer: str
    validation_notes: str
    sources: list[SourceCitation] = Field(default_factory=list)
    tool_calls: list[ToolCall] = Field(default_factory=list)


class DocumentRecord(BaseModel):
    id: str
    filename: str
    storage_path: str
    file_type: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
    upload_timestamp: datetime | None = None
    ingestion_status: IngestionStatus
    vector_collection: str | None = None
    vector_count: int = 0
    chunk_count: int = 0
    file_size: int | None = None
    mime_type: str | None = None
    error_message: str | None = None
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class UploadFileResponse(BaseModel):
    id: str
    filename: str
    storage_path: str
    file_type: str
    ingestion_status: IngestionStatus
    vector_collection: str | None = None
    created_at: datetime | None = None


class UploadResponse(BaseModel):
    ingested_documents: int
    ingested_chunks: int
    files: list[UploadFileResponse]


class DocumentListResponse(BaseModel):
    items: list[DocumentRecord]
    total: int


class DocumentStatsResponse(BaseModel):
    collection_name: str
    vector_count: int
    unique_files: int
    filenames: list[str] = Field(default_factory=list)


class HealthResponse(BaseModel):
    status: str
    app_name: str
    collection_name: str
    vector_count: int
    unique_files: int
