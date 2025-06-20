#!/usr/bin/env python3
"""
Script para executar os testes do projeto Aurora-Platform.
"""

import os
import sys
import pytest
import logging
from dotenv import load_dotenv

# Configuração de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Carrega variáveis de ambiente
load_dotenv()


def main():
    """Função principal que executa os testes."""
    logger.info("Iniciando execução dos testes...")

    # Verifica se a variável de ambiente TEST_DATABASE_URL está configurada
    if not os.getenv("TEST_DATABASE_URL"):
        logger.error("Variável de ambiente TEST_DATABASE_URL não configurada")
        return 1

    # Executa os testes
    result = pytest.main(["-v", "tests/"])

    if result == 0:
        logger.info("✅ Todos os testes passaram!")
    else:
        logger.error("❌ Alguns testes falharam.")

    return result


if __name__ == "__main__":
    sys.exit(main())
