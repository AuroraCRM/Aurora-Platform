# Versão Final Corrigida para: tests/integration/test_cliente_service.py

import pytest
from unittest.mock import MagicMock, AsyncMock
from sqlmodel import Session
from typing import Sequence

from aurora_platform.services.servico_crm import ServicoCRM
from aurora_platform.repositories.cliente_repository import ClienteRepository
from aurora_platform.schemas.cliente_schemas import ClienteCreate
from aurora_platform.utils.exceptions import CRMServiceError

# AURORA: Esta é a importação correta e robusta que resolve o erro.
# Ela importa a classe 'Cliente' do nosso pacote de modelos e a renomeia para 'ClienteModel'
# para evitar conflitos de nome com os schemas.
from aurora_platform.models import Cliente as ClienteModel

# Fixture para o mock do repositório
@pytest.fixture
def mock_cliente_repo() -> MagicMock:
    return MagicMock(spec=ClienteRepository)

# Fixture para o mock do provedor de CNPJ (agora assíncrono)
@pytest.fixture
def mock_cnpj_provider() -> AsyncMock:
    return AsyncMock()

# Fixture para o serviço, injetando os mocks
@pytest.fixture
def cliente_service(mock_cliente_repo: MagicMock, mock_cnpj_provider: AsyncMock) -> ServicoCRM:
    mock_db_session = MagicMock(spec=Session)
    service = ServicoCRM(db=mock_db_session)
    service.repo = mock_cliente_repo
    service.cnpj_service = mock_cnpj_provider
    return service

# --- Testes Refatorados ---

def test_get_all_clientes(cliente_service: ServicoCRM, mock_cliente_repo: MagicMock):
    """
    Testa se o serviço chama corretamente o método get_all do repositório.
    """
    mock_cliente_repo.get_all.return_value = [
        ClienteModel(id=1, razao_social="Cliente A", cnpj="11111111000111"),
        ClienteModel(id=2, razao_social="Cliente B", cnpj="22222222000122"),
    ]

    result: Sequence[ClienteModel] = cliente_service.get_all_clientes()

    mock_cliente_repo.get_all.assert_called_once()
    assert len(list(result)) == 2
    assert list(result)[0].razao_social == "Cliente A"


def test_create_cliente(cliente_service: ServicoCRM, mock_cliente_repo: MagicMock):
    """
    Testa a criação de um cliente simples.
    """
    cliente_data = ClienteCreate(razao_social="Novo Cliente", cnpj="12345678000195")
    mock_created_cliente = ClienteModel(id=3, **cliente_data.model_dump())
    
    mock_cliente_repo.create.return_value = mock_created_cliente

    result = cliente_service.create_cliente(cliente_data)

    mock_cliente_repo.create.assert_called_once_with(cliente_data)
    assert result.id == 3
    assert result.razao_social == "Novo Cliente"


# TODO: Decidir se a funcionalidade de deleção deve ser exposta através do serviço.
# Se sim, adicionar o método 'delete_cliente' no ServicoCRM e reativar os testes abaixo.