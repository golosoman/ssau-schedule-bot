POETRY_RUN = poetry run

# Среда по умолчанию — local. Переопределяется: `make run-bot ENV=prod`
# или `ENV=prod make run-bot`. Экспортируется в дочерние процессы — python
# читает её как os.getenv("ENV"), а порядок env-файлов собирает settings:
#   envs/sensitive.env -> envs/common.env -> envs/$(ENV).env
ENV ?= local
export ENV

.PHONY: lint format format-check typecheck test check \
	run-bot run-worker run-api \
	db-upgrade db-downgrade db-history db-current db-stamp-initial \
	up down logs ps \
	create-environment delete-environment recreate-environment

lint:
	$(POETRY_RUN) ruff check .

format:
	$(POETRY_RUN) ruff format .

format-check:
	$(POETRY_RUN) ruff format --check .

typecheck:
	$(POETRY_RUN) mypy app

test:
	$(POETRY_RUN) pytest

# Green verification gate: lint + typecheck + tests, all non-mutating.
# (`format` is excluded because it rewrites files; run it explicitly.)
check: lint typecheck test

run-bot:
	$(POETRY_RUN) python -m app.entrypoints.bot_main

run-worker:
	$(POETRY_RUN) python -m app.entrypoints.worker_main

run-api:
	$(POETRY_RUN) python -m app.entrypoints.api_main

db-upgrade:
	$(POETRY_RUN) alembic upgrade head

db-downgrade:
	$(POETRY_RUN) alembic downgrade -1

db-history:
	$(POETRY_RUN) alembic history

db-current:
	$(POETRY_RUN) alembic current

db-stamp-initial:
	$(POETRY_RUN) alembic stamp 20260601_0001

# --- docker-стек (ENV прокидывается в контейнеры) ---
# ENV выбирает env-файл внутри контейнеров: `make up ENV=dev` поднимет стек
# на dev-конфиге. По умолчанию ENV=local (см. начало файла). VALKEY__HOST
# внутри docker форсится на `valkey` (см. docker-compose.yaml).

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f

ps:
	docker compose ps

# --- окружение целиком ---

# Полностью поднять окружение: миграции (по ENV) + весь docker-стек
# (valkey + bot + worker + api). Миграции прогоняются до старта сервисов.
create-environment:
	$(POETRY_RUN) alembic upgrade head
	docker compose up -d --build

# Полностью снести окружение: контейнеры + тома + SQLite-БД ТЕКУЩЕГО ENV
# (путь берётся из settings.database.url, только для sqlite).
delete-environment:
	docker compose down -v
	$(POETRY_RUN) python -c "from app.settings.config import settings; from sqlalchemy.engine import make_url; from pathlib import Path; u = make_url(settings.database.url); p = Path(u.database) if u.get_backend_name() == 'sqlite' and u.database else None; p and p.exists() and p.unlink()"

# Пересоздать окружение с нуля.
recreate-environment: delete-environment create-environment
