from __future__ import annotations

from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from app.bots.enterprise.clients.qdrant_client import EnterpriseVectorClient
from app.core.config import Settings


class RetrievalService:
    def __init__(self, settings: Settings, vector_client: EnterpriseVectorClient) -> None:
        self.settings = settings
        self.vector_client = vector_client
        self.embedding_model = HuggingFaceEmbedding(model_name=self.settings.embedding_model)

    def retrieve(
        self,
        query: str,
        limit: int | None = None,
        metadata_filters: dict | None = None,
    ) -> list[dict]:
        query_embedding = self.embedding_model.get_query_embedding(query)
        points = self.vector_client.search(
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

