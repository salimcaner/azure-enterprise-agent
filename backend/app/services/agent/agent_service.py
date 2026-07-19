from app.models.agent import AgentAction
from app.services.ai.ai_service import AIService
from app.services.agent.router_service import RouterService
from app.services.tools.base_tool import BaseTool
from app.services.tools.chat_tool import ChatTool
from app.services.tools.rag_tool import RagTool


class AgentService:
    def __init__(self):
        ai_service = AIService()

        self._router_service = RouterService(ai_service)
        self._tool_registry: dict[AgentAction, BaseTool] = {
            AgentAction.CHAT: ChatTool(ai_service),
            AgentAction.RAG: RagTool(ai_service),
        }

    def chat(self, message: str) -> str:
        action = self._router_service.route(message)
        tool = self._tool_registry.get(action, self._tool_registry[AgentAction.CHAT])

        return tool.execute(message)
