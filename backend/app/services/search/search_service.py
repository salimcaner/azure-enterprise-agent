from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.models import VectorizedQuery
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
)

from app.core.config import settings
from app.models.search import SearchResult


class SearchService:
    """Service for interacting with Azure AI Search."""

    def __init__(self):
        self._client = SearchClient(
            endpoint=settings.search_endpoint,
            index_name=settings.search_index_name,
            credential=AzureKeyCredential(settings.search_api_key),
        )

        self._index_client = SearchIndexClient(
            endpoint=settings.search_endpoint,
            credential=AzureKeyCredential(settings.search_api_key),
        )

    def upload(self, documents: list[dict]) -> None:
        self._client.upload_documents(documents=documents)

    def search(self, embedding: list[float], query: str = None, top: int = 5) -> list[SearchResult]:
        vector_query = VectorizedQuery(
            vector=embedding,
            k_nearest_neighbors=top,
            fields="text_vector",
        )

        results = self._client.search(
            search_text=query,
            vector_queries=[vector_query],
            select=[
                "chunk",
                "title",
                "parent_id",
            ],
        )

        return [
            SearchResult(
                content=result["chunk"],
                score=result.get("@search.score", 0.0),
                metadata={
                    "file_name": result.get("title"),
                    "file_type": result.get("title", "").split(".")[-1] if result.get("title") and "." in result.get("title") else "pdf",
                    "uploaded_at": None,
                    "chunk_index": 0,
                    "document_id": result.get("parent_id"),
                },
            )
            for result in results
        ]

    def create_index(self) -> None:
        index = SearchIndex(
            name=settings.search_index_name,
            fields=[
                SimpleField(
                    name="id",
                    type=SearchFieldDataType.String,
                    key=True,
                ),
                SearchField(
                    name="content",
                    type=SearchFieldDataType.String,
                    searchable=True,
                ),
                SearchField(
                    name="embedding",
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    vector_search_dimensions=1536,
                    vector_search_profile_name="default-profile",
                ),
                SearchField(
                    name="file_name",
                    type=SearchFieldDataType.String,
                    searchable=True,
                    filterable=True,
                ),
                SimpleField(
                    name="file_type",
                    type=SearchFieldDataType.String,
                    filterable=True,
                ),
                SimpleField(
                    name="uploaded_at",
                    type=SearchFieldDataType.DateTimeOffset,
                    filterable=True,
                    sortable=True,
                ),
                SimpleField(
                    name="chunk_index",
                    type=SearchFieldDataType.Int32,
                    filterable=True,
                    sortable=True,
                ),
                SimpleField(
                    name="document_id",
                    type=SearchFieldDataType.String,
                    filterable=True,
                ),
            ],
            vector_search=VectorSearch(
                algorithms=[
                    HnswAlgorithmConfiguration(
                        name="default-hnsw",
                    ),
                ],
                profiles=[
                    VectorSearchProfile(
                        name="default-profile",
                        algorithm_configuration_name="default-hnsw",
                    ),
                ],
            ),
        )

        self._index_client.create_or_update_index(index)

    def list_documents(self) -> list[dict]:
        results = self._client.search(
            search_text="*",
            select=["parent_id", "title"],
            top=1000,
        )

        unique_docs = {}
        for r in results:
            doc_id = r.get("parent_id")
            if doc_id and doc_id not in unique_docs:
                unique_docs[doc_id] = {
                    "document_id": doc_id,
                    "file_name": r.get("title"),
                    "file_type": r.get("title", "").split(".")[-1] if r.get("title") and "." in r.get("title") else "pdf",
                    "uploaded_at": None,
                }

        return list(unique_docs.values())

    def get_document_by_id(self, document_id: str) -> list[dict]:
        results = self._client.search(
            search_text="*",
            filter=f"parent_id eq '{document_id}'",
            select=["title"],
            top=1,
        )
        return list(results)

    def delete_document(self, document_id: str) -> None:
        results = self._client.search(
            search_text="*",
            filter=f"parent_id eq '{document_id}'",
            select=["chunk_id"],
            top=1000,
        )
        keys_to_delete = [{"chunk_id": r["chunk_id"]} for r in results]

        if keys_to_delete:
            self._client.delete_documents(documents=keys_to_delete)

