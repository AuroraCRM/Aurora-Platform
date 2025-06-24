from fastapi.testclient import TestClient
# from aurora_platform.main import app # Removido F401

# Não precisamos mais instanciar TestClient(app) globalmente aqui,
# pois a fixture test_client o fornecerá.


def test_read_root(test_client: TestClient):  # Usa a fixture test_client
    """
    Testa se a rota raiz está funcionando corretamente.
    """
    response = test_client.get("/")  # Usa a fixture
    assert response.status_code == 200
    # Ajustado para corresponder à nova resposta do endpoint raiz
    assert response.json() == {
        "message": "Bem-vindo à Aurora Platform",
        "version": "1.0.0",  # Assumindo que app.version é "1.0.0"
        "docs_url": "/docs",
    }


def test_docs_redirect(test_client: TestClient):  # Usa a fixture test_client
    """
    Testa se a rota /docs (Swagger UI) está acessível.
    """
    response = test_client.get("/docs")  # Usa a fixture
    assert response.status_code == 200
    assert "Swagger UI" in response.text
