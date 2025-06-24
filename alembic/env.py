from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

import os
import sys

# Ajusta o path para permitir importações do seu pacote Aurora
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Importa a base declarativa e, opcionalmente, seus modelos
from aurora.database_config import Base
from aurora.models.cliente_model import Cliente  # garante que o modelo seja carregado

# Este é o objeto Config do Alembic, que carrega as opções do alembic.ini
config = context.config

# Configura o logging via arquivo de configuração
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Aponta para o MetaData dos seus modelos, permitindo o autogenerate
target_metadata = Base.metadata


def run_migrations_offline():
    """Execute as migrações em modo 'offline' (só gera SQL)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()
