set dotenv-load

setup mode="": install
    just compose
    just migrate
    if [ "{{ mode }}" != "prerun" ]; then just decompose; fi

install:
    bun install --frozen-lockfile
    uv sync --frozen

start: compose
    uv run --env-file .env flask --app src/main.py run --host localhost --port 3000 --debug && \
    wait

compose:
    docker compose up --detach --wait database storage
    docker compose run --rm storage-setup

decompose:
    docker compose down

build:
    uv run pywrangler sync

check:
    bun run check
    uv run ruff check --fix && uv run ruff format && uv run ty check

migrate revision="head":
    uv run alembic upgrade {{ revision }}

deploy: install build
    #!/usr/bin/env bash
    set -euo pipefail
    names=(
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
    for name in "${names[@]}"; do if [[ -z "${!name:-}" ]]; then echo "Missing worker secret value: $name" >&2; exit 1; fi; done
    node -e 'process.stdout.write(JSON.stringify(Object.fromEntries(process.argv.slice(1).map((name) => [name, process.env[name]]))))' "${names[@]}" | bun wrangler secret bulk
    bun wrangler deploy

seed:
    uv run --env-file .env python src/seed.py
