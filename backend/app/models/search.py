from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class SearchResult:
    content: str
    score: float
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class IndexedDocument:
    document_id: str
    file_name: str
    file_type: str
    uploaded_at: datetime
    indexed_chunks: int
