import uvicorn
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

if __name__ == "__main__":
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    debug = os.getenv("DEBUG", "False").lower() == "true"

    print(f"Iniciando servidor na porta {port}...")
    print("Para testar a API, acesse: http://localhost:8000/docs")

    uvicorn.run("aurora.main:app", host=host, port=port, reload=debug)
