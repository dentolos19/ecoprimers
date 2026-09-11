FROM python:3.13-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

FROM python:3.13-slim

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

COPY alembic.ini ./
COPY migrations ./migrations
COPY public ./public
COPY src ./src
COPY templates ./templates

RUN python -m compileall -q src
RUN adduser -u 5678 --disabled-password --gecos "" app && chown -R app /app
USER app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 3000

CMD ["uvicorn", "main:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "3000", "--interface", "wsgi"]
