import os
import sys
from pathlib import Path
from logging.config import fileConfig
from alembic import context
from sqlalchemy import engine_from_config, pool

# 1. Configuração ABSOLUTA do path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_ROOT = PROJECT_ROOT / "src"

# Adiciona caminhos ao sys.path
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(SRC_ROOT))

# 2. Forçar reconhecimento do pacote
try:
    import aurora_platform
    print(f"✅ Pacote 'aurora_platform' encontrado em: {aurora_platform.__file__}")
except ImportError as e:
    print(f"❌ Falha crítica ao importar 'aurora_platform': {e}")
    print("🛠️  Verifique se o pacote está instalado com 'poetry install'")
    print(f"🔍 sys.path: {sys.path}")
    raise

# 3. Configuração do Alembic
config = context.config

# Configura logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 4. Importação segura dos modelos
try:
    from aurora_platform.models.base import Base
    print("✅ Importação de 'aurora_platform.models.base' bem-sucedida")
    target_metadata = Base.metadata
except ImportError as e:
    print(f"❌ Erro na importação absoluta: {e}")
    try:
        # Tentativa de fallback com importação relativa
        from ...src.aurora_platform.models.base import Base
        print("⚠️ Usando importação relativa como fallback")
        target_metadata = Base.metadata
    except ImportError as e2:
        print(f"❌❌ Erro duplo na importação:")
        print(f"1. Absoluta: {e}")
        print(f"2. Relativa: {e2}")
        print("💡 Soluções possíveis:")
        print("a) Execute 'poetry run pip install -e .' na raiz do projeto")
        print("b) Verifique a estrutura de diretórios em 'src/aurora_platform'")
        print("c) Confira se o arquivo base.py existe em 'src/aurora_platform/models/'")
        raise e2

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
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
            compare_server_default=True
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()