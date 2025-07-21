FROM python:3.13-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Install dependencies
COPY pyproject.toml .
COPY uv.lock .
RUN uv sync --compile-bytecode

# Copy source
COPY . .

# Expose port
EXPOSE 5000

# Run application
CMD ["uv", "run", "gunicorn", "--conf", "src/gunicorn.py", "--chdir", "src", "--bind", "0.0.0.0:5000", "main:app"]