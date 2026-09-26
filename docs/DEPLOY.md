# Deploy на SysSerJarvis

## 1. DNS

Создайте A-запись:

```
ai.example.com -> 66.151.32.64
```

## 2. Клонирование

```bash
cd ~/docker
git clone https://github.com/tel79222960001/jarvis-assistant.git
cd jarvis-assistant
cp .env.example .env
nano .env
```

Заполните секреты только на сервере. Файл `.env` уже исключён из Git.

## 3. Docker

```bash
docker network inspect app-net >/dev/null 2>&1 || docker network create app-net
docker compose up -d --build
docker compose ps
```

## 4. Caddy

Добавьте в рабочий Caddyfile:

```caddy
ai.example.com {
    reverse_proxy jarvis-assistant:8000
}
```

Перезагрузите конфигурацию Caddy:

```bash
cd ~/docker/caddy
docker compose exec caddy caddy validate --config /etc/caddy/Caddyfile
docker compose exec caddy caddy reload --config /etc/caddy/Caddyfile
```

Проверка:

```bash
curl https://ai.example.com/health
```

## 5. Telegram

После заполнения `.env` загрузите переменные:

```bash
set -a
source .env
set +a
```

Установите webhook (подставьте значения переменных локально на сервере):

```bash
curl -sS "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook" \
  -d "url=https://ai.example.com/telegram/webhook" \
  -d "secret_token=$TELEGRAM_WEBHOOK_SECRET"
```

Проверка:

```bash
curl -sS "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getWebhookInfo"
```

## 6. Алиса

Webhook без токена:

```
https://ai.example.com/alice
```

Если задан `ALICE_WEBHOOK_TOKEN`, используйте:

```
https://ai.example.com/alice/ВАШ_ТОКЕН
```

## 7. Обновление

```bash
cd ~/docker/jarvis-assistant
git pull
docker compose up -d --build
```

## 8. Логи

```bash
docker compose logs -f --tail=200
```