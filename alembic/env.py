import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Ensure app is importable
sys.path.append(os.getcwd())

from app.core.config import settings
from app.core.database import Base
from app.models import message_log  # noqa

config = context.config

# Setup logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 👇 IMPORTANT: metadata for autogenerate
target_metadata = Base.metadata

# 👇 Convert async DB URL → sync (Alembic needs sync driver)
DATABASE_URL = settings.DATABASE_URL.replace("+asyncpg", "")


def run_migrations_offline():
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        {"sqlalchemy.url": DATABASE_URL},
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
