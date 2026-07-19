from app.models.agent import AgentAction
from app.services.ai.ai_service import AIService


class RouterService:
    def __init__(self, ai_service: AIService):
        self._ai_service = ai_service

    def route(self, message: str) -> AgentAction:
        action = self._ai_service.classify(message)

        try:
            return AgentAction(action)
        except ValueError:
            return AgentAction.CHAT