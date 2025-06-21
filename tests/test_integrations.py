# tests/unit/test_integrations.py

import pytest
import httpx
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException

# Importando os componentes a serem testados
from aurora.integrations.cnpj_provider import CNPJaProvider
from aurora.config import settings

# Mock para simular a resposta da API em caso de sucesso
MOCK_API_SUCCESS_DATA = {
    "taxId": "11223344000155",
    "company": {"name": "Empresa de Teste Sucesso"},
}


@pytest.fixture
def mock_httpx_client():
    """Fixture que cria um mock para o httpx.AsyncClient para ser injetado nos testes."""
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_instance = mock_client_class.return_value.__aenter__.return_value
        yield mock_instance


def create_mock_response(status_code: int, json_data: dict = None) -> httpx.Response:
    """Função auxiliar para criar um objeto de resposta httpx mockado e completo."""
    response = httpx.Response(
        status_code=status_code, json=json_data, request=httpx.Request("GET", "")
    )

    # CORREÇÃO: Mockamos o método raise_for_status para simular o comportamento real
    def raise_for_status_mock():
        if 400 <= status_code < 600:
            raise httpx.HTTPStatusError(
                message="", request=response.request, response=response
            )

    response.raise_for_status = raise_for_status_mock
    return response


@pytest.mark.asyncio
async def test_cnpj_provider_uses_primary_key_first(mock_httpx_client, monkeypatch):
    """Testa se o provedor usa a chave primária primeiro e retorna sucesso."""
    monkeypatch.setattr(settings, "CNPJA_PRIMARY_KEY", "valid_primary_key")
    mock_httpx_client.get.return_value = create_mock_response(
        200, MOCK_API_SUCCESS_DATA
    )

    provider = CNPJaProvider()
    result = await provider.get_cnpj_data("11223344000155")

    assert result[0] == MOCK_API_SUCCESS_DATA
    called_headers = mock_httpx_client.get.call_args[1]["headers"]
    assert called_headers["Authorization"] == "Bearer valid_primary_key"


@pytest.mark.asyncio
async def test_cnpj_provider_falls_back_to_secondary_key(
    mock_httpx_client, monkeypatch
):
    """Testa se o provedor tenta a chave secundária quando a primária falha."""
    monkeypatch.setattr(settings, "CNPJA_PRIMARY_KEY", "invalid_primary_key")
    monkeypatch.setattr(settings, "CNPJA_SECONDARY_KEY", "valid_secondary_key")

    mock_httpx_client.get.side_effect = [
        create_mock_response(401, {"error": "unauthorized"}),
        create_mock_response(200, MOCK_API_SUCCESS_DATA),
    ]

    provider = CNPJaProvider()
    result = await provider.get_cnpj_data("11223344000155")

    assert result[0] == MOCK_API_SUCCESS_DATA
    assert mock_httpx_client.get.call_count == 2
    second_call_headers = mock_httpx_client.get.call_args_list[1][1]["headers"]
    assert second_call_headers["Authorization"] == "Bearer valid_secondary_key"


@pytest.mark.asyncio
async def test_cnpj_provider_falls_back_to_free_api(mock_httpx_client, monkeypatch):
    """Testa se o provedor recorre à API gratuita quando ambas as chaves pagas falham."""
    monkeypatch.setattr(settings, "CNPJA_PRIMARY_KEY", "invalid_primary_key")
    monkeypatch.setattr(settings, "CNPJA_SECONDARY_KEY", "invalid_secondary_key")

    mock_httpx_client.get.side_effect = [
        create_mock_response(401),
        create_mock_response(429),
        create_mock_response(200, MOCK_API_SUCCESS_DATA),
    ]

    provider = CNPJaProvider()
    result = await provider.get_cnpj_data("11223344000155")

    assert result[0] == MOCK_API_SUCCESS_DATA
    assert mock_httpx_client.get.call_count == 3
    third_call_headers = mock_httpx_client.get.call_args_list[2][1]["headers"]
    assert "Authorization" not in third_call_headers
