from app.services.document.excel_service import ExcelService
from app.services.document.powerpoint_service import PowerPointService
from app.services.document.word_service import WordService
from backend.app.services.ai.embedding_service import EmbeddingService
from backend.app.services.document.chunk_service import ChunkService
from backend.app.services.document.pdf_service import PDFService
from backend.app.services.search.search_service import SearchService


class DocumentIndexService:
    def __init__(self):
        self._pdf_service = PDFService()
        self._chunk_service = ChunkService()
        self._embedding_service = EmbeddingService()
        self._search_service = SearchService()

    def index_pdf(self, file_path: str) -> int:
        text = self._pdf_service.extract_text(file_path)

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
    
    def index_document(self, file_path: str) -> int:
        extension = Path(file_path).suffix.lower()

        if extension == ".pdf":
            return self.index_pdf(file_path)

        raise ValueError(f"Unsupported file type: {extension}")
    
    def _index_text(self, text: str) -> int:
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