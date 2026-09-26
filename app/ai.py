import asyncio
from openai import OpenAI
from .config import Settings
from .storage import ConversationStore

class AIService:
    def __init__(self, settings: Settings, store: ConversationStore):
        self.settings = settings
        self.store = store
        self.client = OpenAI(api_key=settings.openai_api_key)

    async def ask(self, channel: str, user_id: str, text: str) -> str:
        self.store.add(channel, user_id, "user", text)
        history = self.store.history(channel, user_id)

        def _request() -> str:
            response = self.client.responses.create(
                model=self.settings.openai_model,
                instructions=self.settings.system_prompt,
                input=history,
            )
            return (response.output_text or "").strip()

        answer = await asyncio.to_thread(_request)
        if not answer:
            answer = "Не удалось получить ответ. Попробуйте ещё раз."
        self.store.add(channel, user_id, "assistant", answer)
        return answer
