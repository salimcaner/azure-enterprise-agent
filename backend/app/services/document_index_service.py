from pathlib import Path
from typing import Protocol

from app.services.ai.embedding_service import EmbeddingService
from app.services.document.chunk_service import ChunkService
from app.services.document.excel_service import ExcelService
from app.services.document.pdf_service import PDFService
from app.services.document.powerpoint_service import PowerPointService
from app.services.document.word_service import WordService
from app.services.search.search_service import SearchService


class DocumentReader(Protocol):
    def extract_text(self, file_path: str) -> str:
        """Extract plain text from the given document."""


class DocumentIndexService:
    def __init__(self):
        self._chunk_service = ChunkService()
        self._embedding_service = EmbeddingService()
        self._search_service = SearchService()

        self._reader_registry: dict[str, DocumentReader] = {
            ".pdf": PDFService(),
            ".docx": WordService(),
            ".xlsx": ExcelService(),
            ".pptx": PowerPointService(),
        }

    def index_document(self, file_path: str) -> int:
        suffix = Path(file_path).suffix.lower()
        reader = self._reader_registry.get(suffix)

        if reader is None:
            supported_extensions = ", ".join(sorted(self._reader_registry))
            raise ValueError(
                f"Unsupported document type '{suffix}'. "
                f"Supported types: {supported_extensions}"
            )

        text = reader.extract_text(file_path)

        return self._index_text(text)

    def _index_text(self, text: str) -> int:
        if not text:
            return 0

        chunks = self._chunk_service.create_chunks(text)

        documents = []

        for index, chunk in enumerate(chunks):
            embedding = self._embedding_service.create_embedding(chunk)

            documents.append(
                {
                    "id": str(index),
                    "content": chunk,
                    "embedding": embedding,
                }
            )

        self._search_service.upload_documents(documents)

        return len(documents)
