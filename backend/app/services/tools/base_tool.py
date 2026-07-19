from typing import Protocol


class BaseTool(Protocol):
    name: str

    def execute(self, message: str) -> str:
        """Run the tool for the given user message."""
