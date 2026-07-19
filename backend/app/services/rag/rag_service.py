from app.prompts.rag_prompt import RAG_PROMPT
from app.models.search import SearchResult
from app.services.ai.embedding_service import EmbeddingService
from app.services.search.search_service import SearchService
from app.services.ai.ai_service import AIService


class RAGService:
    """Handles Retrieval-Augmented Generation (RAG)."""

    def __init__(self, ai_service: AIService):
        self._embedding_service = EmbeddingService()
        self._search_service = SearchService()
        self._ai_service = ai_service

    def retrieve(self, question: str) -> list[SearchResult]:
        embedding = self._embedding_service.create_embedding(question)

        return self._search_service.search(embedding, query=question)

    def ask(self, question: str) -> str:
        search_query = self._ai_service.reformulate_query(question)
        documents = self.retrieve(search_query)
        context = "\n\n".join(document.content for document in documents)

        rag_prompt = RAG_PROMPT.format(
            context=context,
            question=question,
        )

        return self._ai_service.rag_chat(rag_prompt, question)
