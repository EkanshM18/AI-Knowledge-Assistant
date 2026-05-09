from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
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


class ChatResponse(BaseModel):
    session_id: str
    route: str
    grounded: bool
    answer: str
    validation_notes: str
    sources: list[SourceCitation] = Field(default_factory=list)


class UploadResponse(BaseModel):
    ingested_documents: int
    ingested_chunks: int
    files: list[dict[str, str]]


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

