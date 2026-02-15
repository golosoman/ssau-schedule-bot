lint:
	poetry run ruff check .

format:
	poetry run ruff format .

typecheck:
	poetry run mypy src

test:
	poetry run pytest

run:
	poetry run python -m ssau_schedule_bot.main
