# alembic/env.py

# --- Início do Bloco de Carregamento de Configuração ---
import os
import sys  # sys precisa ser importado antes de modificar sys.path
from logging.config import fileConfig

# Carrega as variáveis do .env para o ambiente ANTES de qualquer outra coisa
# Isso garante que o Alembic encontre a DATABASE_URL
from pydantic_settings import BaseSettings, SettingsConfigDict # Adicionado SettingsConfigDict


class AlembicSettings(BaseSettings):
    DATABASE_URL: str
    # Configuração para Pydantic V2
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8", # Adicionado conforme instrução
        extra='ignore' # Adicionado conforme instrução
    )

try:
    # Lógica de tentativa de carregamento de .env (pode ser simplificada se SettingsConfigDict lida bem com paths)
    # Pydantic-settings v2 procura .env no CWD por padrão se env_file não for absoluto.
    # Para robustez, pode-se verificar os caminhos como antes ou confiar na detecção automática.
    # No entanto, o exemplo da tarefa instancia settings = AlembicSettings() diretamente.
    # Vou seguir o exemplo da tarefa, que é mais limpo se o .env estiver no lugar esperado (raiz do projeto).
    settings_obj = AlembicSettings()
    DATABASE_URL_FROM_ENV = settings_obj.DATABASE_URL
except Exception as e:
    print(
        f"Aviso: Não foi possível carregar DATABASE_URL via pydantic-settings: {e}"
    )
    DATABASE_URL_FROM_ENV = None
# --- Fim do Bloco de Carregamento de Configuração ---

# Importações principais do Alembic e SQLAlchemy/SQLModel
from alembic import context
from sqlalchemy import create_engine
from sqlmodel import SQLModel

# --- INÍCIO DA LÓGICA DE CORREÇÃO DA URL (conforme instrução da tarefa) ---
# Esta seção deve vir ANTES de config = context.config e do uso de DATABASE_URL_FROM_ENV
# para setar a opção principal do Alembic.

db_url_corrigida = None
if DATABASE_URL_FROM_ENV:
    db_url_corrigida = DATABASE_URL_FROM_ENV
    # Garante que a codificação do cliente seja utf8 para evitar UnicodeDecodeError
    if "client_encoding" not in db_url_corrigida:
        # Adiciona o parâmetro usando '?' se não houver outros, ou '&' se já houver.
        separator = "?" if "?" not in db_url_corrigida else "&"
        db_url_corrigida += f"{separator}client_encoding=utf8"
elif context.config.get_main_option("sqlalchemy.url"):
    # Fallback para a URL do alembic.ini se DATABASE_URL_FROM_ENV não foi carregada
    # Isso é importante se %(DATABASE_URL)s estiver no alembic.ini e for preenchida por env var
    # que pydantic-settings não pegou por algum motivo.
    db_url_ini = context.config.get_main_option("sqlalchemy.url")
    db_url_corrigida = db_url_ini
    if "client_encoding" not in db_url_corrigida:
        separator = "?" if "?" not in db_url_corrigida else "&"
        db_url_corrigida += f"{separator}client_encoding=utf8"
# --- FIM DA LÓGICA DE CORREÇÃO DA URL ---


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

# Substitui a URL do alembic.ini pela URL corrigida (se disponível)
if db_url_corrigida:
    config.set_main_option("sqlalchemy.url", db_url_corrigida)
# Se db_url_corrigida for None (nem env nem ini tinham uma URL base),
# Alembic falhará mais tarde ao tentar obter sqlalchemy.url, o que é esperado.

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
