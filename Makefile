.PHONY: setup start check

setup:
	cd src/app && uv sync
	cd src/server && bun install

start:
	cd src/app && uv run main.py

check:
	cd src/app && uv run ruff format
	cd src/app && uv run ruff check --fix
