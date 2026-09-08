.PHONY: setup start check migrate seed

setup:
	bun install
	uv sync
	$(MAKE) migrate

start:
	bun run dev

check:
	bun run check
	uv run ruff check --fix && uv run ruff format && uv run ty check

migrate:
	uv run alembic upgrade head
	uv run python src/seed.py
