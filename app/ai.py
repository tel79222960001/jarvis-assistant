import asyncio
import logging

from openai import (
    APIConnectionError,
    APIStatusError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)

from .config import Settings
from .storage import ConversationStore

logger = logging.getLogger("jarvis.ai")


class AIService:
    def __init__(self, settings: Settings, store: ConversationStore):
        self.settings = settings
        self.store = store
        self.last_models: dict[tuple[str, str], str] = {}

        if not settings.ai_api_key:
            raise RuntimeError("AI API key is not configured")

        self.client = OpenAI(
            api_key=settings.ai_api_key,
            base_url=settings.ai_base_url,
            default_headers={
                "HTTP-Referer": "https://jarvis.66-151-32-64.sslip.io",
                "X-Title": "Jarvis Assistant",
            },
        )

    def get_last_model(self, channel: str, user_id: str) -> str | None:
        return self.last_models.get((channel, user_id))

    async def ask(self, channel: str, user_id: str, text: str) -> str:
        self.store.add(channel, user_id, "user", text)
        history = self.store.history(channel, user_id)

        def _request():
            return self.client.responses.create(
                model=self.settings.selected_model,
                instructions=self.settings.system_prompt,
                input=history,
            )

        try:
            response = await asyncio.to_thread(_request)
            model_name = getattr(response, "model", None)
            if model_name:
                self.last_models[(channel, user_id)] = model_name

            answer = (response.output_text or "").strip()
            if not answer:
                answer = "Не удалось получить ответ. Попробуйте ещё раз."

            self.store.add(channel, user_id, "assistant", answer)
            return answer

        except AuthenticationError:
            logger.exception("AI authentication failed")
            return "Ошибка авторизации AI-провайдера. Проверьте API-ключ на сервере."
        except RateLimitError:
            logger.exception("AI rate limit or quota exceeded")
            return "AI временно недоступен из-за лимита запросов. Попробуйте немного позже."
        except APIConnectionError:
            logger.exception("AI connection error")
            return "Не удалось связаться с AI-провайдером. Попробуйте ещё раз через минуту."
        except APIStatusError as exc:
            logger.exception("AI provider returned HTTP %s", exc.status_code)
            return f"AI-провайдер вернул ошибку {exc.status_code}. Попробуйте позже."
        except Exception:
            logger.exception("Unexpected AI error")
            return "Произошла внутренняя ошибка Jarvis. Попробуйте ещё раз."
