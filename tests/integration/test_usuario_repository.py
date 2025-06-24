import pytest
from sqlmodel import Session
from fastapi import HTTPException  # Para testar exceções levantadas pelo repo

from aurora_platform.repositories.usuario_repository import (
    UsuarioRepository,
    UsuarioCreateRepo,
)
from aurora_platform.models.usuario_model import Usuario
from aurora_platform.auth.security import (
    get_password_hash,
)  # Para criar hashed_password

# Testes para UsuarioRepository


def test_create_usuario_success(db_session: Session):
    """Testa a criação bem-sucedida de um usuário."""
    repo = UsuarioRepository(db_session)

    hashed_password = get_password_hash("testpassword")
    user_data = UsuarioCreateRepo(
        email="testuser@example.com", hashed_password=hashed_password, nome="Test User"
    )

    db_user = repo.create(user_data)

    assert db_user.id is not None
    assert db_user.email == "testuser@example.com"
    assert db_user.nome == "Test User"
    assert db_user.hashed_password == hashed_password
    assert db_user.is_active is True

    # Verifica se o usuário foi realmente salvo no DB
    fetched_user = db_session.get(Usuario, db_user.id)
    assert fetched_user is not None
    assert fetched_user.email == "testuser@example.com"


def test_create_usuario_duplicate_email(db_session: Session):
    """Testa a falha ao criar usuário com email duplicado."""
    repo = UsuarioRepository(db_session)

    hashed_password = get_password_hash("testpassword1")
    user_data1 = UsuarioCreateRepo(
        email="duplicate@example.com", hashed_password=hashed_password, nome="User One"
    )
    repo.create(user_data1)  # Cria o primeiro usuário

    hashed_password2 = get_password_hash("testpassword2")
    user_data2 = UsuarioCreateRepo(
        email="duplicate@example.com",  # Mesmo email
        hashed_password=hashed_password2,
        nome="User Two",
    )

    with pytest.raises(HTTPException) as exc_info:
        repo.create(user_data2)

    assert exc_info.value.status_code == 409
    assert "já existe" in exc_info.value.detail.lower()


def test_get_usuario_by_email_found(db_session: Session):
    """Testa a busca de usuário por email quando encontrado."""
    repo = UsuarioRepository(db_session)

    email_to_find = "findme@example.com"
    hashed_password = get_password_hash("findpassword")
    user_data = UsuarioCreateRepo(
        email=email_to_find, hashed_password=hashed_password, nome="Find Me User"
    )
    created_user = repo.create(user_data)

    fetched_user = repo.get_by_email(email_to_find)

    assert fetched_user is not None
    assert fetched_user.id == created_user.id
    assert fetched_user.email == email_to_find


def test_get_usuario_by_email_not_found(db_session: Session):
    """Testa a busca de usuário por email quando não encontrado."""
    repo = UsuarioRepository(db_session)
    fetched_user = repo.get_by_email("nonexistent@example.com")
    assert fetched_user is None


def test_get_usuario_by_id_found(db_session: Session):
    """Testa a busca de usuário por ID quando encontrado."""
    repo = UsuarioRepository(db_session)

    hashed_password = get_password_hash("idpassword")
    user_data = UsuarioCreateRepo(
        email="iduser@example.com", hashed_password=hashed_password, nome="ID User"
    )
    created_user = repo.create(user_data)

    assert created_user.id is not None  # Garante que o ID foi atribuído
    fetched_user = repo.get_by_id(created_user.id)

    assert fetched_user is not None
    assert fetched_user.id == created_user.id
    assert fetched_user.email == "iduser@example.com"


def test_get_usuario_by_id_not_found(db_session: Session):
    """Testa a busca de usuário por ID quando não encontrado."""
    repo = UsuarioRepository(db_session)
    fetched_user = repo.get_by_id(99999)  # ID improvável de existir
    assert fetched_user is None
