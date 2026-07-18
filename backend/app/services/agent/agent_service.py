from app.models.agent import AgentAction
from app.services.ai.ai_service import AIService
from app.services.rag.rag_service import RAGService


class AgentService:
    def __init__(self):
        self._ai_service = AIService()
        self._rag_service = RAGService()

    def chat(self, message: str) -> str:
        action = self._ai_service.classify(message)

        if action == AgentAction.RAG:
            return self._rag_service.ask(message)

        return self._ai_service.chat(message)
