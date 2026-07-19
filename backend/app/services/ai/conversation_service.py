from app.prompts.chat_prompt import CHAT_SYSTEM_PROMPT


class ConversationService:
    def __init__(self):
        self.messages = [
            {
                "role": "system",
                "content": CHAT_SYSTEM_PROMPT
            }
        ]

    def add_user_message(self, message: str):
        self.messages.append(
            {
                "role": "user",
                "content": message
            }
        )

    def add_assistant_message(self, message: str):
        self.messages.append(
            {
                "role": "assistant",
                "content": message
            }
        )

    def get_messages(self):
        return self.messages

    def clear(self):
        self.messages = [
            {
                "role": "system",
                "content": CHAT_SYSTEM_PROMPT
            }
        ]