# alembic/env.py

# --- Início do Bloco de Carregamento de Configuração ---
import os
import sys  # sys precisa ser importado antes de modificar sys.path
from logging.config import fileConfig

# Carrega as variáveis do .env para o ambiente ANTES de qualquer outra coisa
# Isso garante que o Alembic encontre a DATABASE_URL
from pydantic_settings import BaseSettings


class AlembicSettings(BaseSettings):
    DATABASE_URL: str

    class Config:
        env_file = ".env"


try:
    if os.path.exists(".env"):
        settings_alembic = AlembicSettings(_env_file=".env")
    elif os.path.exists("../.env"):
        settings_alembic = AlembicSettings(_env_file="../.env")
    else:
        settings_alembic = AlembicSettings()
    DATABASE_URL_FROM_ENV = settings_alembic.DATABASE_URL
except Exception as e:
    print(
        f"Aviso: Não foi possível carregar DATABASE_URL via pydantic-settings: {e}"
    )
    DATABASE_URL_FROM_ENV = None
# --- Fim do Bloco de Carregamento de Configuração ---

from alembic import context  # Movido para cá
from sqlalchemy import create_engine  # Movido para cá
from sqlmodel import SQLModel  # Movido para cá

# Ajusta o path para permitir importações do seu pacote
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

# Importar modelos SQLModel para que Alembic os detecte
from aurora_platform.models.cliente_model import Cliente  # noqa: F401
from aurora_platform.models.lead_models import LeadDB  # noqa: F401
from aurora_platform.models.usuario_model import Usuario  # noqa: F401
from aurora_platform.models.ai_log_model import AIInteractionLog  # noqa: F401

config = context.config

if DATABASE_URL_FROM_ENV:
    config.set_main_option("sqlalchemy.url", DATABASE_URL_FROM_ENV)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    if not url:
        raise ValueError(
            "sqlalchemy.url não está configurada para o modo offline do Alembic."
        )

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    db_url_for_online = config.get_main_option("sqlalchemy.url")
    if not db_url_for_online:
        raise ValueError(
            "sqlalchemy.url não está configurada para o modo online do Alembic. "
            "Verifique alembic.ini e a variável de ambiente DATABASE_URL."
        )

    connectable = create_engine(db_url_for_online)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
