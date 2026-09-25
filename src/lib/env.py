import os
from typing import Any

from flask import request

# Environment variables mirrored from the Worker bindings into os.environ.
VARIABLES = (
    "AWS_ACCESS_KEY_ID",
    "AWS_ENDPOINT_URL_S3",
    "AWS_REGION",
    "AWS_SECRET_ACCESS_KEY",
    "GOOGLE_CLIENT_ID",
    "GOOGLE_CLIENT_SECRET",
    "NEWS_API_KEY",
    "OPENROUTER_API_KEY",
    "OPENROUTER_MODEL",
    "OPENROUTER_REFERER",
    "OPENROUTER_TITLE",
    "OPENWEATHER_API_KEY",
    "RESEND_API_KEY",
    "RESEND_FROM_EMAIL",
    "RESEND_FROM_NAME",
    "SECRET_KEY",
    "TURNSTILE_SECRET_KEY",
    "TURNSTILE_SITE_KEY",
)


def get(name: str, default: str | None = None) -> str | None:
    return os.environ.get(name, default)


def require(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is required.")
    return value


def binding(name: str) -> Any:
    """Return a Cloudflare binding for the current Flask request."""
    return getattr(request.environ["workers.env"], name)


def sync(workers_env: Any) -> None:
    """Mirror string bindings into os.environ for code that reads it directly."""
    if workers_env is None:
        return
    for name in VARIABLES:
        value = getattr(workers_env, name, None)
        if isinstance(value, str):
            os.environ[name] = value
