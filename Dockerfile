FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

RUN apt-get update && \
  apt-get install --no-install-recommends -y build-essential libpq-dev libfreetype6-dev libpng-dev && \
  rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY uv.lock .
RUN uv sync --frozen --compile-bytecode

COPY . .

ENV FLASK_APP=src/main.py
ENV FLASK_DEBUG=0
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["uv", "run", "gunicorn", "--conf", "src/gunicorn.py", "--chdir", "src", "--bind", "0.0.0.0:5000", "main:app"]
