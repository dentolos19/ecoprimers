FROM python:3.13-slim-bookworm

# Installs uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set the working directory
WORKDIR /app

# Install dependencies
COPY pyproject.toml .
COPY uv.lock .
RUN uv sync --frozen --compile-bytecode

# Copy source code
COPY . .

# Expose port
EXPOSE 5000

# Run the application
CMD ["uv", "run", "gunicorn", "--conf", "src/gunicorn.py", "--chdir", "src", "--bind", "0.0.0.0:5000", "main:app"]