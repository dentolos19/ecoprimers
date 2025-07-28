FROM python:3.13-slim

# Install system dependencies
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Install project dependencies
COPY pyproject.toml .
COPY uv.lock .
RUN uv sync --compile-bytecode

# Copy source
COPY . .

# Set environment variables
ENV FLASK_APP=src/main.py
ENV FLASK_DEBUG=0

# Expose port
EXPOSE 5000

# Run application
CMD ["uv", "run", "gunicorn", "--conf", "src/gunicorn.py", "--chdir", "src", "--bind", "0.0.0.0:5000", "main:app"]