from app.bots.general.agents.graph import GeneralAssistantGraph
from app.core.config import Settings
from app.models.schemas import ChatRequest, ChatResponse, ToolCall
from app.services.memory_service import MemoryService


class GeneralChatService:
    def __init__(
        self,
        settings: Settings,
        memory_service: MemoryService,
        agent_graph: GeneralAssistantGraph,
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
            }
        )

        self.memory_service.append(session_id, "user", request.message)
        self.memory_service.append(session_id, "assistant", result["answer"])

        tool_calls = [
            ToolCall(
                tool_name=item.get("tool_name", "tool"),
                status=item.get("status", "unknown"),
                summary=item.get("summary", ""),
                source_label=item.get("source_label", ""),
                source_url=item.get("source_url", ""),
            )
            for item in result.get("tool_results", [])
        ]

        return ChatResponse(
            session_id=session_id,
            bot_type="general",
            route=result.get("route", "conversation"),
            grounded=result.get("grounded", True),
            answer=result["answer"],
            validation_notes=result.get("validation_notes", ""),
            sources=[],
            tool_calls=tool_calls,
        )

