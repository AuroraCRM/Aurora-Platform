import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from aurora_platform.main import app
from aurora_platform.database import get_session
from aurora_platform.models.usuario_model import Usuario
from aurora_platform.auth.security import get_password_hash, create_access_token, SECRET_KEY, ALGORITHM
from datetime import timedelta

# Setup a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def drop_db_and_tables():
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="session")
def session_fixture():
    create_db_and_tables()
    with Session(engine) as session:
        yield session
    drop_db_and_tables()

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.fixture
def test_user_data():
    return {
        "email": "testuser@example.com",
        "password": "TestPassword123",
        "nome": "Test User"
    }

@pytest.fixture
def create_test_user(session: Session, test_user_data: dict):
    hashed_password = get_password_hash(test_user_data["password"])
    user = Usuario(
        email=test_user_data["email"],
        hashed_password=hashed_password,
        nome=test_user_data["nome"],
        is_active=True
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def test_authenticate_user_success(client: TestClient, create_test_user: Usuario, test_user_data: dict):
    response = client.post(
        "/auth/token",
        data={"username": test_user_data["email"], "password": test_user_data["password"]}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()

def test_authenticate_user_invalid_password(client: TestClient, create_test_user: Usuario, test_user_data: dict):
    response = client.post(
        "/auth/token",
        data={"username": test_user_data["email"], "password": "WrongPassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

def test_authenticate_user_non_existent(client: TestClient):
    response = client.post(
        "/auth/token",
        data={"username": "nonexistent@example.com", "password": "AnyPassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

def test_get_current_user_success(client: TestClient, create_test_user: Usuario, test_user_data: dict):
    access_token_data = {"sub": test_user_data["email"], "type": "access"}
    access_token = create_access_token(access_token_data, expires_delta=timedelta(minutes=30))
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/auth/users/me", headers=headers) # Assuming /auth/users/me is a protected endpoint
    assert response.status_code == 200
    assert response.json()["email"] == test_user_data["email"]

def test_get_current_user_invalid_token(client: TestClient):
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/auth/users/me", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"

def test_get_current_user_expired_token(client: TestClient, create_test_user: Usuario, test_user_data: dict):
    access_token_data = {"sub": test_user_data["email"], "type": "access"}
    # Create an expired token
    expired_token = create_access_token(access_token_data, expires_delta=timedelta(minutes=-1))
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = client.get("/auth/users/me", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"

def test_get_current_user_wrong_token_type(client: TestClient, create_test_user: Usuario, test_user_data: dict):
    # Create a refresh token instead of an access token
    refresh_token_data = {"sub": test_user_data["email"], "type": "refresh"}
    refresh_token = create_access_token(refresh_token_data, expires_delta=timedelta(minutes=30))
    headers = {"Authorization": f"Bearer {refresh_token}"}
    response = client.get("/auth/users/me", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"
