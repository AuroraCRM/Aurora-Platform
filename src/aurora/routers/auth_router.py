# src/aurora/routers/auth_router.py

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Dict, Any

from aurora.auth.security import (
    authenticate_user, 
    create_access_token, 
    get_current_user,
    Token,
    UserCredentials
)
from aurora.auth.two_factor import (
    setup_2fa,
    enable_2fa,
    disable_2fa,
    verify_2fa,
    TwoFactorSetup,
    TwoFactorVerify
)
from aurora.config import settings

router = APIRouter()

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint para obter um token de acesso.
    
    Args:
        form_data: Formulário com username e password
        
    Returns:
        Token: Token de acesso
        
    Raises:
        HTTPException: Se as credenciais forem inválidas
    """
    user = await authenticate_user(form_data.username, form_data.password)
    
    # Cria o token de acesso
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "scopes": user["scopes"]},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_at": access_token_expires
    }

@router.post("/token/2fa", response_model=Token)
async def login_with_2fa(
    form_data: OAuth2PasswordRequestForm = Depends(),
    two_factor: TwoFactorVerify = Depends()
):
    """
    Endpoint para login com autenticação de dois fatores.
    
    Args:
        form_data: Formulário com username e password
        two_factor: Código 2FA
        
    Returns:
        Token: Token de acesso
        
    Raises:
        HTTPException: Se as credenciais ou o código 2FA forem inválidos
    """
    # Autentica o usuário
    user = await authenticate_user(form_data.username, form_data.password)
    
    # Verifica o código 2FA
    await verify_2fa(user["username"], two_factor.code)
    
    # Cria o token de acesso
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "scopes": user["scopes"]},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_at": access_token_expires
    }

@router.post("/2fa/setup", response_model=TwoFactorSetup)
async def setup_two_factor(current_user: Dict = Depends(get_current_user)):
    """
    Configura a autenticação de dois fatores.
    
    Args:
        current_user: Usuário atual autenticado
        
    Returns:
        TwoFactorSetup: Dados para configuração de 2FA
    """
    return await setup_2fa(current_user)

@router.post("/2fa/enable")
async def enable_two_factor(
    two_factor: TwoFactorVerify,
    current_user: Dict = Depends(get_current_user)
):
    """
    Ativa a autenticação de dois fatores.
    
    Args:
        two_factor: Código 2FA para verificação
        current_user: Usuário atual autenticado
        
    Returns:
        Dict: Mensagem de sucesso
    """
    result = await enable_2fa(current_user, two_factor.code)
    
    if result:
        return {"message": "Autenticação de dois fatores ativada com sucesso"}
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Não foi possível ativar a autenticação de dois fatores"
    )

@router.post("/2fa/disable")
async def disable_two_factor(current_user: Dict = Depends(get_current_user)):
    """
    Desativa a autenticação de dois fatores.
    
    Args:
        current_user: Usuário atual autenticado
        
    Returns:
        Dict: Mensagem de sucesso
    """
    result = await disable_2fa(current_user)
    
    if result:
        return {"message": "Autenticação de dois fatores desativada com sucesso"}
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Não foi possível desativar a autenticação de dois fatores"
    )

@router.get("/me")
async def read_users_me(current_user: Dict = Depends(get_current_user)):
    """
    Retorna os dados do usuário atual.
    
    Args:
        current_user: Usuário atual autenticado
        
    Returns:
        Dict: Dados do usuário
    """
    return current_user