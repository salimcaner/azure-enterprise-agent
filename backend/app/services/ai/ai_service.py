from openai import OpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

from app.core.config import settings
from app.services.ai.conversation_service import ConversationService


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

        self._conversation = ConversationService()

    def generate_response(self, prompt: str) -> str:
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        self._conversation.add_user_message(prompt)

        response = self._client.responses.create(
            model=settings.model_deployment,
            input=self._conversation.get_messages(),
        )

        assistant_response = response.output_text

        self._conversation.add_assistant_message(assistant_response)

        return assistant_response

    def chat(self, message: str) -> str:
        return self.generate_response(message)

    def classify(self, message: str) -> str:
        prompt = f"""
You are an AI router.

Choose exactly one action.

Available actions:
- rag -> if the user asks about company documents, policies, HR, leave, benefits or internal information.
- chat -> for general conversation.

Reply with only one word:
rag
or
chat

User:
{message}
"""

        response = self._client.chat.completions.create(
            model=settings.model_deployment,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        return response.choices[0].message.content.strip().lower()
