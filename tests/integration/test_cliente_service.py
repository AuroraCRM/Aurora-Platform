import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, status
from sqlmodel import Session  # Necessário para o tipo do db mockado

from aurora_platform.services.servico_crm import ServicoCRM
from aurora_platform.repositories.cliente_repository import ClienteRepository
from aurora_platform.integrations.cnpj_provider import CNPJaProvider
from aurora_platform.schemas.cliente_schemas import ClienteCreate # Removido ClienteUpdate
from aurora_platform.models.cliente_model import Cliente
from aurora_platform.utils.exceptions import CRMServiceError

# Mock para simular a sessão do banco de dados, se necessário para instanciar o repo
# No entanto, vamos mockar o repositório diretamente.
# mock_db_session = MagicMock(spec=Session)


@pytest.fixture
def mock_cliente_repo():
    return MagicMock(spec=ClienteRepository)


@pytest.fixture
def mock_cnpj_provider():
    return AsyncMock(spec=CNPJaProvider)


@pytest.fixture
def cliente_service(mock_cliente_repo, mock_cnpj_provider):
    # Para instanciar ServicoCRM, precisamos de uma 'db_session' para ClienteRepository.
    # Como estamos mockando ClienteRepository, podemos passar None ou um mock simples para db.
    # Ou, melhor ainda, se ServicoCRM aceita o repo como argumento (melhor para testar).
    # A implementação atual de ServicoCRM cria ClienteRepository(db).
    # Então, mockamos a 'db' que o ServicoCRM usa para criar o repo.

    # Simular o Depends(get_db) para o serviço
    # Aqui, o mais simples é passar o mock_cliente_repo diretamente se pudéssemos alterar ServicoCRM
    # Mas como não podemos, vamos mockar o que o ServicoCRM usa.
    # ServicoCRM(db=mock_db_session, cnpj_provider=mock_cnpj_provider)
    # E depois mockar ClienteRepository para ser retornado quando ServicoCRM o instancia.
    # Isso é mais complicado.

    # Abordagem mais simples: Assumir que podemos injetar mocks no construtor do serviço
    # ou que o teste pode controlar a criação do repositório.
    # Para este exemplo, vamos mockar o repositório que o serviço usaria.
    # Este teste foca na lógica do SERVIÇO, não na criação do repositório.

    # Se ServicoCRM.__init__ fosse: def __init__(self, cliente_repo, cnpj_provider):
    # service = ServicoCRM(cliente_repo=mock_cliente_repo, cnpj_provider=mock_cnpj_provider)
    # else:
    # Precisamos mockar a instância do ClienteRepository criada dentro do ServicoCRM
    # Isso pode ser feito com patch no construtor do ServicoCRM ou patch('ServicoCRM.ClienteRepository')

    # Para simplificar, vamos assumir que podemos injetar o repo mockado.
    # Se a injeção de dependência do FastAPI for estritamente seguida,
    # o teste precisaria de um override_dependency.
    # Por agora, instanciamos com mocks.

    service = ServicoCRM(
        db=MagicMock(spec=Session), cnpj_provider=mock_cnpj_provider
    )  # db mockada
    service.cliente_repo = mock_cliente_repo  # Substitui o repo interno pelo nosso mock
    return service


# --- Testes para create_cliente ---
def test_create_cliente_success(
    cliente_service: ServicoCRM, mock_cliente_repo: MagicMock
):
    cliente_data = ClienteCreate(
        razao_social="Teste SA", cnpj="12345678000100", email="teste@sa.com"
    )
    mock_cliente_db = Cliente.model_validate(cliente_data)  # O que o repo retornaria

    mock_cliente_repo.get_by_cnpj.return_value = None  # Simula que CNPJ não existe
    mock_cliente_repo.create.return_value = mock_cliente_db

    result = cliente_service.create_cliente(cliente_data)

    mock_cliente_repo.get_by_cnpj.assert_called_once_with(cnpj="12345678000100")
    mock_cliente_repo.create.assert_called_once_with(cliente_data)
    assert result == mock_cliente_db


def test_create_cliente_cnpj_exists(
    cliente_service: ServicoCRM, mock_cliente_repo: MagicMock
):
    cliente_data = ClienteCreate(
        razao_social="Teste SA", cnpj="12345678000100", email="teste@sa.com"
    )
    mock_cliente_repo.get_by_cnpj.return_value = Cliente.model_validate(
        cliente_data
    )  # Simula que CNPJ já existe

    with pytest.raises(HTTPException) as exc_info:
        cliente_service.create_cliente(cliente_data)

    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    mock_cliente_repo.get_by_cnpj.assert_called_once_with(cnpj="12345678000100")
    mock_cliente_repo.create.assert_not_called()


# --- Testes para get_cliente_by_id ---
def test_get_cliente_by_id_found(
    cliente_service: ServicoCRM, mock_cliente_repo: MagicMock
):
    mock_cliente_db = Cliente(id=1, razao_social="Teste", cnpj="111")
    mock_cliente_repo.get_by_id.return_value = mock_cliente_db

    result = cliente_service.get_cliente_by_id(1)

    mock_cliente_repo.get_by_id.assert_called_once_with(1)
    assert result == mock_cliente_db


def test_get_cliente_by_id_not_found(
    cliente_service: ServicoCRM, mock_cliente_repo: MagicMock
):
    mock_cliente_repo.get_by_id.return_value = None

    with pytest.raises(
        CRMServiceError
    ) as exc_info:  # ServicoCRM levanta CRMServiceError
        cliente_service.get_cliente_by_id(99)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    mock_cliente_repo.get_by_id.assert_called_once_with(99)


# --- Testes para create_cliente_from_cnpj (simplificado, foca na lógica do serviço) ---
@pytest.mark.asyncio
async def test_create_cliente_from_cnpj_success(
    cliente_service: ServicoCRM,
    mock_cliente_repo: MagicMock,
    mock_cnpj_provider: AsyncMock,
):
    cnpj_to_test = "12345678000100"
    normalized_cnpj = "12345678000100"

    mock_provider_data = {
        "razao_social": "Empresa CNPJ",
        "cnpj": normalized_cnpj,
        "email": "cnpj@empresa.com",
    }
    mock_cliente_schema = ClienteCreate(**mock_provider_data)
    mock_created_cliente = Cliente.model_validate(mock_cliente_schema)

    mock_cliente_repo.get_by_cnpj.return_value = None  # CNPJ não existe
    mock_cnpj_provider.get_cnpj_data.return_value = (mock_provider_data, "gratuita")
    mock_cliente_repo.create.return_value = mock_created_cliente

    # Mock _normalizar_dados_cnpj para simplificar, já que sua lógica é de mapeamento
    with patch.object(
        cliente_service, "_normalizar_dados_cnpj", return_value=mock_provider_data
    ) as mock_normalize:
        result = await cliente_service.create_cliente_from_cnpj(cnpj_to_test)

        mock_cliente_repo.get_by_cnpj.assert_called_once_with(cnpj=normalized_cnpj)
        mock_cnpj_provider.get_cnpj_data.assert_called_once_with(normalized_cnpj)
        mock_normalize.assert_called_once_with(mock_provider_data, "gratuita")
        mock_cliente_repo.create.assert_called_once()  # Verificar o argumento exato pode ser mais complexo
        assert result == mock_created_cliente


# Adicionar mais testes para update_cliente, delete_cliente, get_all_clientes
# seguindo o mesmo padrão de mockar o repositório e testar a lógica do serviço.
# Exemplo para delete_cliente:
def test_delete_cliente_success(
    cliente_service: ServicoCRM, mock_cliente_repo: MagicMock
):
    mock_cliente_repo.delete.return_value = True

    result = cliente_service.delete_cliente(1)

    mock_cliente_repo.delete.assert_called_once_with(1)
    assert result is True


def test_delete_cliente_not_found(
    cliente_service: ServicoCRM, mock_cliente_repo: MagicMock
):
    mock_cliente_repo.delete.return_value = False

    with pytest.raises(CRMServiceError) as exc_info:
        cliente_service.delete_cliente(99)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    mock_cliente_repo.delete.assert_called_once_with(99)
