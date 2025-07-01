import pytest
from starlette.testclient import TestClient
import os
from sqlmodel import create_engine, Session, SQLModel

# Importar todos os modelos para que SQLModel.metadata os conheça para create_all/drop_all
from aurora_platform.models.usuario_model import Usuario
from aurora_platform.models.cliente_model import Cliente
from aurora_platform.models.lead_models import LeadDB
from aurora_platform.models.ai_log_model import AIInteractionLog

# Adicionar outros modelos aqui se forem criados


@pytest.fixture(scope="function")
def environment_setup(monkeypatch):
    """
    Configura variáveis de ambiente de teste, recarrega settings do Dynaconf,
    e cria/destrói tabelas do banco de dados de teste usando a engine da aplicação.
    """
    monkeypatch.setenv("ENVIRONMENT", "test")
    # Usar um nome de arquivo de banco de dados específico para testes para evitar conflitos
    # e garantir que seja o mesmo usado pela app_engine.
    test_db_url = "sqlite:///./test_aurora_platform.db"
    monkeypatch.setenv("DATABASE_URL", test_db_url)

    monkeypatch.setenv(
        "REDIS_HOST", "mock_redis_host_for_tests"
    )  # Evita conexões reais
    monkeypatch.setenv("REDIS_PORT", "1234")

    monkeypatch.setenv(
        "AURORA_CNPJWS_PUBLIC_URL", "https://fake-cnpj-ws-for-tests.com/v1"
    ) # type: ignore

    monkeypatch.setenv("AURORA_SECRET_KEY", "test_secret_key_monkeypatched_for_tests")
    

    # Importar e recarregar settings DEPOIS que as monkeypatches de env foram aplicadas
    from aurora_platform.config import settings as app_settings

    app_settings.reload() # type: ignore
    app_settings.ALGORITHM = "HS256"
    app_settings.ACCESS_TOKEN_EXPIRE_MINUTES = 15

    # Verificar se a app_engine está usando a DATABASE_URL de teste
    # Isso é um pouco implícito, pois a engine em database.py é criada na importação.
    # Se database.py for importado ANTES desta fixture rodar e setar as env vars,
    # a app_engine pode ter a URL de produção/dev.
    # Para garantir, podemos recriar a engine da app aqui ou garantir que database.py
    # seja importado após as env vars serem setadas.
    # A ordem de execução das fixtures e importações de módulos é crucial.
    # A maneira mais segura é se a engine for criada dinamicamente ou puder ser reconfigurada.
    # No nosso caso, `aurora_platform.database.engine` é definida no nível do módulo.
    # O `app_settings.reload()` deve fazer o Dynaconf atualizar os valores que `database.py` usará
    # na próxima vez que `settings.DATABASE_URL` for acessado.
    # Contudo, a `engine` em `database.py` já foi criada com o valor antigo.
    # Precisamos forçar a recriação da engine da aplicação ou usar uma engine de teste separada
    # que é garantidamente criada com a URL de teste.

    # Solução: Criar uma engine de teste aqui e usá-la para tudo nos testes.
    # A aplicação real usará sua própria engine. Para TestClient, isso pode ser um problema
    # se ele não usar esta engine_test.
    # TestClient(app) usará a engine da `app`.
    # Então, precisamos garantir que a `app_engine` reflita as monkeypatches.
    # Uma forma é fazer `aurora_platform.database.engine = create_engine(test_db_url)`
    # Mas isso é um "monkeypatch" na própria engine da app.

    # Abordagem mais limpa para TestClient:
    # Fazer a `app` ser criada dentro de uma fixture que configura o ambiente.
    # Por agora, vamos confiar que o reload de settings e a subsequente importação da app
    # pelo TestClient fará com que a engine da app use a URL correta.
    # E para a fixture db_session, usaremos a app_engine.

    # Criar uma engine de teste local para esta fixture
    test_engine = create_engine(test_db_url)
    SQLModel.metadata.drop_all(bind=test_engine)  # Limpar de execuções anteriores
    SQLModel.metadata.create_all(bind=test_engine)

    yield test_engine  # Passar a engine de teste para as fixtures que a utilizam

    # Limpar tabelas após os testes da função
    SQLModel.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def test_client(db_session):
    """
    Cria uma instância do TestClient. Depende de db_session
    para garantir que as variáveis de ambiente e o schema do BD estejam configurados.
    """
    # Importar app aqui para garantir que as settings já foram carregadas
    from aurora_platform.main import app
    from aurora_platform.database import get_session

    # Override the get_session dependency to use the test database session
    def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as client_instance:
        yield client_instance

    # Clear the dependency override after the test
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def db_session(environment_setup):
    """
    Fornece uma sessão de banco de dados de teste usando a engine criada em environment_setup.
    As tabelas já foram criadas/limpas por environment_setup.
    """
    test_engine = environment_setup # environment_setup agora retorna a test_engine
    with Session(test_engine) as session:
        yield session
    # A limpeza é feita em environment_setup
