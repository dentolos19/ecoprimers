import os

from flask import Flask

from lib import ai, database, google, storage

# Load environment variables outside the Workers runtime
from utils import load_environment

load_environment()

# Initialize Flask app
app = Flask(__name__, static_folder=None, template_folder="templates")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")


original_wsgi_app = app.wsgi_app


def worker_wsgi_app(environ, start_response):
    """Initialize Worker bindings and services before each WSGI request."""
    from lib import env

    workers_env = environ.get("workers.env")

    # Mirror string bindings into os.environ before any handler reads them.
    env.sync(workers_env)

    if not app.config["SECRET_KEY"]:
        app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

    ai.init(app)
    google.init(app)

    return original_wsgi_app(environ, start_response)


app.wsgi_app = worker_wsgi_app  # ty: ignore[invalid-assignment] - WSGI middleware replaces the bound method.

# Initialize internal systems
storage.init(app)
database.init(app)

# Import routes into the main module
from routes import *


@app.get("/static/<path:path>")
@app.get("/icon.png")
def serve_asset(path="icon.png"):
    from pathlib import Path

    from flask import Response, request, send_from_directory

    asset_path = "icon.png" if path == "icon.png" else f"static/{path}"
    workers_env = request.environ.get("workers.env")
    if workers_env is None:
        return send_from_directory(Path(__file__).resolve().parents[1] / "public", asset_path)

    from pyodide.ffi import run_sync

    result = run_sync(workers_env.ASSETS.fetch(f"https://assets.local/{asset_path}"))
    return Response(run_sync(result.bytes()), status=result.status, headers=result.headers)
