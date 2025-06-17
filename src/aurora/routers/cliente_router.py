# src/aurora/routers/cliente_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from aurora.database_config import get_db_session
from aurora.models.cliente_model import ClienteDB
from aurora.schemas.cliente_schemas import ClienteCreate, ClienteRead, ClienteUpdate
from aurora.services.servico_crm import (
    cadastrar_novo_cliente,
    buscar_cliente_por_id,
    listar_todos_os_clientes,
    atualizar_cliente,
    deletar_cliente
)

router = APIRouter()

@router.post("/clientes/", response_model=ClienteRead, status_code=status.HTTP_201_CREATED)
def criar_cliente(cliente: ClienteCreate, db: Session = Depends(get_db_session)):
    """
    Cria um novo cliente no sistema.
    """
    return cadastrar_novo_cliente(db, cliente)

@router.get("/clientes/", response_model=List[ClienteRead])
def listar_clientes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_session)):
    """
    Lista todos os clientes cadastrados com paginação.
    """
    return listar_todos_os_clientes(db, skip, limit)

@router.get("/clientes/{cliente_id}", response_model=ClienteRead)
def obter_cliente(cliente_id: int, db: Session = Depends(get_db_session)):
    """
    Obtém os detalhes de um cliente específico pelo ID.
    """
    cliente = buscar_cliente_por_id(db, cliente_id)
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente com ID {cliente_id} não encontrado"
        )
    return cliente

@router.put("/clientes/{cliente_id}", response_model=ClienteRead)
def atualizar_cliente_endpoint(cliente_id: int, cliente_update: ClienteUpdate, db: Session = Depends(get_db_session)):
    """
    Atualiza os dados de um cliente existente.
    """
    cliente_atualizado = atualizar_cliente(db, cliente_id, cliente_update)
    if not cliente_atualizado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente com ID {cliente_id} não encontrado"
        )
    return cliente_atualizado

@router.delete("/clientes/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_cliente(cliente_id: int, db: Session = Depends(get_db_session)):
    """
    Remove um cliente do sistema.
    """
    cliente_removido = deletar_cliente(db, cliente_id)
    if not cliente_removido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente com ID {cliente_id} não encontrado"
        )
    return None