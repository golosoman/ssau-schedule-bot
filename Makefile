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
