# SSAU Schedule Bot

Телеграм-бот, который получает расписание из личного кабинета СГАУ (lk.ssau.ru)
и присылает напоминания за 15 минут до начала пары.

## Возможности

- Мультипользовательский режим
- Асинхронный парсинг расписания
- Кэш расписания в SQLite
- Фоновые воркеры для синка и уведомлений

## Требования

- Python 3.13+
- Poetry

## Настройка

1. Установить зависимости:

```
poetry install
```

2. Создать env-файлы (загружаются по порядку, позже заданные значения перекрывают предыдущие):

`envs/common.env`:

```env
SSAU__BASE_URL=https://lk.ssau.ru

DATABASE__URL=sqlite+aiosqlite:///./data/ssau_schedule_bot.db

NOTIFICATIONS__DEFAULT_TIMEZONE=Europe/Samara
NOTIFICATIONS__LEAD_MINUTES=15

WORKERS__SCHEDULE_FETCH_INTERVAL_HOURS=12
WORKERS__NOTIFICATION_POLL_INTERVAL_SECONDS=60

LOGGING__LEVEL=INFO
LOGGING__FORMAT=json

METRICS__ENABLED=true
METRICS__HOST=0.0.0.0
METRICS__PORT=8000

API__HOST=0.0.0.0
API__PORT=8080

# TELEMETRY__ENABLED=false
# TELEMETRY__OTLP_ENDPOINT=http://localhost:4318/v1/traces
# TELEMETRY__SERVICE_NAME=ssau-schedule-bot

# ALERTS__ENABLED=false
# ALERTS__ADMIN_CHAT_ID=123456789
```

`envs/local.env` (опционально):

```env
# TELEGRAM__PROXY_URL=http://127.0.0.1:7890
```

`envs/dev.env` (опционально):

```env
# WORKERS__NOTIFICATION_POLL_INTERVAL_SECONDS=30
```

`envs/prod.env` (опционально):

```env
# DATABASE__URL=postgresql+asyncpg://user:pass@host:5432/ssau_schedule_bot
```

`envs/sensitive.env` (в `.gitignore`):

```env
TELEGRAM__BOT_TOKEN=your_bot_token
SECURITY__FERNET_KEY=your_fernet_key
# SECURITY__ALLOW_PLAINTEXT=true
```

Ключ Fernet можно сгенерировать командой:

```
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Группа и учебный год подтягиваются автоматически из API после `/auth`.
Если раньше использовали `envs/.env`, перенесите секреты в `envs/sensitive.env`.

База инициализируется автоматически при старте бота/воркера/REST.

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

- SQLite файл: `data/ssau_schedule_bot.db`

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
- Метрики Prometheus: `METRICS__ENABLED=true`, `METRICS__PORT=8000`.
- Трейсинг OpenTelemetry: `TELEMETRY__ENABLED=true`, `TELEMETRY__OTLP_ENDPOINT=...`.
- Алерты воркера в Telegram: `ALERTS__ENABLED=true`, `ALERTS__ADMIN_CHAT_ID=...`.

## Примечания

- Логин/пароль шифруются в SQLite (Fernet). Нужен `SECURITY__FERNET_KEY`.
- Если бот и воркер запущены одновременно, для метрик используйте разные порты
  или отключите метрики в одном процессе.
- Если доступ к Telegram API ограничен, используйте `TELEGRAM__PROXY_URL`.
