from typing import Any
import httpx
from fastapi import HTTPException, Request
from .ai import AIService
from .config import Settings
from .storage import ConversationStore

class TelegramService:
    def __init__(self, settings: Settings, ai: AIService, store: ConversationStore):
        self.settings = settings
        self.ai = ai
        self.store = store

    async def handle(self, request: Request, payload: dict[str, Any]) -> dict:
        if self.settings.telegram_webhook_secret:
            supplied = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
            if supplied != self.settings.telegram_webhook_secret:
                raise HTTPException(status_code=403, detail="Invalid Telegram webhook secret")

        message = payload.get("message") or payload.get("edited_message")
        if not message:
            return {"ok": True}

        chat = message.get("chat") or {}
        sender = message.get("from") or {}
        chat_id = chat.get("id")
        user_id = sender.get("id")
        text = (message.get("text") or "").strip()
        if not chat_id or not user_id or not text:
            return {"ok": True}

        allowed = self.settings.telegram_allowed_ids
        if allowed and int(user_id) not in allowed:
            await self.send_message(chat_id, "Доступ к этому боту закрыт.")
            return {"ok": True}

        key = str(user_id)
        if text.startswith("/start"):
            answer = "Jarvis подключён. Напишите вопрос.\n/new — новый диалог\n/help — помощь"
        elif text.startswith("/new"):
            self.store.clear("telegram", key)
            answer = "Контекст очищен. Начинаем новый диалог."
        elif text.startswith("/help"):
            answer = "Отправьте текстовый вопрос. Команда /new очищает историю диалога."
        else:
            answer = await self.ai.ask("telegram", key, text)

        await self.send_message(chat_id, answer)
        return {"ok": True}

    async def send_message(self, chat_id: int, text: str):
        if not self.settings.telegram_bot_token:
            raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured")
        url = f"https://api.telegram.org/bot{self.settings.telegram_bot_token}/sendMessage"
        chunks = [text[i:i+4000] for i in range(0, len(text), 4000)] or [""]
        async with httpx.AsyncClient(timeout=15) as client:
            for chunk in chunks:
                response = await client.post(url, json={
                    "chat_id": chat_id,
                    "text": chunk,
                    "disable_web_page_preview": True,
                })
                response.raise_for_status()
