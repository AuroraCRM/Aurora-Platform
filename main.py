# Arquivo de compatibilidade para execução direta
# Recomendamos usar o run_api.py para iniciar a aplicação

import os
import logging
from dotenv import load_dotenv

# Configuração de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Carrega variáveis de ambiente
load_dotenv()

if __name__ == "__main__":
    logger.info("Iniciando a aplicação Aurora CRM...")

    # Importa a aplicação principal
    from aurora.main import app
    import uvicorn

    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    debug = os.getenv("DEBUG", "False").lower() == "true"

    logger.info(f"Servidor iniciando em http://{host}:{port}")
    logger.info("Para acessar a documentação da API, visite http://localhost:8000/docs")

    uvicorn.run(app, host=host, port=port, reload=debug)
