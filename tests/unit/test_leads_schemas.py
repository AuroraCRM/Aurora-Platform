import pytest
from pydantic import ValidationError  # SQLModel usa ValidationError de Pydantic
from datetime import datetime

from aurora_platform.models.lead_models import (
    LeadCreate,
    LeadRead,
    LeadUpdate,
    StatusLead,
    # Lead,  # Removido F401
)


# Testes para LeadCreate
def test_lead_create_schema_success():
    """Testa a criação de um schema LeadCreate com dados válidos."""
    lead_data = {
        "nome": "John Doe Lead",
        "email": "john.lead@example.com",
        "telefone": "11999998888",
        "empresa": "Doe Inc.",
        "cargo": "Analista",
        "origem": "Website",
        "interesse": "Produto X",
        "status": StatusLead.NOVO,
    }
    schema = LeadCreate(**lead_data)
    assert schema.nome == lead_data["nome"]
    assert schema.email == lead_data["email"]
    assert schema.status == StatusLead.NOVO


def test_lead_create_schema_missing_required_fields():
    """Testa LeadCreate sem campos obrigatórios (nome, email)."""
    # Falta nome
    with pytest.raises(ValidationError):
        LeadCreate(email="incomplete@example.com")
    # Falta email
    with pytest.raises(ValidationError):
        LeadCreate(nome="Incomplete Lead")


def test_lead_create_schema_invalid_email():
    """Testa LeadCreate com email inválido."""
    lead_data = {"nome": "Bad Email", "email": "not-an-email", "status": StatusLead.NOVO}
    with pytest.raises(
        ValidationError
    ):  # Pydantic/SQLModel valida EmailStr implicitamente se o tipo for EmailStr
        LeadCreate(**lead_data)


# Testes para LeadRead (simples, mais para garantir que pode ser instanciado)
def test_lead_read_schema():
    """Testa a criação de um schema LeadRead."""
    # LeadRead herda de Lead e adiciona id, data_criacao, data_atualizacao
    # Estes campos seriam preenchidos ao ler do banco de dados.
    read_data = {
        "id": 1,
        "nome": "Jane Read",
        "email": "jane.read@example.com",
        "status": StatusLead.QUALIFICADO,
        "data_criacao": datetime.now(),
        "data_atualizacao": datetime.now(),
    }
    schema = LeadRead(**read_data)
    assert schema.id == read_data["id"]
    assert schema.nome == read_data["nome"]
    assert schema.status == StatusLead.QUALIFICADO


# Testes para LeadUpdate (todos os campos são opcionais)
def test_lead_update_schema_partial_data():
    """Testa LeadUpdate com dados parciais."""
    update_data = {"nome": "Updated Name"}
    schema = LeadUpdate(**update_data)
    assert schema.nome == "Updated Name"
    assert schema.email is None  # Outros campos devem ser None se não fornecidos


def test_lead_update_schema_empty_data():
    """Testa LeadUpdate com dados vazios (ainda válido)."""
    schema = LeadUpdate()
    assert schema.model_dump(exclude_unset=True) == {}


def test_lead_update_with_status():
    update_data = {"status": StatusLead.GANHO}
    schema = LeadUpdate(**update_data)
    assert schema.status == StatusLead.GANHO
