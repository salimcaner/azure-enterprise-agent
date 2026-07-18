from enum import Enum


class AgentAction(str, Enum):
    RAG = "rag"
    CHAT = "chat"