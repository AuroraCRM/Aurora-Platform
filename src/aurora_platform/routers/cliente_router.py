# Caminho completo: C:\Users\winha\Aurora\Aurora-Platform\src\aurora_platform\routers\cliente_router.py

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from aurora_platform.models.cliente_model import Cliente as ClienteModel
from aurora_platform.schemas.cliente_schemas import ClienteCreate, ClienteResponse
from aurora_platform.services.servico_crm import ServicoCRM as ClienteService
from aurora_platform.utils.security import get_current_user
from aurora_platform.database import get_db

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
def criar_cliente(
    cliente: ClienteCreate,
    db: Session = Depends(get_db),
    current_user: ClienteModel = Depends(get_current_user), # Assuming get_current_user returns a user object
    request: Request
):
    client_ip = request.client.host if request.client else "unknown"
    novo_cliente = ClienteService.criar_cliente(cliente, db)
    logger.info(
        f"Client created by user: {current_user.email} (ID: {current_user.id}) "
        f"from IP: {client_ip}. New client ID: {novo_cliente.id}"
    )
    return novo_cliente
