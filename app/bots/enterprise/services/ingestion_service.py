from __future__ import annotations

from pathlib import Path

from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter

from app.bots.enterprise.clients.qdrant_client import EnterpriseVectorClient
from app.bots.enterprise.services.document_loader import DocumentLoader
from app.bots.enterprise.services.retrieval_service import RetrievalService
from app.core.config import Settings


class IngestionService:
    def __init__(
        self,
        settings: Settings,
        loader: DocumentLoader,
        vector_client: EnterpriseVectorClient,
        retrieval_service: RetrievalService,
    ) -> None:
        self.settings = settings
        self.loader = loader
        self.vector_client = vector_client
        self.retrieval_service = retrieval_service
        self.pipeline = IngestionPipeline(
            transformations=[
                SentenceSplitter(
                    chunk_size=self.settings.chunk_size,
                    chunk_overlap=self.settings.chunk_overlap,
                ),
                self.retrieval_service.embedding_model,
            ]
        )
        self._load_cache_if_present()

    def ingest_file(self, file_path: Path, tags: list[str] | None = None) -> dict[str, int]:
        documents = self.loader.load(file_path, tags=tags)
        if not documents:
            return {"documents": 0, "chunks": 0}

        nodes = self.pipeline.run(documents=documents)
        upserted = self.vector_client.upsert_nodes(nodes)
        self.pipeline.persist(str(self.settings.resolve_path(self.settings.pipeline_cache_dir)))
        return {"documents": len(documents), "chunks": upserted}

    def _load_cache_if_present(self) -> None:
        cache_dir = self.settings.resolve_path(self.settings.pipeline_cache_dir)
        if any(cache_dir.iterdir()):
            try:
                self.pipeline.load(str(cache_dir))
            except Exception:
                pass

