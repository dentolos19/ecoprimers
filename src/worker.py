"""Cloudflare Python Worker entrypoint for the Flask application."""

from workers import wsgi

from lib.room import Room
from main import app

__all__ = ["Default", "Room"]

Default = wsgi.entrypoint(app)
