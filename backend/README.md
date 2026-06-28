# SSAU Schedule Bot

Телеграм-бот, который получает расписание из личного кабинета СНИУ (lk.ssau.ru)
и присылает напоминания за 15 минут до начала пары.

## Возможности

- Мультипользовательский режим
- Асинхронный парсинг расписания
- Кэш расписания в Valkey
- Фоновые воркеры для синка и уведомлений

## Требования

- Python 3.13+
- Poetry
- Docker + Docker Compose для продового запуска и локального Valkey

## Настройка

1. Установить зависимости:

```
poetry install
```
 
2. Создать env-файлы.

   Профиль выбирается переменной окружения `ENV` (по умолчанию `local`). Загружаются
   ровно три файла в порядке `sensitive.env → common.env → <ENV>.env`, где значения из
   более поздних файлов перекрывают более ранние. То есть на локальной машине
   (`ENV=local`) подхватываются `sensitive.env`, `common.env` и `local.env`, а
   `dev.env`/`prod.env` — только при `ENV=dev`/`ENV=prod`. Секреты (`TELEGRAM__BOT_TOKEN`,
   `SECURITY__FERNET_KEY`, `SECURITY__STATE_TOKEN_SECRET`, `API__ADMIN_API_TOKEN`) хранятся
   как `SecretStr` и не попадают в логи.

`envs/common.env`:

```env
SSAU__BASE_URL=https://lk.ssau.ru

NOTIFICATIONS__DEFAULT_TIMEZONE=Europe/Samara
NOTIFICATIONS__LEAD_MINUTES=15

WORKERS__SCHEDULE_FETCH_INTERVAL_HOURS=12
WORKERS__NOTIFICATION_POLL_INTERVAL_SECONDS=60
```

`envs/local.env` (опционально):

```env
# Отдельная локальная БД.
DATABASE__URL=sqlite+aiosqlite:///./data/ssau_schedule_bot.local.db

# Valkey локально доступен через порт, проброшенный docker compose.
VALKEY__HOST=127.0.0.1
VALKEY__PORT=6379
VALKEY__DB=0

LOGGING__LEVEL=DEBUG
LOGGING__FORMAT=text

METRICS__ENABLED=true
METRICS__HOST=0.0.0.0
METRICS__PORT=3103
TELEGRAM__METRICS_PORT=3101
WORKERS__METRICS_PORT=3102

API__HOST=0.0.0.0
API__PORT=3100
API__METRICS_PORT=3103

TELEMETRY__ENABLED=false
ALERTS__ENABLED=false

# Без Fernet-ключа разрешаем plaintext-шифр паролей только локально.
SECURITY__ALLOW_PLAINTEXT=true

# TELEGRAM__PROXY_URL=http://127.0.0.1:7890
```

`envs/dev.env` (опционально):

```env
SECURITY__ALLOW_PLAINTEXT=true

# WORKERS__NOTIFICATION_POLL_INTERVAL_SECONDS=30
```

`envs/prod.env`:

```env
# В Docker VALKEY__HOST=valkey задаёт docker-compose.yaml.
VALKEY__PORT=6379
VALKEY__DB=0

# Продовая SQLite-БД внутри volume ./data:/app/data.
DATABASE__URL=sqlite+aiosqlite:///./data/ssau_schedule_bot.prod.db

# DATABASE__URL=postgresql+asyncpg://user:pass@host:5432/ssau_schedule_bot

LOGGING__LEVEL=INFO
LOGGING__FORMAT=json

METRICS__ENABLED=true
METRICS__HOST=0.0.0.0
METRICS__PORT=3103
TELEGRAM__METRICS_PORT=3101
WORKERS__METRICS_PORT=3102

API__HOST=0.0.0.0
API__PORT=3100
API__METRICS_PORT=3103
API__CORS_ORIGINS=["https://auth.sasau.ru:8444"]

TELEGRAM__FRONTEND_AUTH_URL=https://auth.sasau.ru:8444/auth

TELEMETRY__ENABLED=false
ALERTS__ENABLED=false
```

`envs/sensitive.env` (в `.gitignore`):

```env
TELEGRAM__BOT_TOKEN=123456789:replace_me
SECURITY__FERNET_KEY=replace_me_generated_fernet_key
SECURITY__STATE_TOKEN_SECRET=replace_me_random_state_secret
API__ADMIN_API_TOKEN=replace_me_random_admin_token

# Если Telegram доступен только через прокси:
# TELEGRAM__PROXY_URL=http://127.0.0.1:7890
```

Что класть в `sensitive.env`:

- `TELEGRAM__BOT_TOKEN` — токен бота из BotFather. Без него бот не стартует.
- `SECURITY__FERNET_KEY` — ключ шифрования логина/пароля в БД. В `prod` обязателен.
- `SECURITY__STATE_TOKEN_SECRET` — секрет подписи ссылок `/auth?token=...` для web-авторизации.
- `API__ADMIN_API_TOKEN` — токен для админских REST-ручек и отправки сообщений через Swagger
  (`X-API-TOKEN`). Если его не задать, админские ручки будут отклонять запросы.
- `TELEGRAM__PROXY_URL` — опционально, только если нужен прокси до Telegram.

Ключи можно сгенерировать командами:

```
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Группа и учебный год подтягиваются автоматически из API после `/auth`.
Если раньше использовали `envs/.env`, перенесите секреты в `envs/sensitive.env`.
На сервере этот файл нужно создать или скопировать вручную, потому что он не хранится в git:

```bash
sudo install -d -m 700 /opt/apps/ssau-schedule-bot/backend/envs
sudo nano /opt/apps/ssau-schedule-bot/backend/envs/sensitive.env
sudo chmod 600 /opt/apps/ssau-schedule-bot/backend/envs/sensitive.env
```

3. Применить миграции БД:

```
poetry run alembic upgrade head
```

При необходимости можно переопределить URL для миграций:

```env
ALEMBIC_DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/ssau_schedule_bot
```

## Запуск

Запускать бот и воркеры нужно в разных терминалах:

```
poetry run python -m app.entrypoints.bot_main
```

```
poetry run python -m app.entrypoints.worker_main
```

Воркеры используют APScheduler, интервалы задаются в `WORKERS__SCHEDULE_FETCH_INTERVAL_HOURS` и
`WORKERS__NOTIFICATION_POLL_INTERVAL_SECONDS`.

Для запуска FastAPI (пробы и внутренние эндпоинты):

```
poetry run python -m app.entrypoints.api_main
```

Health endpoints: `GET /healthz`, `GET /readyz`. Воркеры запускаются отдельным процессом.

### Docker / production

В `docker-compose.yaml` сервисы `bot`, `worker` и `api` берут `ENV` из окружения.
Для production запускайте compose с `ENV=prod`; тогда сервисы читают
`envs/sensitive.env`, `envs/common.env` и `envs/prod.env`.

Запуск/пересборка:

```bash
ENV=prod docker compose up -d --build
ENV=prod docker compose ps
```

После изменения env-файлов пересоздайте процессы приложения, иначе старые контейнеры
не увидят новые значения:

```bash
ENV=prod docker compose up -d --force-recreate bot worker api
```

Swagger UI:

```text
https://auth.sasau.ru:8444/api/docs
http://<server-ip>:3100/docs
```

Если API нужен снаружи сервера, откройте порт:

```bash
sudo ufw allow 3100/tcp comment 'ssau-schedule-bot api swagger'
```

Логи:

```bash
docker compose logs -f --tail=200 bot
docker compose logs -f --tail=200 worker
docker compose logs -f --tail=200 api
```

Проверка Valkey из контейнера бота:

```bash
docker compose exec -T bot python - <<'PY'
import asyncio
from app.settings.config import settings
from valkey.asyncio import Valkey

async def main():
    client = Valkey(host=settings.valkey.host, port=settings.valkey.port, db=settings.valkey.db)
    try:
        print(settings.valkey.host)
        print(await client.ping())
    finally:
        await client.aclose()

asyncio.run(main())
PY
```

## Миграции

- История: `poetry run alembic history`
- Текущая ревизия: `poetry run alembic current`
- Применить все: `poetry run alembic upgrade head`
- Откатить на 1 шаг: `poetry run alembic downgrade -1`
- Если БД уже существует в "старом" состоянии (таблицы есть, но без `notification_type`):
  `poetry run alembic stamp 20260322_0001 && poetry run alembic upgrade head`

## Команды бота

- /start - регистрация
- /help - справка
- /auth - получить ссылку для входа через СНИУ
- /subgroup 1|2 - выбрать подгруппу
- /notify on|off - включить/выключить уведомления
- /status - показать настройки
- /schedule - расписание на сегодня
- /tomorrow - расписание на завтра
- /next - ближайшая пара
- /notify_test - тестовое уведомление
- /sync - принудительно обновить расписание

## Хранилище

- SQLite локально: `data/ssau_schedule_bot.local.db`
- SQLite в Docker/production: `data/ssau_schedule_bot.prod.db`
- Кэш расписания хранится в Valkey и может быть пересоздан из API личного кабинета.

## Архитектура

- `app/api` - входной слой (Telegram, jobs, REST)
- `app/app_layer` - use cases, интерфейсы портов, application services
- `app/domain` - сущности, value objects, доменные сервисы
- `app/infra` - клиенты, БД, репозитории, UoW
- `app/entrypoints` - точки входа
- `app/logging` - логирование
- `app/settings` - настройки

Для быстрого онбординга см. `README_DEV.md`.

## Наблюдаемость

- Логи по умолчанию в JSON, `LOGGING__FORMAT=text` переключит на текст.
- Метрики Prometheus: `METRICS__ENABLED=true`.
- Порты процессов: API HTTP `3100`, bot metrics `3101`, worker metrics `3102`,
  API metrics `3103`.
- Трейсинг OpenTelemetry: `TELEMETRY__ENABLED=true`, `TELEMETRY__OTLP_ENDPOINT=...`.
- Алерты воркера в Telegram: `ALERTS__ENABLED=true`, `ALERTS__ADMIN_CHAT_ID=...`.

## Примечания

- Логин/пароль шифруются в SQLite (Fernet). Нужен `SECURITY__FERNET_KEY`.
- Если бот и воркер запущены одновременно, для метрик используйте разные порты
  или отключите метрики в одном процессе.
- Если в Docker в логах есть `connecting to 127.0.0.1:6379`, проверьте, что сервисы
  запущены через `docker-compose.yaml`, где задаётся `VALKEY__HOST=valkey`, и пересоздайте
  контейнеры.
- Если доступ к Telegram API ограничен, используйте `TELEGRAM__PROXY_URL`.
