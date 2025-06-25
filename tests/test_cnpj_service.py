import pytest
from unittest.mock import AsyncMock  # Para mockar métodos async

# Supondo que CNPJService e CNPJResponse estão corretamente definidos e importáveis
from aurora_platform.services.cnpj_service import CNPJService
from aurora_platform.schemas.cnpj_schema import CNPJResponse
from aurora_platform.integrations.cnpj_provider import CNPJaProvider  # Para mock
from fastapi import HTTPException  # Para testar exceção


@pytest.mark.asyncio  # Marcar o teste como assíncrono
async def test_get_cnpj_data_success():
    """Testa a busca bem-sucedida de dados de CNPJ pelo CNPJService."""

    # Dados mockados que o CNPJaProvider.get_cnpj_data retornaria (parte do tuple)
    mock_provider_data = {
        "cnpj": "12345678000195",
        "razao_social": "Empresa Mockada LTDA",
        "nome_fantasia": "Nome Fantasia Mock",
        "situacao_cadastral": "ATIVA",
        "data_abertura": "2020-01-15",
        "cnae_principal": "1234-5/00",
        "endereco": {
            "logradouro": "Rua Mock",
            "numero": "123",
            "complemento": "Apto 1",
            "bairro": "Mockville",
            "municipio": "Mock City",
            "uf": "MK",
            "cep": "00000-000",
        },
        "contato": {"telefone": "999998888", "email": "contato@mock.com"},
        # Adicione outros campos conforme o schema CNPJResponse espera
    }
    mock_fonte = "gratuita"  # A segunda parte da tupla retornada pelo provider

    # Mockar a instância de CNPJaProvider
    mock_cnpj_provider = AsyncMock(spec=CNPJaProvider)
    # Configurar o valor de retorno para o método get_cnpj_data do provider mockado
    mock_cnpj_provider.get_cnpj_data.return_value = (mock_provider_data, mock_fonte)

    # Instanciar CNPJService com o provider mockado
    cnpj_service = CNPJService(cnpj_provider=mock_cnpj_provider)

    # Chamar o método do serviço que queremos testar
    cnpj_str_to_test = "12345678000195"
    result_schema = await cnpj_service.get_cnpj_data(cnpj_str_to_test)

    # Verificar se o método do provider mockado foi chamado corretamente
    mock_cnpj_provider.get_cnpj_data.assert_called_once_with(cnpj_str_to_test)

    # Verificar se o resultado é uma instância do schema esperado
    assert isinstance(result_schema, CNPJResponse)

    # Verificar alguns campos do resultado
    assert result_schema.cnpj == mock_provider_data["cnpj"]
    assert result_schema.razao_social == mock_provider_data["razao_social"]
    assert result_schema.nome_fantasia == mock_provider_data["nome_fantasia"]
    assert result_schema.situacao_cadastral == mock_provider_data["situacao_cadastral"]


@pytest.mark.asyncio
async def test_get_cnpj_data_provider_raises_exception():
    """Testa o repasse de exceção do provider pelo serviço."""
    mock_cnpj_provider = AsyncMock(spec=CNPJaProvider)
    # Simular o provider levantando uma HTTPException
    mock_cnpj_provider.get_cnpj_data.side_effect = HTTPException(
        status_code=503, detail="Service unavailable from provider"
    )

    cnpj_service = CNPJService(cnpj_provider=mock_cnpj_provider)

    cnpj_to_test = "00000000000000"
    with pytest.raises(HTTPException) as exc_info:
        await cnpj_service.get_cnpj_data(cnpj_to_test)

    assert exc_info.value.status_code == 503
    assert exc_info.value.detail == "Service unavailable from provider"
    mock_cnpj_provider.get_cnpj_data.assert_called_once_with(cnpj_to_test)
