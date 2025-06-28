import time
from datetime import timedelta
from typing import Dict, Optional # Removido Any

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session  # Alterado de sqlalchemy.orm para sqlmodel

from aurora_platform.config import settings
from aurora_platform.database import get_session as get_db
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
        expire = datetime.utcnow() + expires_delta
    else:
        expire_minutes = get_access_token_expire_minutes()
        expire = datetime.utcnow() + timedelta(minutes=expire_minutes)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Refresh tokens duram mais, por exemplo, 7 dias
        expire = datetime.utcnow() + timedelta(days=settings.get("REFRESH_TOKEN_EXPIRE_DAYS", 7))

    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def add_token_to_blacklist(token: str, expires_at: datetime):
    # Calcula o tempo de expiração em segundos
    now = datetime.utcnow()
    expires_in_seconds = int((expires_at - now).total_seconds())
    if expires_in_seconds > 0:
        set_cache(f"{BLACKLIST_PREFIX}{token}", "revoked", expires_in_seconds)

def is_token_blacklisted(token: str) -> bool:
    return redis_client.exists(f"{BLACKLIST_PREFIX}{token}")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> UsuarioModel:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if is_token_blacklisted(token):
        raise credentials_exception
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception

        token_type: Optional[str] = payload.get("type")
        if token_type != "access":
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user_repo = UsuarioRepository(db)
    user = user_repo.get_by_email(email=username)

    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return user

def verify_refresh_token(
    refresh_token: str, db: Session = Depends(get_db)
) -> UsuarioModel:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if is_token_blacklisted(refresh_token):
        raise credentials_exception
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception

        token_type: Optional[str] = payload.get("type")
        if token_type != "refresh":
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user_repo = UsuarioRepository(db)
    user = user_repo.get_by_email(email=username)

    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    # Verify if the refresh token matches the one stored in the database
    if not user.hashed_refresh_token or not verify_password(refresh_token, user.hashed_refresh_token):
        raise credentials_exception

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
