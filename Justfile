setup:
    bun install
    uv sync
    just compose
    just migrate
    just seed

start: compose
    bun run dev && wait
    just decompose

compose:
    docker compose up --detach --wait database storage
    docker compose run --rm storage-setup

decompose:
    docker compose down

check:
    bun run check
    uv run ruff check --fix && uv run ruff format && uv run ty check

migrate:
    uv run alembic upgrade head

seed:
    uv run python src/seed.py
