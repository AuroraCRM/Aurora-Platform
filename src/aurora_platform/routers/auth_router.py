# src/aurora_platform/routers/auth_router.py - Versão Corrigida

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from sqlmodel import Session

from aurora_platform.database import get_session
from aurora_platform.auth import security
from aurora_platform.schemas import token_schemas

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/token", response_model=token_schemas.Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_session),
    request: Request # Adicionado para obter o IP do cliente
):
    """
    Endpoint para autenticar um usuário e retornar um token JWT.
    """
    client_ip = request.client.host if request.client else "unknown"
    user = security.authenticate_user(
        session, email=form_data.username, password=form_data.password
    )
    if not user:
        logger.warning(
            f"Failed login attempt for user: {form_data.username} from IP: {client_ip}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = security.create_access_token(
        data={"sub": user.email}
    )
    logger.info(f"Successful login for user: {user.email} from IP: {client_ip}")
    
    return {"access_token": access_token, "token_type": "bearer"}