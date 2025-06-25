# src/aurora/routers/auth_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
# from typing import Dict # Removido Dict não usado

from aurora_platform.database import get_db  # Adicionado para injetar a sessão
from aurora_platform.auth.security import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_access_token_expire_minutes,  # Importar a função aqui
)

# IMPORTAÇÃO CORRIGIDA: Importa a classe TwoFactorAuth e as schemas Pydantic
from aurora_platform.auth.two_factor import (
    TwoFactorAuth,
    TwoFactorSetup,
    TwoFactorVerify,
)
from aurora_platform.schemas.token_schemas import Token
from aurora_platform.models.usuario_model import Usuario as UsuarioModel # Movido para o topo
from aurora_platform.schemas.usuario_schemas import UsuarioRead # Movido para o topo

# from aurora_platform.config import settings # Removido

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
    # authenticate_user agora retorna um objeto Cliente (SQLModel) ou None
    # e é uma função síncrona, então removemos o await.
    # A Session do DB é injetada em authenticate_user via Depends(get_db)
    user = authenticate_user(next(get_db()), form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Assumindo que user.email é o identificador para 2FA e JWT sub
    # Se 2FA estiver habilitado, não emita o token direto, exija o segundo fator
    if two_factor_service.user_2fa_enabled_status.get(
        user.email
    ):  # Modificado para user.email
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Autenticação de dois fatores necessária. Use o endpoint /token/2fa.",
        )

    access_token_expires_minutes = (
        get_access_token_expire_minutes()
    )  # Usar a função importada no módulo
    access_token_expires = timedelta(minutes=access_token_expires_minutes)
    # Usando user.email como 'sub'. Removido 'scopes' por enquanto.
    access_token = create_access_token(
        data={"sub": user.email, "type": "access"},  # Adicionado type para o token
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
    two_factor_data: TwoFactorVerify = Depends(),  # Nome alterado para evitar conflito com a instância do serviço
):
    """
    Endpoint para login com autenticação de dois fatores.
    """
    user = authenticate_user(next(get_db()), form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # CHAMA O MÉTODO DA INSTÂNCIA DO SERVIÇO
    # Assumindo que verify_2fa_login espera o email do usuário
    await two_factor_service.verify_2fa_login(user.email, two_factor_data.code)

    # Reutilizar a importação e lógica de get_access_token_expire_minutes se já estiver no escopo do módulo
    # ou importar novamente se for em outra função/escopo.
    # Para manter simples, vou assumir que a importação no topo do módulo ou na função anterior é suficiente,
    # mas se cada função for totalmente independente, a importação + chamada seria repetida.
    # Como já importamos e usamos em login_for_access_token, podemos apenas chamar a função.
    # No entanto, para clareza e evitar problemas de escopo se as funções forem movidas,
    # é mais seguro obter o valor novamente.
    access_token_expires_minutes = (
        get_access_token_expire_minutes()
    )  # Usar a função importada no módulo
    access_token_expires = timedelta(minutes=access_token_expires_minutes)
    access_token = create_access_token(
        data={
            "sub": user.email,
            "type": "access",
        },  # Usando user.email, adicionado type
        expires_delta=access_token_expires,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_at": access_token_expires,  # Este campo pode não ser necessário se o token expira
    }


# Importações movidas para o topo


@router.post("/2fa/setup", response_model=TwoFactorSetup)
async def setup_two_factor(
    current_user: UsuarioModel = Depends(get_current_user),
):  # Tipo alterado para UsuarioModel
    """
    Configura a autenticação de dois fatores.
    """
    # CHAMA O MÉTODO DA INSTÂNCIA DO SERVIÇO
    # two_factor_service.setup_2fa_for_user espera um objeto UsuarioModel
    return await two_factor_service.setup_2fa_for_user(current_user)


@router.post("/2fa/enable")
async def enable_two_factor(
    two_factor_data: TwoFactorVerify,
    current_user: UsuarioModel = Depends(get_current_user),  # Tipo alterado
):
    """
    Ativa a autenticação de dois fatores.
    """
    # CHAMA O MÉTODO DA INSTÂNCIA DO SERVIÇO
    result = await two_factor_service.enable_2fa_for_user(
        current_user, two_factor_data.code
    )

    if result:
        return {"message": "Autenticação de dois fatores ativada com sucesso"}

    raise HTTPException(  # Isso provavelmente nunca será atingido se enable_2fa_for_user levantar HTTPExceptions
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Não foi possível ativar a autenticação de dois fatores",
    )


@router.post("/2fa/disable")
async def disable_two_factor(
    current_user: UsuarioModel = Depends(get_current_user),
):  # Tipo alterado
    """
    Desativa a autenticação de dois fatores.
    """
    # CHAMA O MÉTODO DA INSTÂNCIA DO SERVIÇO
    result = await two_factor_service.disable_2fa_for_user(current_user)

    if result:
        return {"message": "Autenticação de dois fatores desativada com sucesso"}

    raise HTTPException(  # Isso provavelmente nunca será atingido
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Não foi possível desativar a autenticação de dois fatores",
    )


@router.get(
    "/me", response_model=UsuarioRead
)  # Alterado response_model para UsuarioRead
async def read_users_me(
    current_user: UsuarioModel = Depends(get_current_user),
):  # Tipo alterado para UsuarioModel
    """
    Retorna os dados do usuário atual.
    """
    # current_user é um objeto UsuarioModel, FastAPI o serializará usando UsuarioRead.
    return current_user
