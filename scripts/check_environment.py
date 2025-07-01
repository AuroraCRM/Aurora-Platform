# scripts/check_environment.py

import sys
import asyncio
import logging
import os

# Configuração básica de logging para este script
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


async def check_environment():
    """
    Script de diagnóstico para verificar o ambiente e as dependências críticas do Aurora-Platform.
    """
    print("-" * 50)
    print("Iniciando Verificação do Ambiente Aurora...")
    print("-" * 50)

    # 1. Verificar Versão do Python
    logging.info(f"Versão do Python: {sys.version}")
    if sys.version_info < (3, 10):
        logging.error("ERRO: O Aurora-Platform requer Python 3.10 ou superior.")
        return

    # 2. Verificar Bibliotecas Essenciais
    try:
        import fastapi
        import uvicorn
        import pydantic
        import sqlalchemy
        import httpx
        import aioredis # type: ignore

        logging.info("Verificação de bibliotecas principais: OK")
        logging.info(f"  - FastAPI version: {fastapi.__version__}")
        logging.info(f"  - Pydantic version: {pydantic.__version__}")
        logging.info(f"  - SQLAlchemy version: {sqlalchemy.__version__}")
        logging.info(f"  - aioredis version: {aioredis.__version__}")

    except ImportError as e:
        logging.error(f"ERRO CRÍTICO: Dependência faltando! {e.name}")
        logging.error(
            "Execute 'pip install -r requirements.txt' (e requirements-test.txt) para instalar as dependências."
        )
        return

    # 3. Verificar Conectividade com Serviços Externos (opcional, mas recomendado)
    print("-" * 50)
    logging.info("Verificando conectividade com serviços...")

    # Tenta conectar com o Redis
    try:
        from aurora_platform.config import settings

        # Usa um timeout curto para não prender o script
        redis_client = aioredis.from_url(settings.REDIS_URL)
        await asyncio.wait_for(redis_client.ping(), timeout=3.0)
        logging.info("Conexão com Redis: OK")
        await redis_client.close()
    except Exception as e:
        logging.warning(
            f"AVISO: Não foi possível conectar ao Redis em '{settings.REDIS_URL}'."
        )
        logging.warning(f"   -> Causa: {e}")
        logging.warning(
            "   -> Certifique-se de que seu container Docker do Redis está em execução."
        )

    # Tenta conectar com o Banco de Dados
    try:
        from aurora_platform.database import engine # Corrigido para importar de database.py

        with engine.connect() as conn:  # Renomeado para conn
            logging.info(f"Conexão com Banco de Dados ({engine.url.drivername}): OK") # Usado engine.url
    except Exception as e:
        logging.warning("AVISO: Não foi possível conectar ao Banco de Dados.") # Removido f-string
        logging.warning(f"   -> Causa: {e}")
        logging.warning(
            "   -> Certifique-se de que seu container Docker do PostgreSQL está em execução."
        )

    print("-" * 50)
    logging.info("Verificação do ambiente concluída.")
    print("-" * 50)


if __name__ == "__main__":
    # 'sys' e 'os' já foram importados no topo do arquivo.
    # Esta lógica de path pode ser desnecessária se o script for executado com poetry run
    # ou se PYTHONPATH estiver configurado.
    # Adicionar ao path apenas se não estiver lá.
    src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

    asyncio.run(check_environment())
