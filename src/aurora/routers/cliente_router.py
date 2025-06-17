# src/aurora/routers/cliente_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from aurora.database_config import get_db_session
from aurora.schemas.cliente_schemas import Cliente, ClienteCreate, ClienteUpdate
from aurora.services.servico_crm import (
    cadastrar_novo_cliente,
    buscar_cliente_por_id,
    listar_todos_os_clientes,
    atualizar_cliente,
    deletar_cliente,
    CRMServiceError
)

router = APIRouter(
    prefix="/clientes",
    tags=["clientes"],
    responses={404: {"description": "Cliente não encontrado"}}
)

@router.post("/", response_model=Cliente, status_code=status.HTTP_201_CREATED)
def criar_cliente(cliente: ClienteCreate, db: Session = Depends(get_db_session)):
    """Cria um novo cliente."""
    try:
        return cadastrar_novo_cliente(db, cliente)
    except CRMServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.get("/", response_model=List[Cliente])
def listar_clientes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_session)):
    """Lista todos os clientes com paginação."""
    return listar_todos_os_clientes(db, skip=skip, limit=limit)

@router.get("/{cliente_id}", response_model=Cliente)
def obter_cliente(cliente_id: int, db: Session = Depends(get_db_session)):
    """Obtém um cliente específico pelo ID."""
    db_cliente = buscar_cliente_por_id(db, cliente_id)
    if db_cliente is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return db_cliente

@router.put("/{cliente_id}", response_model=Cliente)
def atualizar_cliente_endpoint(cliente_id: int, cliente: ClienteUpdate, db: Session = Depends(get_db_session)):
    """Atualiza os dados de um cliente existente."""
    db_cliente = atualizar_cliente(db, cliente_id, cliente)
    if db_cliente is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return db_cliente

@router.delete("/{cliente_id}", response_model=Cliente)
def remover_cliente(cliente_id: int, db: Session = Depends(get_db_session)):
    """Remove um cliente do sistema."""
    db_cliente = deletar_cliente(db, cliente_id)
    if db_cliente is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return db_cliente