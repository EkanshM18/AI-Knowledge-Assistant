from app.bots.enterprise.agents.graph import EnterpriseAssistantGraph
from app.bots.enterprise.services.chat_service import EnterpriseChatService
from app.bots.general.agents.graph import GeneralAssistantGraph
from app.bots.general.clients.news_client import NewsClient
from app.bots.general.clients.weather_client import WeatherClient
from app.bots.general.services.chat_service import GeneralChatService
from app.bots.general.services.joke import JokeService
from app.bots.general.services.tool_service import GeneralToolService
from app.bots.general.services.weather import WeatherService
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
        self.generation_service = GenerationService(self.settings)
        self._retrieval_service: RetrievalService | None = None
        self._ingestion_service: IngestionService | None = None
        self._enterprise_agent_graph: EnterpriseAssistantGraph | None = None
        self._enterprise_chat_service: EnterpriseChatService | None = None
        self.weather_client = WeatherClient(self.settings)
        self.news_client = NewsClient(self.settings)
        self.joke_service = JokeService()
        self.weather_service = WeatherService(self.weather_client)
        self.general_tool_service = GeneralToolService(
            settings=self.settings,
            weather_service=self.weather_service,
            news_client=self.news_client,
            joke_service=self.joke_service,
        )
        self.general_agent_graph = GeneralAssistantGraph(
            memory_service=self.memory_service,
            tool_service=self.general_tool_service,
            generation_service=self.generation_service,
        )
        self.general_chat_service = GeneralChatService(
            settings=self.settings,
            memory_service=self.memory_service,
            agent_graph=self.general_agent_graph,
        )
        self.chat_service = ChatService(
            enterprise_chat_service_factory=lambda: self.enterprise_chat_service,
            general_chat_service=self.general_chat_service,
        )

    @property
    def retrieval_service(self) -> RetrievalService:
        if self._retrieval_service is None:
            self._retrieval_service = RetrievalService(self.settings, self.qdrant_service)
        return self._retrieval_service

    @property
    def ingestion_service(self) -> IngestionService:
        if self._ingestion_service is None:
            self._ingestion_service = IngestionService(
                settings=self.settings,
                loader=self.document_loader,
                qdrant_service=self.qdrant_service,
                retrieval_service=self.retrieval_service,
            )
        return self._ingestion_service

    @property
    def enterprise_agent_graph(self) -> EnterpriseAssistantGraph:
        if self._enterprise_agent_graph is None:
            self._enterprise_agent_graph = EnterpriseAssistantGraph(
                memory_service=self.memory_service,
                retrieval_service=self.retrieval_service,
                generation_service=self.generation_service,
            )
        return self._enterprise_agent_graph

    @property
    def enterprise_chat_service(self) -> EnterpriseChatService:
        if self._enterprise_chat_service is None:
            self._enterprise_chat_service = EnterpriseChatService(
                settings=self.settings,
                memory_service=self.memory_service,
                agent_graph=self.enterprise_agent_graph,
            )
        return self._enterprise_chat_service

    def close(self) -> None:
        self.qdrant_service.close()

