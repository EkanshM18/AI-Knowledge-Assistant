from collections.abc import Callable

from app.bots.enterprise.services.chat_service import EnterpriseChatService
from app.bots.general.services.chat_service import GeneralChatService
from app.models.schemas import ChatRequest, ChatResponse


class ChatService:
    def __init__(
        self,
        enterprise_chat_service_factory: Callable[[], EnterpriseChatService],
        general_chat_service: GeneralChatService,
    ) -> None:
        self.enterprise_chat_service_factory = enterprise_chat_service_factory
        self.general_chat_service = general_chat_service

    def chat(self, request: ChatRequest) -> ChatResponse:
        if request.bot_type == "general":
            return self.general_chat_service.chat(request)
        return self.enterprise_chat_service_factory().chat(request)

