import logging
import uvicorn
from fastapi import FastAPI, Request
from .ai import AIService
from .alice import AliceService
from .config import get_settings
from .storage import ConversationStore
from .telegram import TelegramService

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

settings = get_settings()
store = ConversationStore(settings.database_path, settings.max_history_messages)
ai = AIService(settings, store)
telegram = TelegramService(settings, ai, store)
alice = AliceService(settings, ai, store)

app = FastAPI(title="Jarvis Assistant", version="0.1.0")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "jarvis-assistant"}

@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    return await telegram.handle(request, await request.json())

@app.post("/alice")
async def alice_webhook(request: Request):
    return await alice.handle(await request.json())

@app.post("/alice/{token}")
async def alice_webhook_with_token(token: str, request: Request):
    return await alice.handle(await request.json(), token)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.app_host, port=settings.app_port, reload=False)
