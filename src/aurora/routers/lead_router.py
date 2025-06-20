# src/aurora/routers/lead_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from aurora.database_config import get_db_session
from aurora.schemas.lead_schemas import LeadCreate, LeadRead, LeadUpdate

router = APIRouter()


@router.get("/leads/", response_model=List[LeadRead])
def listar_leads(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db_session)
):
    """
    Lista todos os leads cadastrados com paginação.
    """
    # Implementação temporária
    return []


@router.post("/leads/", response_model=LeadRead, status_code=status.HTTP_201_CREATED)
def criar_lead(lead: LeadCreate, db: Session = Depends(get_db_session)):
    """
    Cria um novo lead no sistema.
    """
    # Implementação temporária
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Funcionalidade ainda não implementada",
    )


@router.get("/leads/{lead_id}", response_model=LeadRead)
def obter_lead(lead_id: int, db: Session = Depends(get_db_session)):
    """
    Obtém os detalhes de um lead específico pelo ID.
    """
    # Implementação temporária
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Funcionalidade ainda não implementada",
    )


@router.put("/leads/{lead_id}", response_model=LeadRead)
def atualizar_lead(
    lead_id: int, lead_update: LeadUpdate, db: Session = Depends(get_db_session)
):
    """
    Atualiza os dados de um lead existente.
    """
    # Implementação temporária
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Funcionalidade ainda não implementada",
    )


@router.delete("/leads/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_lead(lead_id: int, db: Session = Depends(get_db_session)):
    """
    Remove um lead do sistema.
    """
    # Implementação temporária
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Funcionalidade ainda não implementada",
    )
