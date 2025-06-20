# conftest.py
# Este arquivo é usado para configurar fixtures e plugins para o pytest.

import sys
import os
import pytest
from fastapi.testclient import TestClient

# --- CORREÇÃO CRUCIAL ---
# Adiciona o diretório 'src' ao início do path de busca do Python.
# Isso garante que `from aurora...` importe do nosso código-fonte, e não de
# qualquer outra biblioteca instalada que possa ter um nome parecido.
# Esta linha resolve os erros 'ModuleNotFoundError' e 'AttributeError'
# durante a coleta de testes.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
# -------------------------

# Agora que o path está correto, a importação do 'app' deve funcionar.
from aurora.main import app

# Fixture que cria um cliente de teste para a nossa aplicação.
# O escopo "session" significa que ele é criado apenas uma vez por sessão de teste.
@pytest.fixture(scope="session")
def client():
    """
    Cria e fornece uma instância do TestClient para a aplicação FastAPI.
    """
    with TestClient(app) as test_client:
        yield test_client

