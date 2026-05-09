from app.agents.graph import KnowledgeAssistantGraph
from app.core.config import Settings
from app.models.schemas import ChatRequest, ChatResponse, SourceCitation
from app.services.memory_service import MemoryService


class ChatService:
    def __init__(
        self,
        settings: Settings,
        memory_service: MemoryService,
        agent_graph: KnowledgeAssistantGraph,
    ) -> None:
        self.settings = settings
        self.memory_service = memory_service
        self.agent_graph = agent_graph

    def chat(self, request: ChatRequest) -> ChatResponse:
        session_id = self.memory_service.ensure_session(request.session_id)

        result = self.agent_graph.invoke(
            {
                "session_id": session_id,
                "question": request.message,
                "top_k": request.top_k or self.settings.top_k,
                "metadata_filters": request.metadata_filters or {},
            }
        )

        self.memory_service.append(session_id, "user", request.message)
        self.memory_service.append(session_id, "assistant", result["answer"])

        citations = [
            SourceCitation(
                chunk_id=chunk["chunk_id"],
                filename=chunk["filename"],
                source=chunk["source"],
                page_number=chunk.get("page_number"),
                score=chunk["score"],
                tags=chunk.get("tags", []),
                excerpt=chunk["text"][:280],
            )
            for chunk in result.get("retrieved_chunks", [])
        ]

        return ChatResponse(
            session_id=session_id,
            route=result.get("route", "retrieval"),
            grounded=result.get("grounded", False),
            answer=result["answer"],
            validation_notes=result.get("validation_notes", ""),
            sources=citations,
        )

