from app.services.ai.ai_service import AIService


class ChatTool:
    name = "chat"

    def __init__(self, ai_service: AIService):
        self._ai_service = ai_service

    def execute(self, message: str) -> str:
        return self._ai_service.chat(message)
