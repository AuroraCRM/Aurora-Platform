# src/aurora_platform/routers/cliente_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional

from aurora_platform.database import get_session
from aurora_platform.models.cliente_model import Cliente # Asumiendo que Cliente está definido aqui
from aurora_platform.schemas.cliente_schemas import ClienteCreate, ClienteResponse # Assumindo schemas existem
from aurora_platform.services.servico_crm import ServicoCRM # Assumindo que ServicoCRM existe

router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"]
)

# Ajustando a ordem dos parâmetros para que o argumento sem padrão venha primeiro
@router.post("/", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
async def create_cliente(
    cliente_in: ClienteCreate, # Argumento sem padrão
    session: Session = Depends(get_session) # Argumento com padrão
):
    try:
        service = ServicoCRM(session)
        cliente = await service.create_cliente_from_cnpj(cliente_in.cnpj)
        return cliente
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{cliente_id}", response_model=ClienteResponse)
def get_cliente(cliente_id: int, session: Session = Depends(get_session)):
    cliente = session.get(Cliente, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return cliente

@router.get("/", response_model=List[ClienteResponse])
def get_all_clientes(offset: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    clientes = session.exec(select(Cliente).offset(offset).limit(limit)).all()
    return clientes