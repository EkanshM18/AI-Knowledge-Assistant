from fastapi import APIRouter, Depends

from app.api.deps import get_container
from app.core.container import ApplicationContainer
from app.models.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    container: ApplicationContainer = Depends(get_container),
) -> ChatResponse:
    return container.chat_service.chat(request)

