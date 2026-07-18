from app.prompts.rag_prompt import RAG_PROMPT
from app.services.ai.embedding_service import EmbeddingService
from app.services.search.search_service import SearchService
from app.services.ai.ai_service import AIService


class RAGService:
    """Handles Retrieval-Augmented Generation (RAG)."""

    def __init__(self):
        self._embedding_service = EmbeddingService()
        self._search_service = SearchService()
        self._ai_service = AIService()

    def retrieve(self, question: str) -> list[dict]:
        embedding = self._embedding_service.create_embedding(question)

        return self._search_service.search_documents(embedding)

    def ask(self, question: str) -> str:
        documents = self.retrieve(question)
        context = "\n\n".join(document["content"] for document in documents)

        prompt = RAG_PROMPT.format(
            context=context,
            question=question,
        )

        return self._ai_service.generate_response(prompt)
