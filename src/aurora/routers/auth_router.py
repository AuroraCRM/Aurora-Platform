# src/aurora/routers/auth_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Dict

from aurora.auth.security import (
    authenticate_user,
    create_access_token,
    get_current_user,
)
# IMPORTAÇÃO CORRIGIDA: Importa a classe TwoFactorAuth e as schemas Pydantic
from aurora.auth.two_factor import (
    TwoFactorAuth,
    TwoFactorSetup,
    TwoFactorVerify,
)
from aurora.schemas.token_schemas import Token
from aurora.config import settings

router = APIRouter()

# Instanciar a classe TwoFactorAuth globalmente ou via Depends, dependendo do escopo desejado.
# Para simplicidade neste exemplo, vamos instanciar globalmente.
# Em um ambiente de produção, considere usar um padrão de injeção de dependência mais robusto
# para gerenciar a instância de TwoFactorAuth, especialmente se ela precisar interagir com um DB real.
two_factor_service = TwoFactorAuth()


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint para obter um token de acesso.
    """
    user = await authenticate_user(form_data.username, form_data.password)

    # Se 2FA estiver habilitado, não emita o token direto, exija o segundo fator
    if two_factor_service.user_2fa_enabled_status.get(user["username"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Autenticação de dois fatores necessária. Use o endpoint /token/2fa.",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "scopes": user["scopes"]},
        expires_delta=access_token_expires,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_at": access_token_expires,
    }


@router.post("/token/2fa", response_model=Token)
async def login_with_2fa(
    form_data: OAuth2PasswordRequestForm = Depends(),
    two_factor_data: TwoFactorVerify = Depends(), # Nome alterado para evitar conflito com a instância do serviço
):
    """
    Endpoint para login com autenticação de dois fatores.
    """
    user = await authenticate_user(form_data.username, form_data.password)
    
    # CHAMA O MÉTODO DA INSTÂNCIA DO SERVIÇO
    await two_factor_service.verify_2fa_login(user["username"], two_factor_data.code)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "scopes": user["scopes"]},
        expires_delta=access_token_expires,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_at": access_token_expires,
    }


@router.post("/2fa/setup", response_model=TwoFactorSetup)
async def setup_two_factor(current_user: Dict = Depends(get_current_user)):
    """
    Configura a autenticação de dois fatores.
    """
    # CHAMA O MÉTODO DA INSTÂNCIA DO SERVIÇO
    return await two_factor_service.setup_2fa_for_user(current_user)


@router.post("/2fa/enable")
async def enable_two_factor(
    two_factor_data: TwoFactorVerify, current_user: Dict = Depends(get_current_user) # Nome alterado
):
    """
    Ativa a autenticação de dois fatores.
    """
    # CHAMA O MÉTODO DA INSTÂNCIA DO SERVIÇO
    result = await two_factor_service.enable_2fa_for_user(current_user, two_factor_data.code)

    if result:
        return {"message": "Autenticação de dois fatores ativada com sucesso"}

    raise HTTPException( # Isso provavelmente nunca será atingido se enable_2fa_for_user levantar HTTPExceptions
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Não foi possível ativar a autenticação de dois fatores",
    )


@router.post("/2fa/disable")
async def disable_two_factor(current_user: Dict = Depends(get_current_user)):
    """
    Desativa a autenticação de dois fatores.
    """
    # CHAMA O MÉTODO DA INSTÂNCIA DO SERVIÇO
    result = await two_factor_service.disable_2fa_for_user(current_user)

    if result:
        return {"message": "Autenticação de dois fatores desativada com sucesso"}

    raise HTTPException( # Isso provavelmente nunca será atingido
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Não foi possível desativar a autenticação de dois fatores",
    )


@router.get("/me")
async def read_users_me(current_user: Dict = Depends(get_current_user)):
    """
    Retorna os dados do usuário atual.
    """
    return current_user