# Jarvis Assistant

Единый AI-шлюз для:
- Telegram-бота
- навыка Алисы
- OpenAI API

## Архитектура

Telegram / Alice -> Caddy HTTPS -> FastAPI -> OpenAI Responses API

Приложение запускается в Docker и подключается к внешней сети `app-net`.

## Быстрый старт

1. Скопируйте `.env.example` в `.env`.
2. Заполните секреты локально на сервере.
3. Создайте сеть (один раз):

```bash
docker network create app-net
```

4. Запустите:

```bash
docker compose up -d --build
```

5. Проверка:

```bash
curl http://127.0.0.1:8000/health
```

## Безопасность

Никогда не коммитьте `.env`, API-ключи OpenAI и токен Telegram-бота.

## Webhook-и

- Telegram: `https://<ваш-домен>/telegram/webhook`
- Алиса: `https://<ваш-домен>/alice`

Подробности настройки находятся в `docs/DEPLOY.md`.
