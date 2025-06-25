# alembic/env.py - Versão Final com Correção de Encoding

import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# --- Bloco de Carregamento de Configuração ---
from pydantic_settings import BaseSettings, SettingsConfigDict

class AlembicSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra='ignore'
    )
    DATABASE_URL: str

settings = AlembicSettings()
config = context.config

# --- Lógica de Correção de Encoding ---
db_url = settings.DATABASE_URL
if "client_encoding" not in db_url:
    separator = "?" if "?" not in db_url else "&"
    db_url += f"{separator}client_encoding=utf8"
    print(f"INFO: URL de conexão ajustada para usar UTF-8.")

config.set_main_option("sqlalchemy.url", db_url)
# --- Fim da Lógica de Correção ---

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Importa a Base dos modelos para que o autogenerate funcione
# Assumindo que Jules criou uma base unificada em src/aurora_platform/models/base.py
# Se o caminho for diferente, precisaremos ajustar.
from src.aurora_platform.models.base import Base
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
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
            connection=connection, target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()