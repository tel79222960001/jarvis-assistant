# Jarvis Assistant

Единый AI-шлюз для:
- Telegram-бота
- навыка Алисы
- OpenRouter / OpenAI-compatible API

## Архитектура

Telegram / Alice -> Caddy HTTPS -> FastAPI -> OpenRouter -> AI model

По умолчанию используется `openrouter/free` — бесплатный роутер OpenRouter.

## Быстрый старт

1. Скопируйте `.env.example` в `.env`.
2. Заполните `OPENROUTER_API_KEY` и секреты Telegram/Alice локально на сервере.
3. Создайте сеть (один раз):

```bash
docker network create app-net
```

4. Запустите:

```bash
docker compose up -d --build
```

## Безопасность

Никогда не коммитьте `.env`, API-ключи и токены.

## Webhook-и

- Telegram: `https://jarvis.66-151-32-64.sslip.io/telegram/webhook`
- Алиса: `https://jarvis.66-151-32-64.sslip.io/alice/<token>`
