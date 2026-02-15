lint:
	poetry run ruff check .

format:
	poetry run ruff format .

typecheck:
	poetry run mypy app

test:
	poetry run pytest

run:
	poetry run python -m app.entrypoints.bot_main
