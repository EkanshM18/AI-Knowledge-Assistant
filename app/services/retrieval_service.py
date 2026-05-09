from __future__ import annotations

from qdrant_client.http import models as qdrant_models

from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from app.core.config import Settings
from app.services.vector_service import QdrantService


class RetrievalService:
    def __init__(self, settings: Settings, qdrant_service: QdrantService) -> None:
        self.settings = settings
        self.qdrant_service = qdrant_service
        self.embedding_model = HuggingFaceEmbedding(model_name=self.settings.embedding_model)

    def retrieve(
        self,
        query: str,
        limit: int | None = None,
        metadata_filters: dict | None = None,
    ) -> list[dict]:
        query_embedding = self.embedding_model.get_query_embedding(query)
        points = self.qdrant_service.search(
            query_embedding=query_embedding,
            limit=limit or self.settings.top_k,
            metadata_filters=metadata_filters or {},
        )

        results: list[dict] = []
        for point in points:
            payload = point.payload or {}
            results.append(
                {
                    "chunk_id": str(point.id),
                    "filename": payload.get("filename", "unknown"),
                    "source": payload.get("source", ""),
                    "page_number": payload.get("page_number"),
                    "tags": payload.get("tags", []),
                    "text": payload.get("text", ""),
                    "score": float(point.score or 0.0),
                }
            )
        return results

    def build_filter(self, metadata_filters: dict) -> qdrant_models.Filter | None:
        if not metadata_filters:
            return None

        conditions = []
        for key, value in metadata_filters.items():
            if isinstance(value, list):
                conditions.append(
                    qdrant_models.FieldCondition(
                        key=key,
                        match=qdrant_models.MatchAny(any=value),
                    )
                )
            else:
                conditions.append(
                    qdrant_models.FieldCondition(
                        key=key,
                        match=qdrant_models.MatchValue(value=value),
                    )
                )

        return qdrant_models.Filter(must=conditions) if conditions else None

