from fastapi import APIRouter
from app.models.schema import ChatRequest, ChatResponse
from app.services.rag_service import get_answer

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    result = get_answer(request.query)
    return result