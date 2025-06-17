import pytest

from aurora.main import app



def test_read_root(client):
    """Testa se a rota raiz está funcionando corretamente."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Bem-vindo à API do Aurora CRM"}

def test_clientes_endpoint(client):
    """Testa se o endpoint de clientes está disponível."""
    response = client.get("/clientes/")
    # Mesmo que não tenha clientes, o endpoint deve retornar 200 com uma lista vazia
    assert response.status_code == 200
    assert isinstance(response.json(), list)
