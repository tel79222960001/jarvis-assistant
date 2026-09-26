from typing import Any
from fastapi import HTTPException
from .ai import AIService
from .config import Settings
from .storage import ConversationStore

class AliceService:
    def __init__(self, settings: Settings, ai: AIService, store: ConversationStore):
        self.settings = settings
        self.ai = ai
        self.store = store

    async def handle(self, payload: dict[str, Any], token: str = "") -> dict:
        expected = self.settings.alice_webhook_token
        if expected and token != expected:
            raise HTTPException(status_code=403, detail="Invalid Alice webhook token")

        request = payload.get("request") or {}
        session = payload.get("session") or {}
        text = (request.get("original_utterance") or request.get("command") or "").strip()
        user_id = (
            (session.get("user") or {}).get("user_id")
            or (session.get("application") or {}).get("application_id")
            or session.get("session_id")
            or "anonymous"
        )
        key = str(user_id)

        if not text:
            answer = "Здравствуйте. Я Jarvis. Задайте вопрос."
        elif text.lower() in {"новый диалог", "очисти диалог", "сбрось контекст"}:
            self.store.clear("alice", key)
            answer = "Контекст очищен. Начинаем новый диалог."
        else:
            answer = await self.ai.ask("alice", key, text)

        answer = answer[:950]
        return {
            "response": {"text": answer, "tts": answer, "end_session": False},
            "version": payload.get("version", "1.0"),
        }
