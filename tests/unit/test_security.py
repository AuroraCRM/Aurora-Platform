import pytest # noqa: F401 - Pytest é necessário para rodar, mas pode não ser referenciado diretamente
from datetime import timedelta
from jose import jwt # Removido JWTError
from passlib.context import CryptContext

from aurora_platform.auth.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_secret_key,  # Necessário para decodificar token de teste
    get_algorithm,  # Necessário para decodificar token de teste
)

# get_current_user e authenticate_user são mais para testes de integração
# pois dependem de DB e UsuarioRepository.

# Configuração do contexto de senha para os testes, igual ao usado em security.py
pwd_context_test = CryptContext(schemes=["bcrypt"], deprecated="auto")


def test_verify_password():
    password = "testpassword"
    hashed_password = pwd_context_test.hash(password)
    assert verify_password(password, hashed_password) is True
    assert verify_password("wrongpassword", hashed_password) is False


def test_get_password_hash():
    password = "testpassword"
    hashed_password = get_password_hash(password)
    assert pwd_context_test.verify(password, hashed_password)


def test_create_access_token():
    data = {"sub": "testuser@example.com", "type": "access"}
    token = create_access_token(data)

    payload = jwt.decode(token, get_secret_key(), algorithms=[get_algorithm()])
    assert payload.get("sub") == "testuser@example.com"
    assert payload.get("type") == "access"
    assert "exp" in payload


def test_create_access_token_with_expiry():
    data = {"sub": "testuser@example.com", "type": "access"}
    expires_delta = timedelta(minutes=15)
    token = create_access_token(data, expires_delta=expires_delta)

    payload = jwt.decode(token, get_secret_key(), algorithms=[get_algorithm()])
    assert payload.get("sub") == "testuser@example.com"
    assert "exp" in payload


def test_create_access_token_default_type_if_not_provided():
    data = {"sub": "testuser_no_type@example.com"}  # Sem 'type'
    token = create_access_token(data)

    payload = jwt.decode(token, get_secret_key(), algorithms=[get_algorithm()])
    assert payload.get("sub") == "testuser_no_type@example.com"
    assert payload.get("type") == "access"  # Deve ser adicionado por padrão


# Não vamos testar get_current_user ou authenticate_user aqui pois eles
# requerem uma sessão de banco de dados e um repositório,
# tornando-os mais adequados para testes de integração.
# As funções acima são "puras" ou dependem apenas de settings.

# Poderíamos adicionar um teste para verificar o comportamento de brute-force
# se essa lógica estivesse ativa e testável unitariamente (sem DB/Redis real).
# Por ora, focamos nas funções puras de token e senha.
