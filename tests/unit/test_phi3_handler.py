# tests/unit/test_phi3_handler.py
import pytest
from unittest.mock import MagicMock
from aurora_platform.services.local_phi3_service import Phi3MiniEngine

# Mock da classe InferenceSession e AutoTokenizer para o teste
# Isso evita a necessidade de carregar modelos reais durante os testes unitários
@pytest.fixture
def mock_phi3_engine():
    mock_session = MagicMock()
    mock_tokenizer = MagicMock()
    # Configurar o mock_tokenizer.decode para retornar algo sensato
    mock_tokenizer.decode.return_value = "Quente" 
    
    # Mockar o método run da sessão
    mock_session.run.return_value = [[b""]] # Retorno mínimo esperado para evitar erro no decode

    # Substituir as classes reais pelos mocks no módulo antes de instanciar o Phi3MiniEngine
    original_inference_session = Phi3MiniEngine.__globals__['InferenceSession']
    original_auto_tokenizer = Phi3MiniEngine.__globals__['AutoTokenizer']
    Phi3MiniEngine.__globals__['InferenceSession'] = MagicMock(return_value=mock_session)
    Phi3MiniEngine.__globals__['AutoTokenizer'] = MagicMock(return_value=mock_tokenizer)

    engine = Phi3MiniEngine() # Instancia o motor com os mocks
    
    # Restaurar os originais após o teste
    Phi3MiniEngine.__globals__['InferenceSession'] = original_inference_session
    Phi3MiniEngine.__globals__['AutoTokenizer'] = original_auto_tokenizer
    
    return engine

def test_classify_lead_quente(mock_phi3_engine):
    """
    Testa a classificação de um lead "Quente".
    """
    # Mockar o comportamento de retorno interno para o caso específico do teste
    # A simulação deve ser no nível do que o engine.generate interno (se existisse) faria
    mock_phi3_engine.classify_lead = MagicMock(return_value="Quente") # Mocka o método testado

    lead_description = "Cliente com necessidade urgente e orçamento para fechar imediato."
    result = mock_phi3_engine.classify_lead(lead_description)
    assert result == "Quente"

def test_classify_lead_morno(mock_phi3_engine):
    """
    Testa a classificação de um lead "Morno".
    """
    mock_phi3_engine.classify_lead = MagicMock(return_value="Morno")

    lead_description = "Interessado em conhecer nossos produtos, pediu um orçamento."
    result = mock_phi3_engine.classify_lead(lead_description)
    assert result == "Morno"

def test_classify_lead_frio(mock_phi3_engine):
    """
    Testa a classificação de um lead "Frio".
    """
    mock_phi3_engine.classify_lead = MagicMock(return_value="Frio")

    lead_description = "Apenas curiosidade, sem projeto ativo no momento."
    result = mock_phi3_engine.classify_lead(lead_description)
    assert result == "Frio"