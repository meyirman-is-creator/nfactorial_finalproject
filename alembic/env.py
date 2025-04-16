from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import app.db.base
from app.db.base import Base  # ✅ импорт твоих моделей
from app.core.config import settings  # ✅ настройки, где есть DATABASE_URL

config = context.config
fileConfig(config.config_file_name)

# Устанавливаем URL из настроек FastAPI
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

target_metadata = Base.metadata

def run_migrations_offline():
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

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

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
