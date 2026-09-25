from alembic import context
from dotenv import load_dotenv
from sqlalchemy import create_engine, pool

from lib.database import get_url
from lib.models import Base

config = context.config
load_dotenv()

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    supplied_connection = config.attributes.get("connection")
    connectable = supplied_connection or create_engine(get_url(), poolclass=pool.NullPool)

    def migrate(connection) -> None:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            render_as_batch=True,
        )
        with context.begin_transaction():
            context.run_migrations()
        connection.commit()

    if supplied_connection is not None:
        migrate(supplied_connection)
    else:
        with connectable.connect() as connection:
            migrate(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
