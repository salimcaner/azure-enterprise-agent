from app.services.rag.rag_service import RAGService
from app.services.ai.ai_service import AIService


class RagTool:
    name = "rag"

    def __init__(self, ai_service: AIService):
        self._rag_service = RAGService(ai_service)

    def execute(self, message: str) -> str:
        return self._rag_service.ask(message)
