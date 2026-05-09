from __future__ import annotations

from llama_index.core.schema import BaseNode
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models

from app.core.config import Settings


class EnterpriseVectorClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = QdrantClient(path=str(self.settings.resolve_path(self.settings.qdrant_path)))

    def ensure_collection(self, vector_size: int) -> None:
        if self.client.collection_exists(self.settings.qdrant_collection):
            return

        self.client.create_collection(
            collection_name=self.settings.qdrant_collection,
            vectors_config=qdrant_models.VectorParams(
                size=vector_size,
                distance=qdrant_models.Distance.COSINE,
            ),
        )

    def upsert_nodes(self, nodes: list[BaseNode]) -> int:
        if not nodes:
            return 0

        first_embedding = nodes[0].embedding or []
        self.ensure_collection(len(first_embedding))

        points = []
        for node in nodes:
            embedding = node.embedding or []
            text = getattr(node, "text", None) or node.get_content()
            metadata = node.metadata or {}
            payload = {
                "text": text,
                "filename": metadata.get("filename", ""),
                "page_number": metadata.get("page_number"),
                "source": metadata.get("source", ""),
                "tags": metadata.get("tags", []),
                "timestamp": metadata.get("timestamp", ""),
                "document_id": getattr(node, "ref_doc_id", None),
                "metadata": metadata,
            }
            points.append(
                qdrant_models.PointStruct(
                    id=str(node.node_id),
                    vector=embedding,
                    payload=payload,
                )
            )

        self.client.upsert(collection_name=self.settings.qdrant_collection, points=points)
        return len(points)

    def search(self, query_embedding: list[float], limit: int, metadata_filters: dict):
        if not self.client.collection_exists(self.settings.qdrant_collection):
            return []

        query_filter = self._build_filter(metadata_filters)
        return self.client.search(
            collection_name=self.settings.qdrant_collection,
            query_vector=query_embedding,
            query_filter=query_filter,
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )

    def get_stats(self) -> dict:
        if not self.client.collection_exists(self.settings.qdrant_collection):
            return {
                "collection_name": self.settings.qdrant_collection,
                "vector_count": 0,
                "unique_files": 0,
                "filenames": [],
            }

        count = self.client.count(collection_name=self.settings.qdrant_collection, exact=True).count
        points, _ = self.client.scroll(
            collection_name=self.settings.qdrant_collection,
            with_payload=["filename"],
            limit=1000,
        )
        filenames = sorted(
            {
                point.payload.get("filename")
                for point in points
                if point.payload and point.payload.get("filename")
            }
        )
        return {
            "collection_name": self.settings.qdrant_collection,
            "vector_count": count,
            "unique_files": len(filenames),
            "filenames": filenames,
        }

    def close(self) -> None:
        self.client.close()

    def _build_filter(self, metadata_filters: dict) -> qdrant_models.Filter | None:
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

        return qdrant_models.Filter(must=conditions)

