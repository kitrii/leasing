import sys
import os
from logging.config import fileConfig

from sqlalchemy import create_engine
from sqlalchemy import pool
from alembic import context
# Добавляем путь к корню проекта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Теперь можно импортировать app.*
from app.core.config import settings
from app.db.database import Base
from app.models import user, equipment, application, payment, document


# Alembic Config
config = context.config

# Logging
fileConfig(config.config_file_name)

# Metadata for autogenerate
target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    url = settings.DATABASE_URL

    engine = create_engine(
        url,
        poolclass=pool.NullPool,
    )

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()


# **Creating Migration Commands**
# ```
# poetry run alembi revision --autogenerate -m "init tables"
# poetry run alembi upgrade head
# ```