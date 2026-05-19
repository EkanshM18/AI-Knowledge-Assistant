from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter

from app.core.config import Settings
from app.models.schemas import DocumentRecord, IngestionStatus
from app.services.document_loader import DocumentLoader
from app.services.retrieval_service import RetrievalService
from app.services.supabase_client import SupabaseClient, SupabaseError
from app.services.supabase_document_store import SupabaseDocumentStore
from app.services.vector_service import QdrantService


@dataclass(frozen=True)
class IngestionResult:
    document_id: str
    document_count: int
    chunk_count: int


class IngestionService:
    def __init__(
        self,
        settings: Settings,
        loader: DocumentLoader,
        qdrant_service: QdrantService,
        retrieval_service: RetrievalService,
        supabase_client: SupabaseClient,
        document_store: SupabaseDocumentStore,
    ) -> None:
        self.settings = settings
        self.loader = loader
        self.qdrant_service = qdrant_service
        self.retrieval_service = retrieval_service
        self.supabase_client = supabase_client
        self.document_store = document_store
        self.pipeline = IngestionPipeline(
            transformations=[
                SentenceSplitter(
                    chunk_size=self.settings.chunk_size,
                    chunk_overlap=self.settings.chunk_overlap,
                ),
                self.retrieval_service.embedding_model,
            ]
        )

    async def ingest_document(self, document_id: str) -> IngestionResult:
        record = await self.document_store.get_document(document_id)
        if record is None:
            raise ValueError(f"Document not found: {document_id}")

        await self.document_store.update_document_status(
            document_id,
            ingestion_status="processing",
        )

        try:
            content = await self.supabase_client.download_object(record.storage_path)
            documents = self.loader.load_from_bytes(
                filename=record.filename,
                content=content,
                tags=record.tags,
                source_path=record.storage_path,
            )
            if not documents:
                await self.document_store.update_document_status(
                    document_id,
                    ingestion_status="failed",
                    error_message="No extractable content found in uploaded file",
                )
                return IngestionResult(document_id=document_id, document_count=0, chunk_count=0)

            nodes = self.pipeline.run(documents=documents)
            chunk_count = self.qdrant_service.upsert_nodes(nodes)

            await self.document_store.update_document_status(
                document_id,
                ingestion_status="completed",
                chunk_count=chunk_count,
                vector_count=chunk_count,
                metadata={
                    "storage_path": record.storage_path,
                    "source": record.storage_path,
                    "filename": record.filename,
                    "file_type": record.file_type,
                    "vector_collection": self.settings.qdrant_collection,
                },
            )
            return IngestionResult(
                document_id=document_id,
                document_count=len(documents),
                chunk_count=chunk_count,
            )
        except Exception as exc:
            await self.document_store.update_document_status(
                document_id,
                ingestion_status="failed",
                error_message=str(exc),
            )
            raise

    async def ingest_documents(self, document_ids: list[str]) -> list[IngestionResult]:
        results: list[IngestionResult] = []
        for document_id in document_ids:
            results.append(await self.ingest_document(document_id))
        return results

    async def ingest_supabase_object(self, document_id: str) -> None:
        await self.ingest_document(document_id)

    async def ingest_file(self, file_path, tags: list[str] | None = None) -> dict[str, int]:
        documents = self.loader.load(file_path, tags=tags)
        if not documents:
            return {"documents": 0, "chunks": 0}

        nodes = self.pipeline.run(documents=documents)
        upserted = self.qdrant_service.upsert_nodes(nodes)
        return {"documents": len(documents), "chunks": upserted}
