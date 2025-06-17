# src/aurora/auth/security.py

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from jose import JWTError, jwt, ExpiredSignatureError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
import secrets
import logging
import re
import time

from aurora.config import settings

# Configuração de logging
logger = logging.getLogger(__name__)

# Configuração do contexto de criptografia para senhas
# Usando bcrypt com fator de custo 12 (recomendado para segurança)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

# Configuração do OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Armazenamento temporário de tokens revogados (em produção, use Redis)
revoked_tokens = {}

# Armazenamento temporário para proteção contra força bruta
failed_attempts = {}
account_lockouts = {}

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_at: datetime

class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = []
    jti: str  # JWT ID único

class UserCredentials(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha em texto plano corresponde ao hash.
    Implementa proteção contra timing attacks.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Gera um hash seguro para a senha usando bcrypt.
    """
    # Valida a força da senha antes de hash
    if not is_strong_password(password):
        raise ValueError("A senha não atende aos requisitos mínimos de segurança")
    
    return pwd_context.hash(password)

def is_strong_password(password: str) -> bool:
    """
    Verifica se a senha atende aos requisitos mínimos de segurança.
    - Pelo menos 10 caracteres
    - Pelo menos uma letra maiúscula
    - Pelo menos uma letra minúscula
    - Pelo menos um número
    - Pelo menos um caractere especial
    """
    if len(password) < 10:
        return False
    
    if not re.search(r'[A-Z]', password):
        return False
        
    if not re.search(r'[a-z]', password):
        return False
        
    if not re.search(r'[0-9]', password):
        return False
        
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
        
    return True

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Cria um token JWT seguro com os dados fornecidos.
    
    Args:
        data: Dados a serem codificados no token
        expires_delta: Tempo de expiração opcional
        
    Returns:
        str: Token JWT codificado
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Adiciona claims de segurança
    jti = secrets.token_hex(16)  # ID único do token para revogação
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "nbf": datetime.utcnow(),  # Not valid before
        "jti": jti,  # JWT ID
        "type": "access"
    })
    
    # Codifica o token usando o algoritmo especificado nas configurações
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt

def revoke_token(token: str) -> bool:
    """
    Revoga um token JWT.
    
    Args:
        token: Token JWT a ser revogado
        
    Returns:
        bool: True se o token foi revogado com sucesso
    """
    try:
        # Decodifica o token para obter o JTI e a expiração
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        jti = payload.get("jti")
        exp = payload.get("exp")
        
        if jti:
            # Armazena o JTI na lista de tokens revogados até sua expiração
            revoked_tokens[jti] = exp
            return True
    except Exception as e:
        logger.error(f"Erro ao revogar token: {str(e)}")
    
    return False

def clean_revoked_tokens() -> None:
    """Remove tokens expirados da lista de revogados."""
    current_time = datetime.utcnow().timestamp()
    to_remove = []
    
    for jti, exp in revoked_tokens.items():
        if exp < current_time:
            to_remove.append(jti)
    
    for jti in to_remove:
        revoked_tokens.pop(jti, None)

async def get_current_user(request: Request, token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Valida o token JWT e retorna os dados do usuário.
    Implementa verificações de segurança avançadas.
    
    Args:
        request: Objeto de requisição para verificações adicionais
        token: Token JWT a ser validado
        
    Returns:
        Dict: Dados do usuário
        
    Raises:
        HTTPException: Se o token for inválido, expirado ou revogado
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Limpa tokens revogados expirados
    clean_revoked_tokens()
    
    try:
        # Decodifica o token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        jti: str = payload.get("jti")
        if jti is None:
            raise credentials_exception
            
        # Verifica se o token foi revogado
        if jti in revoked_tokens:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token revogado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verifica o tipo de token
        token_type = payload.get("type")
        if token_type != "access":
            raise credentials_exception
        
        token_data = TokenData(
            username=username,
            scopes=payload.get("scopes", []),
            jti=jti
        )
        
        # Registra o acesso
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("User-Agent", "unknown")
        logger.info(f"Acesso autenticado: {username} de {client_ip} usando {user_agent}")
        
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise credentials_exception
    
    # Aqui você deve implementar a lógica para buscar o usuário no banco de dados
    # Por enquanto, retornamos apenas os dados do token
    return {
        "username": token_data.username, 
        "scopes": token_data.scopes,
        "jti": token_data.jti
    }

def check_permissions(required_scopes: List[str]):
    """
    Decorator para verificar as permissões do usuário.
    
    Args:
        required_scopes: Lista de escopos necessários para acessar o recurso
    """
    async def permission_checker(request: Request, current_user: Dict = Depends(get_current_user)):
        user_scopes = current_user.get("scopes", [])
        
        # Verifica cada escopo requerido
        missing_scopes = []
        for scope in required_scopes:
            if scope not in user_scopes:
                missing_scopes.append(scope)
        
        if missing_scopes:
            # Registra a tentativa de acesso não autorizado
            logger.warning(
                f"Tentativa de acesso não autorizado: {current_user.get('username')} "
                f"tentou acessar recurso que requer escopos {missing_scopes}"
            )
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permissão insuficiente. Escopos necessários: {', '.join(missing_scopes)}"
            )
            
        return current_user
    return permission_checker

async def authenticate_user(username: str, password: str) -> Dict[str, Any]:
    """
    Autentica um usuário e implementa proteção contra força bruta.
    
    Args:
        username: Nome de usuário
        password: Senha
        
    Returns:
        Dict: Dados do usuário autenticado
        
    Raises:
        HTTPException: Se as credenciais forem inválidas ou a conta estiver bloqueada
    """
    # Verifica se a conta está bloqueada
    if username in account_lockouts:
        lockout_time, attempts = account_lockouts[username]
        current_time = time.time()
        
        # Calcula o tempo de bloqueio baseado no número de tentativas
        # 5 min para 5 tentativas, 30 min para 10 tentativas, 24h para mais
        if attempts <= 5:
            lockout_duration = 5 * 60  # 5 minutos
        elif attempts <= 10:
            lockout_duration = 30 * 60  # 30 minutos
        else:
            lockout_duration = 24 * 60 * 60  # 24 horas
        
        # Verifica se o bloqueio ainda está ativo
        if current_time < lockout_time + lockout_duration:
            remaining = int((lockout_time + lockout_duration - current_time) / 60)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Conta temporariamente bloqueada. Tente novamente em {remaining} minutos."
            )
        else:
            # Remove o bloqueio se o tempo expirou
            del account_lockouts[username]
    
    # Aqui você deve implementar a lógica para buscar o usuário no banco de dados
    # e verificar a senha. Este é apenas um exemplo.
    
    # Simulação de verificação de senha (substitua por consulta ao banco)
    if username == "admin" and password == "Senha@Forte123":
        # Limpa tentativas de login falhas
        if username in failed_attempts:
            del failed_attempts[username]
        
        # Retorna os dados do usuário
        return {
            "username": username,
            "scopes": ["admin", "user"],
            "email": "admin@example.com"
        }
    
    # Registra tentativa de login falha
    if username not in failed_attempts:
        failed_attempts[username] = {"count": 1, "first_attempt": time.time()}
    else:
        failed_attempts[username]["count"] += 1
    
    # Verifica se deve bloquear a conta
    if failed_attempts[username]["count"] >= 5:
        account_lockouts[username] = (time.time(), failed_attempts[username]["count"])
        del failed_attempts[username]
        
        logger.warning(f"Conta bloqueada após múltiplas tentativas de login: {username}")
        
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Muitas tentativas de login. Conta temporariamente bloqueada."
        )
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )