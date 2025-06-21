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
    load_dotenv(override=True)

    required_vars = [
        "DATABASE_URL",
        "SECRET_KEY",
        "ALGORITHM",
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "CNPJA_PAID_URL",
        "CNPJA_FREE_URL",
        "CNPJA_PRIMARY_KEY",
        "CNPJA_SECONDARY_KEY",
        "CNPJA_AUTH_TYPE",
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
    from sqlalchemy import create_engine
    from sqlalchemy.exc import OperationalError
    from aurora.config import settings

    try:
        logger.info("🔄 Tentando conectar ao banco de dados...")
        engine = create_engine(settings.DATABASE_URL)
        connection = engine.connect()
        connection.close()
        logger.info("✅ Conexão com o banco de dados estabelecida com sucesso.")

    except OperationalError as e:
        logger.error("❌ ERRO CRÍTICO: Não foi possível conectar ao banco de dados.")
        logger.error(f"Verifique a string de conexão: {settings.DATABASE_URL}")
        logger.error(f"Detalhes técnicos: {e}")
        # sys.exit(1)

    except Exception as e:
        logger.error(
            "❌ Ocorreu um erro inesperado ao verificar a conexão com o banco de dados."
        )
        logger.error(f"Detalhes: {e}")
        # sys.exit(1)
