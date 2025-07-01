from datetime import timedelta, datetime, timezone
from typing import Dict, Optional, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

# AURORA: Correção 1 - Importando 'LazySettings' para a correta anotação de tipo do Dynaconf.
from dynaconf import LazySettings

from aurora_platform.config import settings
from aurora_platform.database import get_session as get_db
from aurora_platform.repositories import UsuarioRepository
# AURORA: Correção 2 - Usando a importação a nível de pacote que já corrigimos.
from aurora_platform.models import Usuario as UsuarioModel

# --- Configurações de Segurança ---

# AURORA: Adicionada a anotação de tipo correta para o objeto settings do Dynaconf.
# settings: LazySettings = settings  # Removido para evitar problemas de tipo

# Acesso direto aos atributos, como na sua versão que funcionava.
SECRET_KEY: str = str(settings.SECRET_KEY)
ALGORITHM: str = str(settings.ALGORITHM)
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(settings.ACCESS_TOKEN_EXPIRE_MINUTES)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# --- Funções de Criptografia e JWT ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if "type" not in to_encode:
        to_encode["type"] = "access"
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: Dict[str, Any]) -> str:
    to_encode = data.copy()
    expires = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"exp": expires})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- Dependências e Autenticação ---
# (O restante das funções como get_current_user, authenticate_user, etc. permanecem como na última versão funcional)

def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> UsuarioModel:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_type: Optional[str] = payload.get("type")
        if token_type != "access":
            raise credentials_exception
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user_repo = UsuarioRepository(db)
    user = user_repo.get_by_email(email=username)

    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return user

def get_current_active_user(
    current_user: UsuarioModel = Depends(get_current_user),
) -> UsuarioModel:
    return current_user

def get_user_from_refresh_token(refresh_token: str, db: Session) -> UsuarioModel:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
    )
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user_repo = UsuarioRepository(db)
    user = user_repo.get_by_email(email=username)

    if user is None or not user.is_active:
        raise credentials_exception
    
    return user

def authenticate_user(
    db: Session, username: str, password: str
) -> Optional[UsuarioModel]:
    user_repo = UsuarioRepository(db)
    user = user_repo.get_by_email(email=username)

    if not user:
        return None
    if not user.is_active:
        return None
    if not verify_password(password, user.hashed_password):
        return None

    return user

# --- Funções auxiliares para testes ---

def get_secret_key() -> str:
    return SECRET_KEY

def get_algorithm() -> str:
    return ALGORITHM