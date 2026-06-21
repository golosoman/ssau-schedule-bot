# SSAU Schedule Bot

Телеграм-бот, который получает расписание из личного кабинета СГАУ (lk.ssau.ru)
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
   `SECURITY__FERNET_KEY`) хранятся как `SecretStr` и не попадают в логи.

`envs/common.env`:

```env
SSAU__BASE_URL=https://lk.ssau.ru

DATABASE__URL=sqlite+aiosqlite:///./data/ssau_schedule_bot.db

NOTIFICATIONS__DEFAULT_TIMEZONE=Europe/Samara
NOTIFICATIONS__LEAD_MINUTES=15

WORKERS__SCHEDULE_FETCH_INTERVAL_HOURS=12
WORKERS__NOTIFICATION_POLL_INTERVAL_SECONDS=60

# Valkey (кэш расписания). Локально используется host 127.0.0.1.
# В Docker/ENV=prod это значение обязательно переопределяется в prod.env.
VALKEY__HOST=127.0.0.1
VALKEY__PORT=6379
VALKEY__DB=0
# VALKEY__PASSWORD=changeme

LOGGING__LEVEL=INFO
LOGGING__FORMAT=json

METRICS__ENABLED=true
METRICS__HOST=0.0.0.0
# Process ports:
# API HTTP       -> 3100
# bot metrics    -> 3101
# worker metrics -> 3102
# API metrics    -> 3103
METRICS__PORT=3103
TELEGRAM__METRICS_PORT=3101
WORKERS__METRICS_PORT=3102

API__HOST=0.0.0.0
API__PORT=3100
API__METRICS_PORT=3103

# TELEMETRY__ENABLED=false
# TELEMETRY__OTLP_ENDPOINT=http://localhost:4318/v1/traces
# TELEMETRY__SERVICE_NAME=ssau-schedule-bot

# ALERTS__ENABLED=false
# ALERTS__ADMIN_CHAT_ID=123456789
```

`envs/local.env` (опционально):

```env
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
# В Docker Valkey доступен по имени сервиса, а не через 127.0.0.1.
VALKEY__HOST=valkey

# Продовая SQLite-БД внутри volume ./data:/app/data.
DATABASE__URL=sqlite+aiosqlite:///./data/ssau_schedule_bot.prod.db

# DATABASE__URL=postgresql+asyncpg://user:pass@host:5432/ssau_schedule_bot
```

`envs/sensitive.env` (в `.gitignore`):

```env
TELEGRAM__BOT_TOKEN=your_bot_token
SECURITY__FERNET_KEY=your_fernet_key
# API__ADMIN_API_TOKEN=your_admin_api_token
```

Ключ Fernet можно сгенерировать командой:

```
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Группа и учебный год подтягиваются автоматически из API после `/auth`.
Если раньше использовали `envs/.env`, перенесите секреты в `envs/sensitive.env`.

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

В `docker-compose.yaml` сервисы `bot`, `worker` и `api` запускаются с `ENV=prod`.
Они читают `envs/sensitive.env`, `envs/common.env` и `envs/prod.env`.

Запуск/пересборка:

```bash
docker compose up -d --build
docker compose ps
```

После изменения env-файлов пересоздайте процессы приложения, иначе старые контейнеры
не увидят новые значения:

```bash
docker compose up -d --force-recreate bot worker api
```

Swagger UI:

```text
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
- /auth LOGIN PASSWORD - сохранить доступ
- /subgroup 1|2 - выбрать подгруппу
- /notify on|off - включить/выключить уведомления
- /status - показать настройки
- /schedule - расписание на сегодня
- /tomorrow - расписание на завтра
- /next - ближайшая пара
- /notify_test - тестовое уведомление
- /sync - принудительно обновить расписание

## Хранилище

- SQLite локально: `data/ssau_schedule_bot.db`
- SQLite в Docker/production: `data/ssau_schedule_bot.prod.db`
- Кэш расписания хранится в Valkey и может быть пересоздан из SSAU API.

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
- Если в Docker в логах есть `connecting to 127.0.0.1:6379`, проверьте, что
  в `envs/prod.env` задано `VALKEY__HOST=valkey`, и пересоздайте контейнеры.
- Если доступ к Telegram API ограничен, используйте `TELEGRAM__PROXY_URL`.
