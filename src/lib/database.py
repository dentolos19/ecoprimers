import os
from typing import Any, cast

from flask import Flask
from flask import session as flask_session
from flask_sqlalchemy import SQLAlchemy
from lib.models import Base

initialized: bool = False
sql = cast(SQLAlchemy, None)
session: Any = None


def get_url() -> str:
    url = os.environ.get("DATABASE_URL", "").strip().strip('"')
    if not url:
        raise RuntimeError("DATABASE_URL is required.")
    if url.startswith("postgres://"):
        url = "postgresql://" + url.removeprefix("postgres://")
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url.removeprefix("postgresql://")
    return url


def _alembic_config():
    from pathlib import Path

    from alembic.config import Config

    project_dir = Path(__file__).resolve().parents[2]
    return Config(project_dir / "alembic.ini")


def _migrate(revision: str = "head") -> None:
    from alembic import command
    from sqlalchemy import create_engine
    from sqlalchemy.pool import NullPool

    engine = create_engine(get_url(), poolclass=NullPool)
    try:
        with engine.connect() as connection:
            config = _alembic_config()
            config.attributes["connection"] = connection
            command.upgrade(config, revision)
    finally:
        engine.dispose()


def init(app: Flask) -> None:
    global initialized, session, sql

    if initialized:
        return

    # Deployment runs migrations before rollout; remote database I/O must not block container startup.
    app.config["SQLALCHEMY_DATABASE_URI"] = get_url()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    sql = SQLAlchemy(model_class=Base)
    session = sql.session
    sql.init_app(app)
    initialized = True


def setup() -> None:
    _migrate()


def reset() -> None:
    from alembic import command
    from sqlalchemy import create_engine
    from sqlalchemy.pool import NullPool

    sql.session.remove()

    config = _alembic_config()
    engine = create_engine(get_url(), poolclass=NullPool)
    try:
        with engine.connect() as connection:
            config.attributes["connection"] = connection
            command.downgrade(config, "base")
            command.upgrade(config, "head")
    finally:
        engine.dispose()

    flask_session.clear()
