# fix_tests.py
import os
import pathlib

# --- 1. Definição das Correções ---

# Dicionário de renomeações de métodos
# Chave: nome antigo (errado), Valor: nome novo (correto)
METHOD_RENAMES = {
    "create_cliente_from_cnpj": "criar_cliente_por_cnpj",
    "get_cliente_by_id": "buscar_cliente_por_id",
    "get_all_clientes": "buscar_todos_os_clientes",
    "update_cliente": "atualizar_cliente",
    "delete_cliente": "deletar_cliente",
    # Adicione outros mapeamentos se necessário
}

# Conteúdo correto para o pytest.ini
PYTEST_INI_CONTENT = """
[pytest]
pythonpath = . src
"""

# Conteúdo correto para o tests/conftest.py
CONFTEST_PY_CONTENT = """
# tests/conftest.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator

from aurora.main import app
from aurora.database_config import Base
from aurora.database import get_db_session
from aurora.config import Settings

# Usa um banco de dados SQLite em memória para os testes serem rápidos e isolados
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    \"\"\"Cria as tabelas no banco de dados de teste antes de os testes começarem.\"\"\"
    Base.metadata.create_all(bind=engine)
    yield

@pytest.fixture(scope="function")
def db_session() -> Generator:
    \"\"\"
    Cria uma sessão de banco de dados para cada teste, garantindo que
    a transação seja revertida ao final para manter os testes isolados.
    \"\"\"
    connection = engine.connect()
    transaction = connection.begin()
    db = TestingSessionLocal(bind=connection)
    try:
        yield db
    finally:
        db.close()
        transaction.rollback()
        connection.close()

@pytest.fixture(scope="module")
def client(db_session) -> Generator:
    \"\"\"
    Cria um cliente de API para os testes, usando o banco de dados de teste.
    \"\"\"
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db_session] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture(scope="session")
def test_settings() -> Settings:
    \"\"\"
    Carrega as configurações do arquivo .env para os testes.
    Isso resolve os erros de AttributeError (DATABASE_URL, CNPJA_API_URL, etc).
    \"\"\"
    return Settings()
"""

# --- 2. Lógica do Script ---

def fix_method_names_in_tests(tests_dir="tests"):
    """Varre a pasta de testes e aplica as renomeações de métodos."""
    print("--- Iniciando renomeação de métodos nos testes ---")
    tests_path = pathlib.Path(tests_dir)
    if not tests_path.is_dir():
        print(f"AVISO: Diretório de testes '{tests_dir}' não encontrado.")
        return

    for filepath in tests_path.glob("**/*_test.py"):
        print(f"Analisando arquivo: {filepath}")
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content
        for old_name, new_name in METHOD_RENAMES.items():
            content = content.replace(f".{old_name}", f".{new_name}")

        if content != original_content:
            print(f"  -> Modificações aplicadas em {filepath}")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
    print("--- Renomeação de métodos concluída ---\n")

def create_or_update_config_files():
    """Cria ou sobrescreve os arquivos de configuração de teste."""
    print("--- Criando/Atualizando arquivos de configuração ---")

    # Criar pytest.ini
    with open("pytest.ini", "w", encoding="utf-8") as f:
        f.write(PYTEST_INI_CONTENT.strip())
    print("  -> Arquivo 'pytest.ini' criado/atualizado.")

    # Garantir que o diretório tests exista
    os.makedirs("tests", exist_ok=True)

    # Criar tests/conftest.py
    with open("tests/conftest.py", "w", encoding="utf-8") as f:
        f.write(CONFTEST_PY_CONTENT.strip())
    print("  -> Arquivo 'tests/conftest.py' criado/atualizado.")
    print("--- Configuração concluída ---\n")


if __name__ == "__main__":
    print("Iniciando script de correção massiva do ambiente de testes da Aurora...")
    create_or_update_config_files()
    fix_method_names_in_tests()
    print("Script finalizado. Por favor, revise as alterações e execute 'pip install -r requirements.txt' se necessário.")