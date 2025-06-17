# conftest.py - Versão Final, Corrigida e com Boas Práticas

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Importações da nossa aplicação
from aurora.main import app
from aurora.config import settings  # Importa a configuração centralizada que lê o .env
from aurora.database_config import Base, get_db_session

# --- 1. Configuração do Engine de Teste ---
# O engine agora é criado usando a URL do banco de dados de TESTE
# que vem do nosso arquivo de config central (que por sua vez lê o .env).
engine = create_engine(settings.TEST_DATABASE_URL)

# Cria uma fábrica de sessões específica para os testes
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# --- 2. Setup e Teardown da Suíte de Testes ---
# Estas linhas são executadas uma vez quando o pytest inicia.
# Elas garantem que o banco de dados de teste esteja sempre limpo e
# na versão mais recente dos seus modelos antes de os testes começarem.
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


# --- 3. Fixture para a Sessão de Banco de Dados de Teste (Isolamento) ---
@pytest.fixture(scope="function")
def db_session_test():
    """
    Cria uma nova sessão de banco de dados para CADA teste dentro de uma transação
    e desfaz (rollback) a transação ao final, garantindo 100% de isolamento
    entre os testes. Um teste não verá os dados criados por outro.
    """
    connection = engine.connect()
    transaction = connection.begin()
    db = TestingSessionLocal(bind=connection)

    try:
        yield db
    finally:
        db.close()
        transaction.rollback()
        connection.close()


# --- 4. Fixture para o Cliente de API de Teste (Injeção de Dependência) ---
@pytest.fixture(scope="function")
def client(db_session_test):
    """
    Cria um TestClient que usa a sessão de banco de dados de teste isolada.
    Este é o ponto chave que conecta nossos testes à sessão de DB isolada.
    """
    def override_get_db():
        """
        Esta função substitui a dependência 'get_db_session' original da aplicação.
        """
        try:
            yield db_session_test
        finally:
            db_session_test.close()

    # Aplica o override: toda vez que um endpoint pedir a dependência get_db_session,
    # o FastAPI irá, na verdade, executar a função override_get_db.
    app.dependency_overrides[get_db_session] = override_get_db
    
    yield TestClient(app)
    
    # Limpa o override após o teste para não afetar outros contextos
    del app.dependency_overrides[get_db_session]