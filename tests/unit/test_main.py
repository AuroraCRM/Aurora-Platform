from fastapi.testclient import TestClient
from aurora.main import app

# Cria um cliente de teste para a nossa aplicação
client = TestClient(app)

def test_read_root():
    """
    Testa se a rota raiz está funcionando corretamente.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Bem-vindo à API da Aurora CRM!",
        "docs": "/docs",
        "version": "1.0.0"
    }

def test_docs_redirect():
    """
    Testa se a rota /docs (Swagger UI) está acessível.
    """
    response = client.get("/docs")
    assert response.status_code == 200
    assert "Swagger UI" in response.text
