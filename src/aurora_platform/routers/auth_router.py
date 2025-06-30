import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from sqlmodel import Session
from datetime import datetime

from aurora_platform.database import get_session
from aurora_platform.auth import security
from aurora_platform.schemas import token_schemas
from aurora_platform.models.usuario_model import Usuario as UsuarioModel

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/token", response_model=token_schemas.Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    request: Request,
    session: Session = Depends(get_session)
):
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
    refresh_token = security.create_refresh_token(
        data={"sub": user.email}
    )

    # Store hashed refresh token in the database
    user.hashed_refresh_token = security.get_password_hash(refresh_token)
    session.add(user)
    session.commit()
    session.refresh(user)

    logger.info(f"Successful login for user: {user.email} from IP: {client_ip}")
    
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    current_user: UsuarioModel = Depends(security.get_current_user),
    session: Session = Depends(get_session),
    token: str = Depends(security.oauth2_scheme)
):
    # Blacklist the current access token
    security.add_token_to_blacklist(token, datetime.fromtimestamp(security.jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])["exp"]))
    
    # Clear the refresh token from the database
    current_user.hashed_refresh_token = None
    session.add(current_user)
    session.commit()

    return

@router.post("/refresh", response_model=token_schemas.Token)
async def refresh_token(
    refresh_token: Annotated[str, Depends(security.oauth2_scheme)],
    request: Request,
    session: Session = Depends(get_session)
):
    client_ip = request.client.host if request.client else "unknown"
    user = security.verify_refresh_token(refresh_token, session)

    # Blacklist the old refresh token
    security.add_token_to_blacklist(refresh_token, datetime.fromtimestamp(security.jwt.decode(refresh_token, security.SECRET_KEY, algorithms=[security.ALGORITHM])["exp"]))

    # Generate new access and refresh tokens
    new_access_token = security.create_access_token(data={"sub": user.email})
    new_refresh_token = security.create_refresh_token(data={"sub": user.email})

    # Store the new hashed refresh token in the database
    user.hashed_refresh_token = security.get_password_hash(new_refresh_token)
    session.add(user)
    session.commit()
    session.refresh(user)

    logger.info(f"Token refreshed for user: {user.email} from IP: {client_ip}")

    return {"access_token": new_access_token, "token_type": "bearer", "refresh_token": new_refresh_token}