set dotenv-load
set dotenv-filename := dotenv_file
set dotenv-override

environment := ""
dotenv_file := if environment == "" { ".env" } else { ".env." + environment }

setup mode="": install compose
    just --no-deps environment={{ quote(environment) }} migrate
    if [ "{{ mode }}" != "prerun" ]; then just decompose; fi

install:
    bun install --frozen-lockfile
    uv sync --frozen

start: compose
    #!/usr/bin/env bash
    set -euo pipefail
    bun run build:client
    bun run build:client --watch &
    watcher_pid=$!
    trap 'kill "$watcher_pid" 2>/dev/null || true; wait "$watcher_pid" 2>/dev/null || true' EXIT
    uv run --env-file {{ quote(dotenv_file) }} flask --app src/main.py run --host localhost --port 3000 --debug

compose:
    if [ "${CI:-false}" != "true" ]; then docker compose up --detach --wait; fi

decompose:
    if [ "${CI:-false}" != "true" ]; then docker compose down; fi

build:
    bun run build:client
    uv run pywrangler sync
    uv run python scripts/patch_pillow.py

check:
    bun lint --fix && bun fmt && bun check --no-script
    uv run ruff check --fix && uv run ruff format && uv run ty check
    PYTHONPATH=src uv run python -m unittest discover -s tests

migrate revision="head": compose
    uv run alembic upgrade {{ revision }}

deploy: install build
    #!/usr/bin/env bash
    set -euo pipefail
    test -f {{ quote(dotenv_file) }}
    CI=true just environment={{ quote(environment) }} migrate
    bun wrangler deploy --secrets-file {{ quote(dotenv_file) }}

seed: compose
    uv run --env-file {{ quote(dotenv_file) }} python src/seed.py
