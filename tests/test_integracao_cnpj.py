# tests/test_integracao_cnpj.py
from unittest.mock import patch, MagicMock
import pytest
import httpx

# Dados simulados da API CNPJá
mock_cnpj_data_success = {
    "name": "EMPRESA DE TESTE MOCK FINAL",
    "alias": "MOCK TESTE FINAL",
    "taxId": "55444333000122",
    "email": "contato.final@teste.com",
    "phone": "1122224444"
}
mock_cnpj_data_error = {"message": "CNPJ não localizado"}

@patch('aurora.services.servico_crm.httpx.get')
def test_criar_cliente_via_cnpj_sucesso(mock_get, client):
    """Testa o caminho feliz da criação de cliente via CNPJ."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_cnpj_data_success
    mock_get.return_value.raise_for_status.return_value = None

    cnpj_valido = "55444333000122"
    response = client.post(f"/clientes/cnpj/{cnpj_valido}")

    assert response.status_code == 201, f"Ocorreu um erro: {response.json()}"
    data = response.json()
    assert data["razao_social"] == "EMPRESA DE TESTE MOCK FINAL"

@patch('aurora.services.servico_crm.httpx.get')
def test_criar_cliente_via_cnpj_nao_encontrado(mock_get, client):
    """Testa o caminho de falha quando o CNPJ não é encontrado."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.json.return_value = mock_cnpj_data_error
    side_effect = httpx.HTTPStatusError("Not Found", request=MagicMock(), response=mock_response)
    mock_get.side_effect = side_effect

    cnpj_invalido = "00000000000000"
    response = client.post(f"/clientes/cnpj/{cnpj_invalido}")

    assert response.status_code == 404
    assert mock_cnpj_data_error["message"] in response.json()["detail"]