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

    def upload_documents(self, documents: list[dict]) -> None:
        self._client.upload_documents(documents=documents)

    def search_documents(self, embedding: list[float], top: int = 3) -> list[dict]:
        vector_query = VectorizedQuery(
            vector=embedding,
            k_nearest_neighbors=top,
            fields="embedding",
        )

        results = self._client.search(
            search_text=None,
            vector_queries=[vector_query],
            select=["content"],
        )

        return list(results)

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
