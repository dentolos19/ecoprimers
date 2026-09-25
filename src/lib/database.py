"""Request-scoped SQLAlchemy access to PostgreSQL."""

import hashlib
import os
from urllib.parse import quote

from flask import Flask, g, request
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool

from lib.models import Base


def worker_pbkdf2(hash_name, password, salt, iterations, dklen=None):
    from Crypto.Hash import SHA256
    from Crypto.Protocol.KDF import PBKDF2

    if hash_name != "sha256":
        raise ValueError(f"Unsupported SCRAM hash: {hash_name}")
    return PBKDF2(password, salt, dkLen=dklen or SHA256.digest_size, count=iterations, hmac_hash_module=SHA256)


class Database:
    @property
    def engine(self):
        if "db_engine" not in g:
            workers_env = request.environ.get("workers.env")
            if workers_env is not None:
                if not hasattr(hashlib, "pbkdf2_hmac"):
                    hashlib.pbkdf2_hmac = worker_pbkdf2
                g.db_engine = create_engine(
                    get_worker_url(workers_env), connect_args={"ssl_context": None}, poolclass=NullPool
                )
            else:
                g.db_engine = create_engine(get_url(), poolclass=NullPool)
        return g.db_engine

    @property
    def session(self) -> Session:
        if "db_session" not in g:
            g.db_session = Session(self.engine)
        return g.db_session


sql = Database()


def get_url() -> str:
    url = os.environ.get("DATABASE_URL", "").strip().strip('"')
    if not url:
        raise RuntimeError("DATABASE_URL is required.")
    if url.startswith("postgres://"):
        url = "postgresql://" + url.removeprefix("postgres://")
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url.removeprefix("postgresql://")
    return url


def get_worker_url(workers_env) -> str:
    hyperdrive = workers_env.HYPERDRIVE
    user = quote(str(hyperdrive.user), safe="")
    password = quote(str(hyperdrive.password), safe="")
    database = quote(str(hyperdrive.database), safe="")
    return f"postgresql+pg8000://{user}:{password}@{hyperdrive.host}:{hyperdrive.port}/{database}"


def init(app: Flask) -> None:
    @app.teardown_appcontext
    def close_database(error):
        session = g.pop("db_session", None)
        if session is not None:
            session.close()
        engine = g.pop("db_engine", None)
        if engine is not None:
            engine.dispose()


def setup() -> None:
    from pathlib import Path

    from alembic import command
    from alembic.config import Config

    config = Config(Path(__file__).resolve().parents[2] / "alembic.ini")
    command.upgrade(config, "head")


def reset() -> None:
    sql.session.close()
    Base.metadata.drop_all(sql.engine)
    Base.metadata.create_all(sql.engine)
