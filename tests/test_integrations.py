import pytest
import httpx
from unittest.mock import patch, MagicMock  # MagicMock para simular o objeto response

from aurora_platform.integrations.cnpj_provider import CNPJaProvider
from aurora_platform.config import settings  # Para configurar a URL base
from fastapi import HTTPException

# Mock para simular a resposta da API pública cnpj.ws em caso de sucesso
MOCK_CNPJ_WS_SUCCESS_DATA = {
    "estabelecimento": {
        "cnpj": "11223344000155",  # CNPJ formatado como na API
        "nome_fantasia": "Empresa Teste WS",
        "ddd1": "11",
        "telefone1": "987654321",
        "email": "contato@testews.com",
        "logradouro": "Rua Teste WS",
        "numero": "789",
        "complemento": "Andar 10",
        "bairro": "Bairro WS",
        "cidade": {"nome": "Cidade WS"},
        "estado": {"sigla": "WS"},
        "cep": "99999-777",
    },
    "razao_social": "Razao Social Teste WS LTDA",
    # Adicionar outros campos que a API cnpj.ws retorna e que são usados
}


@pytest.mark.asyncio
async def test_cnpj_provider_get_cnpj_data_success(monkeypatch):
    """Testa a busca bem-sucedida de dados na API cnpj.ws."""

    # Configurar a URL da API para o teste via variável de ambiente
    test_api_url = "https://fake-cnpj-ws.com/v1"
    # Dynaconf espera variáveis de ambiente com prefixo (ex: AURORA_).
    # O nome da variável em settings.get() é CNPJWS_PUBLIC_URL.
    monkeypatch.setenv("AURORA_CNPJWS_PUBLIC_URL", test_api_url)
    settings.reload()  # Forçar Dynaconf a recarregar com a nova env var

    # Criar um mock para a resposta HTTP de httpx.AsyncClient().get()
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    # Simular o conteúdo da resposta (bytes) e o método .json() e .content.decode()
    # A API cnpj.ws retorna JSON, então o .content precisa ser bytes de um JSON string.
    # O provider tenta response.content.decode('utf-8') e depois 'latin-1'.
    mock_response.content = (
        str(MOCK_CNPJ_WS_SUCCESS_DATA).replace("'", '"').encode("utf-8")
    )

    # Mock para o método raise_for_status (não deve levantar exceção para status 200)
    mock_response.raise_for_status = MagicMock()

    # Usar patch para mockar httpx.AsyncClient
    with patch("httpx.AsyncClient") as mock_async_client_class:
        # Configurar o mock do cliente para retornar nosso mock_response quando .get for chamado
        mock_async_client_instance = (
            mock_async_client_class.return_value.__aenter__.return_value
        )
        mock_async_client_instance.get.return_value = mock_response

        provider = CNPJaProvider()
        cnpj_to_test = "11223344000155"
        dados_brutos, fonte = await provider.get_cnpj_data(cnpj_to_test)

        # Verificar se a URL correta foi chamada
        expected_url = f"{test_api_url}/cnpj/{cnpj_to_test}"
        mock_async_client_instance.get.assert_called_once_with(
            expected_url, headers={"Accept": "application/json"}, timeout=10.0
        )

        # Verificar os dados retornados
        assert fonte == "gratuita"
        # Comparar alguns campos chave. A estrutura exata de MOCK_CNPJ_WS_SUCCESS_DATA
        # deve corresponder ao que o provider retorna após json.loads()
        assert dados_brutos["razao_social"] == MOCK_CNPJ_WS_SUCCESS_DATA["razao_social"]
        assert (
            dados_brutos["estabelecimento"]["cnpj"]
            == MOCK_CNPJ_WS_SUCCESS_DATA["estabelecimento"]["cnpj"]
        )


@pytest.mark.asyncio
async def test_cnpj_provider_http_error(monkeypatch):
    """Testa o tratamento de erro HTTP (ex: 404, 500) da API cnpj.ws."""
    test_api_url = "https://fake-cnpj-ws.com/v1"
    monkeypatch.setenv("AURORA_CNPJWS_PUBLIC_URL", test_api_url)  # Usar setenv
    settings.reload()  # Forçar Dynaconf a recarregar

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 404  # Simular um Not Found
    mock_response.request = httpx.Request(
        "GET", f"{test_api_url}/cnpj/00000000000000"
    )  # Necessário para HTTPStatusError

    # Configurar raise_for_status para levantar HTTPStatusError
    mock_response.raise_for_status = MagicMock(
        side_effect=httpx.HTTPStatusError(
            message="Not Found", request=mock_response.request, response=mock_response
        )
    )

    with patch("httpx.AsyncClient") as mock_async_client_class:
        mock_async_client_instance = (
            mock_async_client_class.return_value.__aenter__.return_value
        )
        mock_async_client_instance.get.return_value = mock_response

        provider = CNPJaProvider()
        with pytest.raises(HTTPException) as exc_info:
            await provider.get_cnpj_data(
                "00000000000000"
            )  # CNPJ que causará o erro mockado

        assert exc_info.value.status_code == 404


# Testar a decodificação UTF-8 vs Latin-1 é mais complexo de mockar precisamente
# pois envolve o atributo `response.content` sendo bytes brutos.
# O teste de sucesso já cobre o caminho feliz da decodificação UTF-8.
# Um teste específico para Latin-1 exigiria mockar `response.content.decode('utf-8')`
# para levantar UnicodeDecodeError e então verificar se `response.content.decode('latin-1')` foi chamado.
