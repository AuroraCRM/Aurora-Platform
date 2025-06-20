#!/usr/bin/env python3
"""
Script para verificar a configuração do ambiente Aurora-Platform.
Verifica as dependências, variáveis de ambiente e conexões necessárias.
"""

import os
import sys
import importlib
import logging
from dotenv import load_dotenv

# Configuração de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def check_python_version():
    """Verifica se a versão do Python é compatível."""
    required_version = (3, 8)
    current_version = sys.version_info

    if current_version < required_version:
        logger.error(
            f"Versão do Python incompatível. Requer Python {required_version[0]}.{required_version[1]} ou superior."
        )
        return False

    logger.info(f"Versão do Python: {sys.version}")
    return True


def check_dependencies():
    """Verifica se as dependências necessárias estão instaladas."""
    required_packages = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "pydantic",
        "python-dotenv",
        "httpx",
        "aioredis",
        "email-validator",
    ]

    missing_packages = []

    for package in required_packages:
        try:
            importlib.import_module(package)
            logger.info(f"✓ {package} instalado")
        except ImportError:
            logger.error(f"✗ {package} não encontrado")
            missing_packages.append(package)

    return len(missing_packages) == 0


def check_environment_variables():
    """Verifica se as variáveis de ambiente necessárias estão configuradas."""
    load_dotenv()

    required_vars = [
        "DATABASE_URL",
        "SECRET_KEY",
        "ALGORITHM",
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "CNPJA_API_URL",
        "CNPJA_API_KEY",
    ]

    missing_vars = []

    for var in required_vars:
        if not os.getenv(var):
            logger.error(f"✗ Variável de ambiente {var} não configurada")
            missing_vars.append(var)
        else:
            logger.info(f"✓ Variável de ambiente {var} configurada")

    return len(missing_vars) == 0


def check_database_connection():
    """Verifica a conexão com o banco de dados."""
    try:
        from sqlalchemy import create_engine
        from aurora.config import settings

        engine = create_engine(settings.DATABASE_URL)
        connection = engine.connect()
        connection.close()

        logger.info("✓ Conexão com o banco de dados estabelecida com sucesso")
        return True
    except Exception as e:
        logger.error(f"✗ Erro ao conectar ao banco de dados: {str(e)}")
        return False


def main():
    """Função principal que executa todas as verificações."""
    logger.info("Iniciando verificação do ambiente Aurora-Platform...")

    python_ok = check_python_version()
    deps_ok = check_dependencies()
    env_ok = check_environment_variables()

    # Só verifica a conexão com o banco se as outras verificações passarem
    if python_ok and deps_ok and env_ok:
        db_ok = check_database_connection()
    else:
        db_ok = False
        logger.warning(
            "Pulando verificação de banco de dados devido a erros anteriores"
        )

    # Resultado final
    if all([python_ok, deps_ok, env_ok, db_ok]):
        logger.info("✅ Ambiente configurado corretamente!")
        return 0
    else:
        logger.error(
            "❌ Ambiente com problemas de configuração. Corrija os erros acima."
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
