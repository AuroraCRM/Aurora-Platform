# import pytest # Removido F401
from fastapi.testclient import TestClient
from sqlmodel import Session

# from aurora_platform.main import app  # Removido F401 - app é usado via fixture test_client
from aurora_platform.repositories.usuario_repository import (
    UsuarioRepository,
    UsuarioCreateRepo,
)
from aurora_platform.auth.security import get_password_hash
# from aurora_platform.models.usuario_model import Usuario # Removido F401

# from unittest.mock import patch  # Removido F401
# import os  # Removido F401

# Testes para o auth_router (fluxo de autenticação)


def test_login_for_access_token_success(
    test_client: TestClient, db_session: Session
):  # Mudado client para test_client, removido monkeypatch
    """Testa o login bem-sucedido e obtenção de token."""
    # O monkeypatch para settings agora está em environment_setup via conftest.py

    # Criar um usuário de teste diretamente no banco
    user_repo = UsuarioRepository(db_session)
    test_email = "login_success@example.com"
    test_password = "testpassword"
    hashed_password = get_password_hash(test_password)

    user_create_data = UsuarioCreateRepo(
        email=test_email,
        hashed_password=hashed_password,
        nome="Login Success User",
        is_active=True,
    )
    user_repo.create(user_create_data)

    # Tentar login
    login_data = {"username": test_email, "password": test_password}
    response = test_client.post(
        "/auth/token", data=login_data
    )  # Corrigido para test_client

    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    # TODO: Decodificar o token e verificar o 'sub' e 'type' se necessário,
    # mas isso já é testado unitariamente em test_security.py para create_access_token.


def test_login_for_access_token_incorrect_password(
    test_client: TestClient, db_session: Session
):  # Mudado client para test_client
    """Testa a falha de login com senha incorreta."""
    user_repo = UsuarioRepository(db_session)
    test_email = "wrong_pass@example.com"
    test_password = "correctpassword"
    hashed_password = get_password_hash(test_password)

    user_create_data = UsuarioCreateRepo(
        email=test_email,
        hashed_password=hashed_password,
        nome="Wrong Pass User",
        is_active=True,
    )
    user_repo.create(user_create_data)

    login_data = {"username": test_email, "password": "incorrectpassword"}
    response = test_client.post(
        "/auth/token", data=login_data
    )  # Corrigido para test_client

    assert response.status_code == 401  # Unauthorized
    response_data = response.json()
    assert response_data["detail"] == "Incorrect username or password"


def test_login_for_access_token_user_not_found(
    test_client: TestClient, db_session: Session
):  # Mudado client para test_client
    """Testa a falha de login com usuário não existente."""
    # Com db_session, a tabela usuarios será criada.
    login_data = {"username": "nonexistent@example.com", "password": "somepassword"}
    response = test_client.post(
        "/auth/token", data=login_data
    )  # Já estava test_client, correto

    assert response.status_code == 401  # Unauthorized
    response_data = response.json()
    assert (
        response_data["detail"] == "Incorrect username or password"
    )  # Mesma msg para user not found ou wrong pass


def test_login_for_access_token_inactive_user(
    test_client: TestClient, db_session: Session
):  # Mudado client para test_client
    """Testa a falha de login com usuário inativo."""
    user_repo = UsuarioRepository(db_session)
    test_email = "inactive@example.com"
    test_password = "inactivepassword"
    hashed_password = get_password_hash(test_password)

    user_create_data = UsuarioCreateRepo(
        email=test_email,
        hashed_password=hashed_password,
        nome="Inactive User",
        is_active=False,  # Usuário inativo
    )
    user_repo.create(user_create_data)

    login_data = {"username": test_email, "password": test_password}
    response = test_client.post(
        "/auth/token", data=login_data
    )  # Corrigido para test_client

    # Conforme security.py, authenticate_user retorna None para usuário inativo,
    # o que auth_router trata como "Incorrect username or password".
    # Uma alternativa seria security.py levantar uma exceção específica para usuário inativo.
    assert response.status_code == 401
    # Se get_current_user fosse chamado com token de user inativo, ele levantaria 400.
    # Mas aqui a autenticação falha antes.
    # assert response.json()["detail"] == "Inactive user" # Isso seria se authenticate_user levantasse HTTP 400
    assert response.json()["detail"] == "Incorrect username or password"


def test_read_users_me_unauthenticated(test_client: TestClient):
    """Testa o acesso ao endpoint /me sem autenticação."""
    response = test_client.get("/auth/me")
    assert response.status_code == 401  # Unauthorized
    assert response.json()["detail"] == "Not authenticated"


def test_read_users_me_authenticated(
    test_client: TestClient, db_session: Session
):  # Removido monkeypatch desnecessário
    """Testa o acesso ao endpoint /me com autenticação."""
    # monkeypatch para settings.get não é mais necessário aqui, environment_setup deve cuidar disso.

    user_repo = UsuarioRepository(db_session)
    test_email = "me_user@example.com"
    test_password = "mepassword"
    hashed_password = get_password_hash(test_password)

    user_create_data = UsuarioCreateRepo(
        email=test_email,
        hashed_password=hashed_password,
        nome="Me User",
        is_active=True,
    )
    created_user = user_repo.create(user_create_data)

    # Login para obter token
    login_data = {"username": test_email, "password": test_password}
    login_response = test_client.post(
        "/auth/token", data=login_data
    )  # Corrigido para test_client
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Acessar /me com o token
    headers = {"Authorization": f"Bearer {token}"}
    response = test_client.get(
        "/auth/me", headers=headers
    )  # Corrigido para test_client

    assert response.status_code == 200
    user_data = response.json()
    assert user_data["id"] == created_user.id
    assert user_data["email"] == test_email
    assert user_data["nome"] == "Me User"
    assert user_data["is_active"] is True
    assert "hashed_password" not in user_data  # Garantir que senha não é exposta


# TODO: Adicionar testes para os endpoints de 2FA se o escopo permitir.
# Envolveria mockar ou interagir com o TwoFactorAuth service.
# Ex: test_setup_2fa_request, test_enable_2fa_correct_code, test_enable_2fa_wrong_code, etc.
