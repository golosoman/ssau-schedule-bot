# SSAU Schedule Bot - README для разработчика

## Быстрый обзор

Проект следует Clean Architecture + DDD. Зависимости направлены внутрь: domain -> app_layer -> api/infra.

## Структура каталогов

- `app/api` - входной слой: Telegram handlers, REST, jobs (APScheduler)
- `app/app_layer` - use cases, порты/интерфейсы, application services (schedule/notifications/users)
- `app/domain` - сущности, value objects, доменные сервисы, события
- `app/infra` - реализации портов: HTTP-клиенты, БД, репозитории, UoW, security
- `app/entrypoints` - точки запуска процессов (bot/worker/api)
- `app/di` - DI контейнер и композиция зависимостей
- `app/logging` - конфигурация логирования
- `app/settings` - pydantic settings и загрузка env

## Потоки выполнения

### Telegram команда
1) Handler в `app/api/events/telegram/handlers/*`
2) Use case в `app/app_layer/use_cases/*`
3) UoW + репозитории (`app/app_layer/interfaces/uow`, `app/infra/uow`, `app/infra/repos`)
4) Доменные модели и value objects (`app/domain/*`)

### Jobs (APScheduler)
- Планировщик: `app/api/jobs/scheduler.py`
- Джобы: `app/api/jobs/*/job.py`
- Используют те же use cases/services через DI

### REST
- FastAPI фабрика: `app/api/rest/app.py`
- Роутеры: `app/api/rest/routers/*`

## Где добавлять изменения

- Новый бизнес-сценарий: `app/app_layer/use_cases`
- Новый доменный объект/инвариант: `app/domain`
- Новый порт/интерфейс: `app/app_layer/interfaces`
- Реализация порта (HTTP/DB/Queue): `app/infra`
- Новый вход (бот/REST/job): `app/api`

## DI и wiring

- Контейнер: `app/di/container.py`
- Wiring делается в entrypoints (bot/worker) через `container.wire(...)`
- В обработчиках используется `@inject` + `Provide[Container.*]`

## Тесты

- Юнит: `tests/unit`
- Интеграционные (SQLite): `tests/integration`

## Окружения и настройки

- `ENV=local` используется по умолчанию.
- Settings читают файлы в порядке `envs/sensitive.env -> envs/common.env -> envs/<ENV>.env`.
- Локальная SQLite-БД: `data/ssau_schedule_bot.db`.
- Production SQLite-БД в Docker: `data/ssau_schedule_bot.prod.db`.
- `local.env` и `dev.env` разрешают `SECURITY__ALLOW_PLAINTEXT=true`, но в `prod` нужен `SECURITY__FERNET_KEY`.
- `common.env` задаёт `VALKEY__HOST=127.0.0.1` для локального запуска.
- `prod.env` обязан задавать `VALKEY__HOST=valkey`, потому что внутри Docker `127.0.0.1` указывает на сам контейнер приложения.

## Локальный запуск

Поднять Valkey для локальных процессов:

```bash
docker compose up -d valkey
```

Применить миграции и запустить процессы:

```bash
make db-upgrade
make run-bot
make run-worker
make run-api
```

API локально:

```text
http://127.0.0.1:3100/docs
```

Если нужно запустить приложение полностью в Docker, используется `ENV=prod` из
`docker-compose.yaml`:

```bash
docker compose up -d --build
docker compose ps
```

После изменения env-файлов пересоздайте контейнеры приложения:

```bash
docker compose up -d --force-recreate bot worker api
```

## Полезные команды

```bash
make check
make format
poetry run pytest
poetry run ruff check .
poetry run mypy app
poetry run alembic upgrade head
poetry run alembic downgrade -1
poetry run alembic stamp 20260601_0001
```

## Диагностика

Логи Docker-сервисов:

```bash
docker compose logs -f --tail=200 bot
docker compose logs -f --tail=200 worker
docker compose logs -f --tail=200 api
docker compose logs -f --tail=200 valkey
```

Проверить, какие настройки реально видит контейнер:

```bash
docker compose exec -T bot python - <<'PY'
from app.settings.config import settings

print("env valkey host:", settings.valkey.host)
print("db url:", settings.database.url)
PY
```

Проверить соединение с Valkey из контейнера:

```bash
docker compose exec -T bot python - <<'PY'
import asyncio
from app.settings.config import settings
from valkey.asyncio import Valkey

async def main():
    client = Valkey(host=settings.valkey.host, port=settings.valkey.port, db=settings.valkey.db)
    try:
        print(await client.ping())
    finally:
        await client.aclose()

asyncio.run(main())
PY
```

Если в логах есть `connecting to 127.0.0.1:6379`, значит Docker-процесс не получил
`VALKEY__HOST=valkey`. Проверьте `envs/prod.env` и пересоздайте `bot`, `worker`, `api`.

Swagger с сервера доступен на `http://<server-ip>:3100/docs`, если порт открыт:

```bash
sudo ufw allow 3100/tcp comment 'ssau-schedule-bot api swagger'
```

## Jenkins (миграции вручную)

- Параметр `PIPELINE_JOB`:
  - `deploy`
  - `db-history`
  - `db-current`
  - `db-upgrade-head`
  - `db-downgrade-1`
  - `db-stamp-initial`
- `DB_MIGRATION_SERVICE`: сервис `docker-compose` для запуска миграций (`worker`/`bot`).
- `DB_STAMP_REVISION`: ревизия для `db-stamp-initial`.
- Для изменяющих действий (`upgrade/downgrade/stamp`) в Jenkins добавлено ручное `input`-подтверждение.
- В migration-режимах Jenkins перед запуском команды делает `docker compose build` выбранного сервиса.
