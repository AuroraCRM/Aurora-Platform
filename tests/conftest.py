import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from aurora.config import settings
from aurora.database import Base, get_db
from aurora.main import app
from fastapi.testclient import TestClient

# Cria o engine do SQLAlchemy para testes
test_engine = create_engine(settings.TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="function")
def db():
    # Cria as tabelas no banco de dados de teste
    Base.metadata.create_all(bind=test_engine)
    
    # Cria uma sessão de teste
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        
    # Limpa as tabelas após o teste
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="function")
def client(db):
    # Sobrescreve a dependência get_db para usar o banco de dados de teste
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        yield client
    
    # Remove a sobrescrita após o teste
    app.dependency_overrides = {}