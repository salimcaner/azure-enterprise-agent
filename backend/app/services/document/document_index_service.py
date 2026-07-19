from datetime import datetime, timezone
from pathlib import Path
from shutil import copyfileobj
from typing import Protocol
from uuid import uuid4

from app.models.search import IndexedDocument
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
    """Ingestion pipeline for supported document types."""

    def __init__(self):
        self._upload_directory = Path("data/uploads")
        self._chunk_service = ChunkService()
        self._embedding_service = EmbeddingService()
        self._search_service = SearchService()

        self._reader_registry: dict[str, DocumentReader] = {
            ".pdf": PDFService(),
            ".docx": WordService(),
            ".xlsx": ExcelService(),
            ".pptx": PowerPointService(),
        }

    def index_upload(self, file) -> IndexedDocument:
        self._upload_directory.mkdir(parents=True, exist_ok=True)

        file_path = self._upload_directory / Path(file.filename).name

        with file_path.open("wb") as destination:
            copyfileobj(file.file, destination)

        return self.index_document(str(file_path))

    def index_document(self, file_path: str) -> IndexedDocument:
        path = Path(file_path)
        suffix = path.suffix.lower()
        reader = self._reader_registry.get(suffix)

        if reader is None:
            supported_extensions = ", ".join(sorted(self._reader_registry))
            raise ValueError(
                f"Unsupported document type '{suffix}'. "
                f"Supported types: {supported_extensions}"
            )

        text = reader.extract_text(file_path)
        document_id = str(uuid4())
        uploaded_at = datetime.now(timezone.utc)
        indexed_chunks = self._index_text(
            text=text,
            document_id=document_id,
            file_name=path.name,
            file_type=suffix.removeprefix("."),
            uploaded_at=uploaded_at,
        )

        return IndexedDocument(
            document_id=document_id,
            file_name=path.name,
            file_type=suffix.removeprefix("."),
            uploaded_at=uploaded_at,
            indexed_chunks=indexed_chunks,
        )

    def _index_text(
        self,
        text: str,
        document_id: str,
        file_name: str,
        file_type: str,
        uploaded_at: datetime,
    ) -> int:
        if not text:
            return 0

        chunks = self._chunk_service.create_chunks(text)

        documents = []

        for chunk_index, chunk in enumerate(chunks):
            embedding = self._embedding_service.create_embedding(chunk)

            documents.append(
                {
                    "id": f"{document_id}-{chunk_index}",
                    "content": chunk,
                    "embedding": embedding,
                    "file_name": file_name,
                    "file_type": file_type,
                    "uploaded_at": uploaded_at,
                    "chunk_index": chunk_index,
                    "document_id": document_id,
                }
            )

        self._search_service.upload(documents)

        return len(documents)

    def list_documents(self) -> list[IndexedDocument]:
        docs_data = self._search_service.list_documents()
        return [
            IndexedDocument(
                document_id=doc["document_id"],
                file_name=doc["file_name"],
                file_type=doc["file_type"],
                uploaded_at=doc["uploaded_at"],
                indexed_chunks=0,
            )
            for doc in docs_data
        ]

    def delete_document(self, document_id: str) -> str:
        metadata = self._search_service.get_document_by_id(document_id)
        if not metadata:
            raise ValueError(f"Document with ID {document_id} not found in search index.")

        file_name = metadata[0]["file_name"]

        self._search_service.delete_document(document_id)

        file_path = self._upload_directory / file_name
        if file_path.exists():
            file_path.unlink()

        return file_name

