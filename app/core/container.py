from app.agents.graph import KnowledgeAssistantGraph
from app.core.config import Settings, get_settings
from app.services.chat_service import ChatService
from app.services.document_loader import DocumentLoader
from app.services.generation_service import GenerationService
from app.services.ingestion_service import IngestionService
from app.services.memory_service import MemoryService
from app.services.retrieval_service import RetrievalService
from app.services.vector_service import QdrantService


class ApplicationContainer:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.document_loader = DocumentLoader()
        self.memory_service = MemoryService()
        self.qdrant_service = QdrantService(self.settings)
        self.retrieval_service = RetrievalService(self.settings, self.qdrant_service)
        self.generation_service = GenerationService(self.settings)
        self.ingestion_service = IngestionService(
            settings=self.settings,
            loader=self.document_loader,
            qdrant_service=self.qdrant_service,
            retrieval_service=self.retrieval_service,
        )
        self.agent_graph = KnowledgeAssistantGraph(
            memory_service=self.memory_service,
            retrieval_service=self.retrieval_service,
            generation_service=self.generation_service,
        )
        self.chat_service = ChatService(
            settings=self.settings,
            memory_service=self.memory_service,
            agent_graph=self.agent_graph,
        )

    def close(self) -> None:
        self.qdrant_service.close()

