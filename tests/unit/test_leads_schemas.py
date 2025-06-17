# tests/unit/test_cliente_schemas.py

import pytest
from pydantic import ValidationError
from aurora.schemas.cliente_schemas import ClienteCreate

def test_create_cliente_schema_success():
    """Testa a criação de um schema ClienteCreate com dados válidos."""
    cliente_data = {
        "razao_social": "Empresa de Teste SA",
        "nome_fantasia": "Teste Fantasia",
        "cnpj": "12345678000195",
        "email": "contato@teste.com"
    }
    cliente_schema = ClienteCreate(**cliente_data)
    assert cliente_schema.razao_social == cliente_data["razao_social"]
    assert cliente_schema.cnpj == cliente_data["cnpj"]

def test_create_cliente_schema_missing_required_field():
    """Testa a criação sem um campo obrigatório (razao_social)."""
    cliente_data = {
        "cnpj": "12345678000195",
        "email": "contato@teste.com"
    }
    with pytest.raises(ValidationError):
        ClienteCreate(**cliente_data)
