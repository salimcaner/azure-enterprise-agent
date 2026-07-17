from openai import OpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

from app.core.config import settings


class AIService:
    """Handles communication with Azure AI Foundry."""

    def __init__(self) -> None:
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(),
            "https://ai.azure.com/.default",
        )

        self._client = OpenAI(
            base_url=settings.project_endpoint,
            api_key=token_provider,
        )

    def generate_response(self, prompt: str) -> str:
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        response = self._client.responses.create(
            model=settings.model_deployment,
            input=prompt,
        )

        return response.output_text