from fastapi import APIRouter, Depends, status # Removido HTTPException
from typing import List

from aurora_platform.models.lead_models import LeadCreate, LeadRead, LeadUpdate
from aurora_platform.services.lead_service import LeadService

router = APIRouter()


@router.post("/leads/", response_model=LeadRead, status_code=status.HTTP_201_CREATED)
def criar_lead(lead_data: LeadCreate, service: LeadService = Depends()):
    """
    Cria um novo lead no sistema.
    """
    # O LeadService pode levantar HTTPException em caso de erro (ex: email duplicado, se implementado)
    return service.create_lead(lead_data=lead_data)


@router.get("/leads/", response_model=List[LeadRead])
def listar_leads(skip: int = 0, limit: int = 100, service: LeadService = Depends()):
    """
    Lista todos os leads cadastrados com paginação.
    """
    leads_db = service.get_all_leads(skip=skip, limit=limit)
    # Converter List[LeadDB] para List[LeadRead] é feito automaticamente pelo FastAPI
    # se LeadRead for o response_model e for compatível (o que é, pois LeadDB inclui campos de LeadRead)
    return leads_db


@router.get("/leads/{lead_id}", response_model=LeadRead)
def obter_lead(lead_id: int, service: LeadService = Depends()):
    """
    Obtém os detalhes de um lead específico pelo ID.
    """
    # LeadService.get_lead_by_id já levanta HTTPException se não encontrado
    db_lead = service.get_lead_by_id(lead_id=lead_id)
    return db_lead


@router.put("/leads/{lead_id}", response_model=LeadRead)
def atualizar_lead(
    lead_id: int, lead_update_data: LeadUpdate, service: LeadService = Depends()
):
    """
    Atualiza os dados de um lead existente.
    """
    # LeadService.update_lead já levanta HTTPException se não encontrado
    updated_lead = service.update_lead(lead_id=lead_id, lead_data=lead_update_data)
    return updated_lead


@router.delete("/leads/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_lead(lead_id: int, service: LeadService = Depends()):
    """
    Remove um lead do sistema.
    """
    # LeadService.delete_lead já levanta HTTPException se não encontrado
    service.delete_lead(lead_id=lead_id)
    return None  # Resposta 204 não tem corpo
