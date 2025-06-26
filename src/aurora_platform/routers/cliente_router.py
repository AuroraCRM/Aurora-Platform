# Caminho completo: C:\Users\winha\Aurora\Aurora-Platform\src\aurora_platform\routers\cliente_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from aurora_platform.models.cliente_model import Cliente as ClienteModel
from aurora_platform.schemas.cliente_schemas import ClienteCreate, ClienteResponse
from aurora_platform.services.servico_crm import ServicoCRM as ClienteService
from aurora_platform.auth.security import get_current_user # Changed import path
from aurora_platform.database import get_session # Changed get_db to get_session

router = APIRouter()

@router.post("/", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
def criar_cliente(
    cliente: ClienteCreate,
    db: Session = Depends(get_session), # Changed get_db to get_session
):
    try:
        novo_cliente = ClienteService.criar_cliente(cliente, db)
        return novo_cliente
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
