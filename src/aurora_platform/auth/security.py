import time
from datetime import timedelta
from typing import Dict, Optional # Removido Any

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session  # Alterado de sqlalchemy.orm para sqlmodel

from aurora_platform.config import settings
from aurora_platform.database import get_db  # get_db agora retorna sqlmodel.Session
from aurora_platform.repositories.usuario_repository import (
    UsuarioRepository,
)  # Novo repositório
from aurora_platform.models.usuario_model import Usuario as UsuarioModel  # Novo modelo

# --- Configurações de Segurança ---
SECRET_KEY = settings.get("SECRET_KEY", "uma-chave-secreta-padrao-deve-ser-trocada")
ALGORITHM = settings.get("ALGORITHM", "HS256")
# ACCESS_TOKEN_EXPIRE_MINUTES será acessado via função para garantir valor atualizado em testes
# ACCESS_TOKEN_EXPIRE_MINUTES_VALUE = settings.get("ACCESS_TOKEN_EXPIRE_MINUTES", 30)


def get_access_token_expire_minutes() -> int:
    return settings.get("ACCESS_TOKEN_EXPIRE_MINUTES", 30)


# --- Configurações de Controle de Brute-Force (manter se a lógica for usada) ---
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_SECONDS = 300

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/token"
)  # O tokenUrl pode precisar de ajuste se o endpoint de token mudar

# Dicionários em memória para controle de brute-force (idealmente usar Redis em produção)
failed_attempts: Dict[str, int] = {}
account_lockouts: Dict[str, float] = {}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = time.time() + expires_delta.total_seconds()
    else:
        expire_minutes = get_access_token_expire_minutes()  # Usar a função
        expire = time.time() + (expire_minutes * 60)

    to_encode.update({"exp": expire})
    # Garantir que 'type' está no payload, como esperado por get_current_user
    if "type" not in to_encode:
        to_encode["type"] = "access"  # Default para access token

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> UsuarioModel:  # Retorna UsuarioModel
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")  # username é o email do usuário
        if username is None:
            raise credentials_exception

        token_type: Optional[str] = payload.get("type")
        if token_type != "access":
            # Idealmente, logar tentativa de uso de token inválido
            raise credentials_exception

    except JWTError:
        # Idealmente, logar erro de decodificação
        raise credentials_exception

    # Usar UsuarioRepository para buscar o usuário
    user_repo = UsuarioRepository(db)
    user = user_repo.get_by_email(email=username)

    if user is None:
        raise credentials_exception
    if not user.is_active:  # Adicionada verificação se usuário está ativo
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return user


def authenticate_user(
    db: Session, username: str, password: str  # username aqui é o email
) -> Optional[UsuarioModel]:  # Retorna Optional[UsuarioModel]
    user_repo = UsuarioRepository(db)
    user = user_repo.get_by_email(email=username)

    if not user:
        return None
    if not user.is_active:  # Não autenticar usuários inativos
        return None
    if not verify_password(password, user.hashed_password):
        return None

    return user


# Funções de controle de brute-force (manter se usadas, adaptar para user.email ou user.id)
# def record_failed_attempt(username: str): ...
# def is_account_locked(username: str): ...
# Estas funções precisariam ser adaptadas se o brute-force for gerenciado aqui.
# Por simplicidade na refatoração, a lógica exata delas não foi alterada,
# mas o `username` deve ser o identificador único do usuário (ex: email).
