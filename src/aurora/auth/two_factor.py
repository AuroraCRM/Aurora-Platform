# src/aurora/auth/two_factor.py

import pyotp
import qrcode
import io
import base64
import secrets
import time
from typing import Dict, Optional, Tuple
from fastapi import HTTPException, status, Depends, Request
from pydantic import BaseModel
import logging

from aurora.config import settings
from aurora.auth.security import get_current_user

logger = logging.getLogger(__name__)

# Armazenamento temporário para segredos 2FA (em produção, use banco de dados)
user_2fa_secrets = {}
user_backup_codes = {}
user_2fa_enabled = {}

class TwoFactorSetup(BaseModel):
    """Modelo para configuração inicial de 2FA."""
    secret: str
    qr_code: str
    backup_codes: list[str]

class TwoFactorVerify(BaseModel):
    """Modelo para verificação de código 2FA."""
    code: str

def generate_secret() -> str:
    """Gera um segredo para TOTP."""
    return pyotp.random_base32()

def generate_backup_codes(count: int = 10) -> list[str]:
    """Gera códigos de backup para 2FA."""
    return [secrets.token_hex(4).upper() for _ in range(count)]

def generate_qr_code(secret: str, username: str) -> str:
    """
    Gera um código QR para configuração de 2FA.
    
    Args:
        secret: Segredo TOTP
        username: Nome do usuário
        
    Returns:
        str: Imagem do código QR em base64
    """
    # Cria o URI TOTP
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(
        name=username,
        issuer_name="Aurora Platform"
    )
    
    # Gera o código QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Converte para base64
    buffered = io.BytesIO()
    img.save(buffered)
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"

def verify_totp(secret: str, code: str) -> bool:
    """
    Verifica um código TOTP.
    
    Args:
        secret: Segredo TOTP
        code: Código a ser verificado
        
    Returns:
        bool: True se o código for válido
    """
    totp = pyotp.TOTP(secret)
    return totp.verify(code)

def verify_backup_code(username: str, code: str) -> bool:
    """
    Verifica um código de backup.
    
    Args:
        username: Nome do usuário
        code: Código de backup a ser verificado
        
    Returns:
        bool: True se o código for válido
    """
    if username not in user_backup_codes:
        return False
    
    if code in user_backup_codes[username]:
        # Remove o código usado
        user_backup_codes[username].remove(code)
        return True
    
    return False

async def setup_2fa(current_user: Dict) -> TwoFactorSetup:
    """
    Configura a autenticação de dois fatores para um usuário.
    
    Args:
        current_user: Dados do usuário atual
        
    Returns:
        TwoFactorSetup: Dados para configuração de 2FA
    """
    username = current_user["username"]
    
    # Gera um novo segredo
    secret = generate_secret()
    user_2fa_secrets[username] = secret
    
    # Gera códigos de backup
    backup_codes = generate_backup_codes()
    user_backup_codes[username] = backup_codes
    
    # Gera o código QR
    qr_code = generate_qr_code(secret, username)
    
    # 2FA ainda não está ativado até que o usuário verifique um código
    user_2fa_enabled[username] = False
    
    logger.info(f"2FA configurado para o usuário {username}")
    
    return TwoFactorSetup(
        secret=secret,
        qr_code=qr_code,
        backup_codes=backup_codes
    )

async def enable_2fa(current_user: Dict, code: str) -> bool:
    """
    Ativa a autenticação de dois fatores após verificação do código.
    
    Args:
        current_user: Dados do usuário atual
        code: Código TOTP para verificação
        
    Returns:
        bool: True se o 2FA foi ativado com sucesso
        
    Raises:
        HTTPException: Se o código for inválido
    """
    username = current_user["username"]
    
    if username not in user_2fa_secrets:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA não configurado. Configure primeiro."
        )
    
    secret = user_2fa_secrets[username]
    
    if verify_totp(secret, code):
        user_2fa_enabled[username] = True
        logger.info(f"2FA ativado para o usuário {username}")
        return True
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Código inválido"
    )

async def verify_2fa(username: str, code: str) -> bool:
    """
    Verifica um código 2FA durante o login.
    
    Args:
        username: Nome do usuário
        code: Código TOTP ou de backup
        
    Returns:
        bool: True se o código for válido
        
    Raises:
        HTTPException: Se o código for inválido
    """
    if username not in user_2fa_enabled or not user_2fa_enabled[username]:
        # 2FA não está ativado para este usuário
        return True
    
    if username not in user_2fa_secrets:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA não configurado para este usuário"
        )
    
    secret = user_2fa_secrets[username]
    
    # Verifica se é um código TOTP válido
    if verify_totp(secret, code):
        return True
    
    # Verifica se é um código de backup válido
    if verify_backup_code(username, code):
        logger.warning(f"Código de backup usado pelo usuário {username}")
        return True
    
    # Código inválido
    logger.warning(f"Tentativa de login com código 2FA inválido para {username}")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Código 2FA inválido",
        headers={"WWW-Authenticate": "Bearer"},
    )

async def disable_2fa(current_user: Dict) -> bool:
    """
    Desativa a autenticação de dois fatores.
    
    Args:
        current_user: Dados do usuário atual
        
    Returns:
        bool: True se o 2FA foi desativado com sucesso
    """
    username = current_user["username"]
    
    if username in user_2fa_enabled:
        user_2fa_enabled[username] = False
        logger.info(f"2FA desativado para o usuário {username}")
        return True
    
    return False

def require_2fa(request: Request, current_user: Dict = Depends(get_current_user)):
    """
    Middleware para exigir 2FA em rotas sensíveis.
    
    Args:
        request: Objeto de requisição
        current_user: Dados do usuário atual
        
    Returns:
        Dict: Dados do usuário
        
    Raises:
        HTTPException: Se o 2FA não estiver ativado
    """
    username = current_user["username"]
    
    # Verifica se o usuário tem 2FA ativado
    if username not in user_2fa_enabled or not user_2fa_enabled[username]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta operação requer autenticação de dois fatores"
        )
    
    return current_user