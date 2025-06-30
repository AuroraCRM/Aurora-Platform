import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from aurora_platform.main import app

# Fixture para o cliente de teste do FastAPI
@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

# Mock para o Phi3Handler para evitar o carregamento real do modelo durante os testes de integração
@pytest.fixture
def mock_phi3_handler():
    with patch('aurora_platform.models.phi3_handler.Phi3Handler') as MockHandler:
        instance = MockHandler.return_value
        instance.generate_response.return_value = "Mocked Phi-3 response for: Test prompt"
        yield MockHandler

def test_run_phi3_inference_success(client: TestClient, mock_phi3_handler):
    prompt_text = "Test prompt"
    response = client.post(
        "/api/v1/inference/phi3",
        json={
            "prompt": prompt_text,
            "max_new_tokens": 50
        }
    )
    assert response.status_code == 200
    assert response.json() == {"response": "Mocked Phi-3 response for: Test prompt"}
    mock_phi3_handler.return_value.generate_response.assert_called_once_with(
        prompt=prompt_text,
        max_new_tokens=50
    )

def test_run_phi3_inference_missing_prompt(client: TestClient):
    response = client.post(
        "/api/v1/inference/phi3",
        json={
            "max_new_tokens": 50
        }
    )
    assert response.status_code == 422  # Unprocessable Entity (Pydantic validation error)
    assert "prompt" in response.json()["detail"][0]["loc"]

def test_run_phi3_inference_internal_error(client: TestClient, mock_phi3_handler):
    mock_phi3_handler.return_value.generate_response.side_effect = Exception("Simulated internal error")
    response = client.post(
        "/api/v1/inference/phi3",
        json={
            "prompt": "Error test",
            "max_new_tokens": 50
        }
    )
    assert response.status_code == 500
    assert "Failed to get response from Phi-3 model" in response.json()["detail"]
