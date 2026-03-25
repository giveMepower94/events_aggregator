import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context
from src.events_agg.core.config import settings
from src.events_agg.db.base import Base
from src.events_agg.models.event import Event, Place  # noqa
from src.events_agg.models.idempotency import IdempotencyKey  # noqa
from src.events_agg.models.outbox import OutboxMessage  # noqa
from src.events_agg.models.sync_state import SyncState  # noqa
from src.events_agg.models.ticket import Ticket  # noqa

config = context.config

sync_database_url = settings.database_url.replace(
    "postgresql+asyncpg",
    "postgresql+psycopg",
)

config.set_main_option("sqlalchemy.url", sync_database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=sync_database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
