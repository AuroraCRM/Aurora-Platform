from typing import List, Optional
from fastapi import Depends, HTTPException, status
from sqlmodel import Session

from aurora_platform.database import get_session
from aurora_platform.models.lead_models import (
    LeadDB,
    LeadCreate,
    LeadUpdate,
    # LeadRead, # Removido LeadRead não usado no serviço
)  # Schemas definidos em lead_models.py
from aurora_platform.repositories.lead_repository import LeadRepository

# Supondo uma exceção similar à CRMServiceError para consistência
# from aurora_platform.utils.exceptions import LeadServiceError


class LeadService:
    def __init__(self, db: Session = Depends(get_session)):
        self.lead_repo = LeadRepository(db)

    def create_lead(self, lead_data: LeadCreate) -> LeadDB:
        """Cria um novo lead."""
        # LeadCreate é um SQLModel, pode ser validado diretamente para LeadDB
        # se os campos forem compatíveis ou se LeadDB tiver valores padrão.
        # Se LeadCreate não tiver todos os campos de LeadDB (ex: data_criacao),
        # o modelo LeadDB deve ter defaults para eles.
        db_lead = LeadDB.model_validate(lead_data)
        # Potencialmente verificar duplicidade de email se for uma regra de negócio
        # existing_lead = self.lead_repo.get_by_email(lead_data.email)
        # if existing_lead:
        #     raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Lead com este email já existe.")
        return self.lead_repo.create(db_lead)

    def get_all_leads(self, skip: int = 0, limit: int = 100) -> List[LeadDB]:
        """Lista todos os leads."""
        return self.lead_repo.list_all(skip=skip, limit=limit)

    def get_lead_by_id(self, lead_id: int) -> Optional[LeadDB]:
        """Busca um lead pelo ID."""
        lead = self.lead_repo.get_by_id(lead_id)
        if not lead:
            # Levantar exceção se não encontrado, para o router tratar
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lead com ID {lead_id} não encontrado.",
            )
        return lead

    def update_lead(self, lead_id: int, lead_data: LeadUpdate) -> Optional[LeadDB]:
        """Atualiza um lead existente."""
        # Verificar se o lead existe primeiro
        existing_lead = self.lead_repo.get_by_id(lead_id)
        if not existing_lead:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lead com ID {lead_id} não encontrado para atualização.",
            )

        updated_lead = self.lead_repo.update(lead_id=lead_id, lead_data=lead_data)
        return updated_lead

    def delete_lead(self, lead_id: int) -> bool:
        """Remove um lead."""
        # Verificar se o lead existe primeiro
        existing_lead = self.lead_repo.get_by_id(lead_id)
        if not existing_lead:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lead com ID {lead_id} não encontrado para remoção.",
            )

        return self.lead_repo.delete(lead_id=lead_id)
