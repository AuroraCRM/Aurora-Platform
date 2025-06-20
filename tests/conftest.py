import pytest
from starlette.testclient import TestClient
from src.aurora.main import app
import os

@pytest.fixture(scope="session", autouse=True)
def set_test_environment():
    """
    Fixture para garantir que as variáveis de ambiente de TESTE sejam definidas
    antes que a aplicação e suas dependências (como a classe Settings) sejam importadas.
    O escopo é de 'session' e 'autouse=True' para que execute uma única vez no início
    de toda a suíte de testes.
    """
    os.environ['ENVIRONMENT'] = 'test'
    os.environ['DATABASE_URL'] = 'sqlite:///./test.db'
    os.environ['REDIS_HOST'] = 'localhost'
    os.environ['REDIS_PORT'] = '6379'
    os.environ['CNPJA_API_URL'] = 'https://fake-cnpja-api.com'
    os.environ['CNPJA_API_KEY'] = 'fake_api_key_for_testing'
    os.environ['JWT_SECRET_KEY'] = 'a_very_secret_key_for_tests'
    os.environ['JWT_ALGORITHM'] = 'HS256'

@pytest.fixture()
def client(set_test_environment):
    """
    Fixture para criar um cliente de teste para a aplicação FastAPI.
    Depende explicitamente de 'set_test_environment' para garantir a ordem de execução.
    """
    with TestClient(app) as c:
        yield c