from logging.config import fileConfig
import os
import sys

from alembic import context
from sqlalchemy import engine_from_config, pool

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from app import models  # noqa: F401,E402
from app.db.base import Base  # noqa: E402

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Allow database URL via -x db_url=... or environment variable
x_args = context.get_x_argument(as_dictionary=True)
db_url = x_args.get("db_url") or os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")
if not db_url:
    raise RuntimeError("Database URL must be provided via -x db_url=, env DATABASE_URL, or sqlalchemy.url in alembic.ini")

config.set_main_option("sqlalchemy.url", db_url)

target_metadata = Base.metadata


def run_migrations_offline():
    context.configure(url=db_url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


def main():
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()


if __name__ == "__main__":
    main()
