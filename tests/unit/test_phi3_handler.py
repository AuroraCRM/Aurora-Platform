# tests/unit/test_phi3_handler.py
import pytest
from unittest.mock import MagicMock, patch
from aurora_platform.models.phi3_handler import Phi3Handler

# Mock da classe InferenceSession e AutoTokenizer para o teste
# Isso evita a necessidade de carregar modelos reais durante os testes unitários
@pytest.fixture
def mock_phi3_handler():
    # Retorna um MagicMock que se comporta como uma instância de Phi3Handler
    return MagicMock(spec=Phi3Handler)


def test_generate_response_quente(mock_phi3_handler):
    """
    Testa a geração de resposta "Quente".
    """
    mock_phi3_handler.generate_response.return_value = "Quente"

    lead_description = "Cliente com necessidade urgente e orçamento para fechar imediato."
    result = mock_phi3_handler.generate_response(lead_description)
    assert result == "Quente"

def test_generate_response_morno(mock_phi3_handler):
    """
    Testa a geração de resposta "Morno".
    """
    mock_phi3_handler.generate_response.return_value = "Morno"

    lead_description = "Interessado em conhecer nossos produtos, pediu um orçamento."
    result = mock_phi3_handler.generate_response(lead_description)
    assert result == "Morno"

def test_generate_response_frio(mock_phi3_handler):
    """
    Testa a geração de resposta "Frio".
    """
    mock_phi3_handler.generate_response.return_value = "Frio"

    lead_description = "Apenas curiosidade, sem projeto ativo no momento."
    result = mock_phi3_handler.generate_response(lead_description)
    assert result == "Frio"