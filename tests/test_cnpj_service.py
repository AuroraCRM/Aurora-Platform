import pytest
from unittest.mock import AsyncMock, patch

# A importação e o uso da classe foram corrigidos aqui
from aurora_platform.services.cnpj_service import CNPJService
from aurora_platform.schemas.cnpj_schema import CNPJResponseSchema # NOME CORRIGIDO
from aurora_platform.integrations.cnpj_provider import CNPJaProvider
from fastapi import HTTPException


@pytest.mark.asyncio
async def test_get_cnpj_data_success():
    """Testa a busca bem-sucedida de dados de CNPJ pelo CNPJService."""

    mock_provider_data = {
        "cnpj": "12345678000195",
        "razao_social": "Empresa Mockada LTDA",
        "nome_fantasia": "Nome Fantasia Mock",
        "situacao_cadastral": "ATIVA",
        # ... outros campos mockados
    }

    mock_cnpj_provider = AsyncMock(spec=CNPJaProvider)
    mock_cnpj_provider.get_cnpj_data.return_value = (mock_provider_data, "CNPJa")

    cnpj_service = CNPJService()
    # Patch the internal provider of CNPJService
    with patch('aurora_platform.services.cnpj_service.CNPJaProvider', return_value=mock_cnpj_provider):
        cnpj_service = CNPJService()
        cnpj_str_to_test = "12345678000195"
        result_dict = await cnpj_service.buscar_dados_cnpj(cnpj_str_to_test)

        mock_cnpj_provider.get_cnpj_data.assert_called_once_with(cnpj_str_to_test)
        
        # A verificação de tipo também foi corrigida aqui
        assert isinstance(result_dict, dict)
        assert result_dict["cnpj"] == mock_provider_data["cnpj"]


@pytest.mark.asyncio
async def test_get_cnpj_data_provider_raises_exception():
    """Testa o repasse de exceção do provider pelo serviço."""
    mock_cnpj_provider = AsyncMock(spec=CNPJaProvider)
    mock_cnpj_provider.get_cnpj_data.side_effect = HTTPException(
        status_code=503, detail="Service unavailable from " \
        "provider"
    )

    with patch('aurora_platform.services.cnpj_service.CNPJaProvider', return_value=mock_cnpj_provider):
        cnpj_service = CNPJService()
        cnpj_to_test = "00000000000000"
        with pytest.raises(HTTPException) as excinfo:
            await cnpj_service.buscar_dados_cnpj(cnpj_to_test)
        
        assert excinfo.value.status_code == 503