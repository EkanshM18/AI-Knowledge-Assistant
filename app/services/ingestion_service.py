from __future__ import annotations

from pathlib import Path

from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter

from app.core.config import Settings
from app.services.document_loader import DocumentLoader
from app.services.retrieval_service import RetrievalService
from app.services.vector_service import QdrantService


class IngestionService:
    def __init__(
        self,
        settings: Settings,
        loader: DocumentLoader,
        qdrant_service: QdrantService,
        retrieval_service: RetrievalService,
    ) -> None:
        self.settings = settings
        self.loader = loader
        self.qdrant_service = qdrant_service
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
        upserted = self.qdrant_service.upsert_nodes(nodes)
        self.pipeline.persist(str(self.settings.resolve_path(self.settings.pipeline_cache_dir)))
        return {"documents": len(documents), "chunks": upserted}

    def _load_cache_if_present(self) -> None:
        cache_dir = self.settings.resolve_path(self.settings.pipeline_cache_dir)
        if any(cache_dir.iterdir()):
            try:
                self.pipeline.load(str(cache_dir))
            except Exception:
                pass

