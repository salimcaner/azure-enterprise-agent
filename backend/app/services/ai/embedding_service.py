from openai import OpenAI

from azure.identity import DefaultAzureCredential, get_bearer_token_provider

from app.core.config import settings

class EmbeddingService:
    """Service for generating text embeddings."""

    def __init__(self):
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(),
            "https://cognitiveservices.azure.com/.default",
        )

        self._client = OpenAI(
            base_url=settings.project_endpoint,
            api_key=token_provider,
        )

    def create_embedding(self, text: str) -> list[float]:
        response = self._client.embeddings.create(
            model=settings.embedding_deployment,
            input=text,
        )

        return response.data[0].embedding
