.PHONY: setup start check

setup:
	uv sync

start:
	uv run main.py

check:
	uv run ruff format
	uv run ruff check --fix
