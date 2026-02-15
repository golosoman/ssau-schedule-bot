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

## Полезные команды

```
poetry run pytest
poetry run ruff check .
poetry run mypy app
```
