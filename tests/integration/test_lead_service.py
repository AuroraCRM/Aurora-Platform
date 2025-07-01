import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException, status
from sqlmodel import Session  # Para tipo do db mockado

from aurora_platform.services.lead_service import LeadService
from aurora_platform.repositories.lead_repository import LeadRepository
from aurora_platform.models.lead_models import (
    LeadCreate,
    LeadUpdate,
    LeadDB,
    # LeadRead, # Removido F401
    StatusLead,
)


@pytest.fixture
def mock_lead_repo():
    return MagicMock(spec=LeadRepository)


@pytest.fixture
def lead_service(mock_lead_repo: MagicMock):
    # Similar ao ServicoCRM, o LeadService cria LeadRepository(db).
    # Mockamos o db para instanciar o serviço e depois substituímos o repo.
    service = LeadService(db=MagicMock(spec=Session))
    service.lead_repo = mock_lead_repo
    return service


# --- Testes para create_lead ---
def test_create_lead_success(lead_service: LeadService, mock_lead_repo: MagicMock):
    lead_data = LeadCreate(
        nome="Novo Lead", email="lead@exemplo.com", status=StatusLead.NOVO
    )
    # O repo.create espera LeadDB, o serviço converte LeadCreate para LeadDB
    # Aqui, vamos mockar o que o repo.create retorna
    mock_lead_db_return = LeadDB.model_validate(
        lead_data
    )  # Simula o objeto que o repo retornaria
    mock_lead_db_return.id = 1  # Simula ID atribuído pelo DB

    mock_lead_repo.create.return_value = mock_lead_db_return

    result = lead_service.create_lead(lead_data)

    # Verifica se o repo.create foi chamado (o argumento exato pode ser complexo de mockar se houver conversão interna)
    # Por isso, é mais fácil verificar se foi chamado e o resultado.
    mock_lead_repo.create.assert_called_once()
    # Se quiser verificar o argumento passado ao repo:
    # called_arg = mock_lead_repo.create.call_args[0][0]
    # assert called_arg.nome == lead_data.nome
    assert result.id == mock_lead_db_return.id
    assert result.nome == lead_data.nome
    assert result.email == lead_data.email


# --- Testes para get_lead_by_id ---
def test_get_lead_by_id_found(lead_service: LeadService, mock_lead_repo: MagicMock):
    mock_lead_db = LeadDB(
        id=1,
        nome="Lead Encontrado",
        email="found@example.com",
        status=StatusLead.QUALIFICADO,
    )
    mock_lead_repo.get_by_id.return_value = mock_lead_db

    result = lead_service.get_lead_by_id(1)

    mock_lead_repo.get_by_id.assert_called_once_with(1)
    assert result == mock_lead_db


def test_get_lead_by_id_not_found(lead_service: LeadService, mock_lead_repo: MagicMock):
    mock_lead_repo.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        lead_service.get_lead_by_id(99)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    mock_lead_repo.get_by_id.assert_called_once_with(99)


# --- Testes para update_lead ---
def test_update_lead_success(lead_service: LeadService, mock_lead_repo: MagicMock):
    lead_id = 1
    update_data = LeadUpdate(nome="Lead Atualizado", status=StatusLead.PROPOSTA)

    # Simular que o lead existe para ser atualizado
    existing_lead_db = LeadDB(
        id=lead_id,
        nome="Lead Antigo",
        email="update@example.com",
        status=StatusLead.QUALIFICADO,
    )
    mock_lead_repo.get_by_id.return_value = (
        existing_lead_db  # get_by_id é chamado primeiro no serviço
    )

    # Simular o retorno do repo.update
    # O repo.update deve receber LeadUpdate e retornar LeadDB atualizado
    # O serviço passa o lead_data (LeadUpdate) para o repo.
    updated_lead_db = LeadDB(
        id=lead_id,
        nome=update_data.nome if update_data.nome is not None else existing_lead_db.nome,
        email="update@example.com",
        status=update_data.status if update_data.status is not None else existing_lead_db.status,
    )
    mock_lead_repo.update.return_value = updated_lead_db

    result = lead_service.update_lead(lead_id, update_data)

    mock_lead_repo.get_by_id.assert_called_once_with(lead_id)
    mock_lead_repo.update.assert_called_once_with(
        lead_id=lead_id, lead_data=update_data
    )
    if update_data.nome is not None:
        assert result.nome == update_data.nome # type: ignore
    if update_data.status is not None:
        assert result.status == update_data.status # type: ignore


def test_update_lead_not_found(lead_service: LeadService, mock_lead_repo: MagicMock):
    lead_id = 99
    update_data = LeadUpdate(nome="Não Encontrado")

    mock_lead_repo.get_by_id.return_value = None  # Simula que o lead não existe

    with pytest.raises(HTTPException) as exc_info:
        lead_service.update_lead(lead_id, update_data)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    mock_lead_repo.get_by_id.assert_called_once_with(lead_id)
    mock_lead_repo.update.assert_not_called()


# --- Testes para delete_lead ---
def test_delete_lead_success(lead_service: LeadService, mock_lead_repo: MagicMock):
    lead_id = 1
    # Simular que o lead existe para ser deletado
    existing_lead_db = LeadDB(
        id=lead_id,
        nome="Lead para Deletar",
        email="delete@example.com",
        status=StatusLead.PERDIDO,
    )
    mock_lead_repo.get_by_id.return_value = existing_lead_db
    mock_lead_repo.delete.return_value = True  # Repo.delete retorna bool

    result = lead_service.delete_lead(lead_id)

    mock_lead_repo.get_by_id.assert_called_once_with(lead_id)
    mock_lead_repo.delete.assert_called_once_with(
        lead_id=lead_id
    )  # Corrigido para keyword argument
    assert result is True


def test_delete_lead_not_found(lead_service: LeadService, mock_lead_repo: MagicMock):
    lead_id = 99
    mock_lead_repo.get_by_id.return_value = None  # Simula que o lead não existe

    with pytest.raises(HTTPException) as exc_info:
        lead_service.delete_lead(lead_id)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    mock_lead_repo.get_by_id.assert_called_once_with(lead_id)
    mock_lead_repo.delete.assert_not_called()


# Adicionar testes para get_all_leads se necessário, similar a ServicoCRM.
# def test_get_all_leads(lead_service: LeadService, mock_lead_repo: MagicMock):
#     mock_leads_list = [
#         LeadDB(id=1, nome="Lead 1", email="l1@e.com", status=StatusLead.NOVO),
#         LeadDB(id=2, nome="Lead 2", email="l2@e.com", status=StatusLead.CONTATADO),
#     ]
#     mock_lead_repo.list_all.return_value = mock_leads_list

#     results = lead_service.get_all_leads(skip=0, limit=10)

#     mock_lead_repo.list_all.assert_called_once_with(skip=0, limit=10)
#     assert len(results) == 2
#     assert results == mock_leads_list
