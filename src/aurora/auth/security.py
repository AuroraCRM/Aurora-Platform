# src/aurora/auth/security.py
import time
from datetime import timedelta
from typing import Dict, Any, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from aurora.config import settings
from aurora.database import get_db
from aurora.repositories.cliente_repository import ClienteRepository # Assumindo que o usuário é um 'Cliente'
from aurora.models.cliente_model import Cliente as ClienteModel

# --- Configurações de Segurança ---
# Lidas a partir do nosso sistema de configuração centralizado
SECRET_KEY = settings.get("SECRET_KEY", "uma-chave-secreta-padrao-deve-ser-trocada")
ALGORITHM = settings.get("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = settings.get("ACCESS_TOKEN_EXPIRE_MINUTES", 30)

# --- Configurações de Controle de Brute-Force ---
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_SECONDS = 300  # 5 minutos

# Contexto para hashing de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme para o FastAPI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Dicionários em memória para controle de brute-force (em produção, usar Redis)
failed_attempts: Dict[str, int] = {}
account_lockouts: Dict[str, float] = {}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha fornecida corresponde ao hash armazenado."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Gera o hash de uma senha."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Cria um novo token de acesso JWT."""
    to_encode = data.copy()
    if expires_delta:
        expire = time.time() + expires_delta.total_seconds()
    else:
        expire_minutes = ACCESS_TOKEN_EXPIRE_MINUTES
        expire = time.time() + (expire_minutes * 60)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> ClienteModel:
    """
    Decodifica o token JWT para obter o usuário atual.
    Esta é uma dependência do FastAPI que pode ser usada para proteger endpoints.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        token_type = payload.get("type")
        # CORREÇÃO (Falso Positivo): Adicionado '# nosec' para instruir o Bandit
        # a ignorar esta linha, pois 'access' é um tipo de token, não uma senha.
        if token_type != "access": # nosec B105
            raise credentials_exception

    except JWTError:
        raise credentials_exception
    
    user = ClienteRepository(db).get_by_email(email=username) # Busca o usuário pelo email (que é o 'sub')
    if user is None:
        raise credentials_exception
    return user

def authenticate_user(db: Session, username: str, password: str) -> Optional[ClienteModel]:
    """
    CORREÇÃO (Verdadeiro Positivo): Função refatorada para autenticar um usuário
    de forma segura contra o banco de dados, eliminando o placeholder com senha hardcoded.
    """
    repo = ClienteRepository(db)
    user = repo.get_by_email(email=username) # Ou get_by_username, se aplicável
    
    # Se o usuário não existe ou a senha não corresponde, retorna None
    if not user or not verify_password(password, user.hashed_password):
        return None
    
    # Retorna o objeto do usuário se a autenticação for bem-sucedida
    return user