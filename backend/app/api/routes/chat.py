from fastapi import APIRouter

from app.models.chat import ChatRequest, ChatResponse
from app.services.agent.agent_service import AgentService

router = APIRouter()
agent_service = AgentService()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    answer = agent_service.chat(request.message)

    return ChatResponse(answer=answer)
