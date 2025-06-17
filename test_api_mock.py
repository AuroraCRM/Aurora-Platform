import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

# Adiciona o diretório atual ao path para importação
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock para o SQLAlchemy engine e Base
@pytest.fixture
def mock_db():
    with patch('aurora.database_config.engine') as mock_engine, \
         patch('aurora.database_config.Base') as mock_base, \
         patch('aurora.database_config.get_db_session') as mock_session:
        
        # Configura o mock para não tentar conectar ao banco de dados
        mock_base.metadata.create_all = MagicMock()
        mock_session.return_value = MagicMock()
        
        yield

# Importa o app após configurar os mocks
@pytest.fixture
def client(mock_db):
    from main import app
    return TestClient(app)

def test_read_root(client):
    """Testa se a rota raiz está funcionando corretamente."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Bem-vindo à API do Aurora CRM"}