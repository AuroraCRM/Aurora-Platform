# src/aurora_platform/routers/auth_router.py - Versão Corrigida

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from sqlmodel import Session

# --- INÍCIO DA CORREÇÃO ---
# Importando a função de dependência correta 'get_session' em vez de 'get_db'
from aurora_platform.database import get_session
# --- FIM DA CORREÇÃO ---

from aurora_platform.auth import security
from aurora_platform.schemas import token_schemas # Supondo que os schemas de token existam aqui

router = APIRouter()

@router.post("/token", response_model=token_schemas.Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    # --- CORREÇÃO NA ASSINATURA DA FUNÇÃO ---
    session: Session = Depends(get_session)
):
    """
    Endpoint para autenticar um usuário e retornar um token JWT.
    """
    user = security.authenticate_user(
        session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = security.create_access_token(
        data={"sub": user.email}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}