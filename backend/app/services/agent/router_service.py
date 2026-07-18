from app.models.agent import AgentAction
from app.services.ai.ai_service import AIService


class RouterService:
    def __init__(self):
        self._ai_service = AIService()

    def route(self, message: str) -> AgentAction:
        action = self._ai_service.classify(message)

        try:
            return AgentAction(action)
        except ValueError:
            return AgentAction.CHAT