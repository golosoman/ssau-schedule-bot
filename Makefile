POETRY_RUN = poetry run

lint:
	$(POETRY_RUN) ruff check .

format:
	$(POETRY_RUN) ruff format .

typecheck:
	$(POETRY_RUN) mypy app

test:
	$(POETRY_RUN) pytest

check:
	format typecheck test

run-bot:
	poetry run python -m app.entrypoints.bot_main

run-worker:
	poetry run python -m app.entrypoints.worker_main

db-upgrade:
	$(POETRY_RUN) alembic upgrade head

db-downgrade:
	$(POETRY_RUN) alembic downgrade -1

db-history:
	$(POETRY_RUN) alembic history

db-current:
	$(POETRY_RUN) alembic current

db-stamp-initial:
	$(POETRY_RUN) alembic stamp 20260322_0001
