from fastapi.testclient import TestClient
from aurora_platform.main import app  # Ajuste o import conforme a estrutura do seu projeto
import datetime

client = TestClient(app)

def test_get_status_success():
    """
    Testa se o endpoint /api/v1/status retorna 200 OK e a resposta esperada.
    """
    response = client.get("/api/v1/status")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "Operational"

    # Valida o timestamp
    assert "timestamp" in data
    try:
        # Verifica se o timestamp está no formato ISO 8601 e é UTC
        timestamp = datetime.datetime.fromisoformat(data["timestamp"])
        assert timestamp.tzinfo == datetime.timezone.utc
    except ValueError:
        assert False, "Timestamp não está no formato ISO 8601 correto ou não é UTC"

def test_status_response_format():
    """
    Testa se a resposta do endpoint /api/v1/status contém as chaves corretas.
    """
    response = client.get("/api/v1/status")
    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert len(data.keys()) == 2 # Garante que não há chaves extras inesperadas
