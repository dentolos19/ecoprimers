set dotenv-load

setup mode="": install compose
    just --no-deps migrate
    if [ "{{ mode }}" != "prerun" ]; then just decompose; fi

install:
    bun install --frozen-lockfile
    uv sync --frozen

start: compose
    uv run --env-file .env flask --app src/main.py run --host localhost --port 3000 --debug && \
    wait

compose:
    if [ "${CI:-false}" != "true" ]; then docker compose up --detach --wait; fi

decompose:
    if [ "${CI:-false}" != "true" ]; then docker compose down; fi

build:
    uv run pywrangler sync

check:
    bun run check
    uv run ruff check --fix && uv run ruff format && uv run ty check

migrate revision="head": compose
    uv run alembic upgrade {{ revision }}

deploy: install build
    #!/usr/bin/env bash
    set -euo pipefail
    secrets=(
        AWS_ACCESS_KEY_ID
        AWS_ENDPOINT_URL_S3
        AWS_REGION
        AWS_SECRET_ACCESS_KEY
        GOOGLE_CLIENT_ID
        GOOGLE_CLIENT_SECRET
        NEWS_API_KEY
        OPENROUTER_API_KEY
        OPENROUTER_MODEL
        OPENROUTER_REFERER
        OPENROUTER_TITLE
        OPENWEATHER_API_KEY
        RESEND_API_KEY
        RESEND_FROM_EMAIL
        RESEND_FROM_NAME
        SECRET_KEY
        TURNSTILE_SECRET_KEY
        TURNSTILE_SITE_KEY
    )
    for secret in "${secrets[@]}"; do if [[ -z "${!secret:-}" ]]; then echo "Missing secret value: $secret" >&2; exit 1; fi; done
    node -e 'process.stdout.write(JSON.stringify(Object.fromEntries(process.argv.slice(1).map((name) => [name, process.env[name]]))))' "${secrets[@]}" | bun wrangler secret bulk
    bun wrangler deploy

seed: compose
    uv run --env-file .env python src/seed.py
