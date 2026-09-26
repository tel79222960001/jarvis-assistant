from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # AI provider. OpenRouter is the default for this project.
    openrouter_api_key: str = ""
    ai_base_url: str = "https://openrouter.ai/api/v1"
    ai_model: str = "openrouter/free"

    # Backward-compatible OpenAI variables, if you want to switch providers later.
    openai_api_key: str = ""
    openai_model: str = ""

    system_prompt: str = "Ты Jarvis, полезный голосовой и текстовый ассистент. Отвечай по-русски, кратко и по делу."
    telegram_bot_token: str = ""
    telegram_webhook_secret: str = ""
    telegram_allowed_user_ids: str = ""
    alice_webhook_token: str = ""
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    database_path: str = "/app/data/jarvis.db"
    max_history_messages: int = 12
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def ai_api_key(self) -> str:
        return self.openrouter_api_key or self.openai_api_key

    @property
    def selected_model(self) -> str:
        return self.ai_model or self.openai_model or "openrouter/free"

    @property
    def telegram_allowed_ids(self) -> set[int]:
        if not self.telegram_allowed_user_ids.strip():
            return set()
        return {int(x.strip()) for x in self.telegram_allowed_user_ids.split(",") if x.strip()}

@lru_cache
def get_settings() -> Settings:
    return Settings()
