from typing import List, Optional, Tuple
from sqlmodel import Session, select # Removido SQLModel não usado diretamente

from aurora_platform.models.lead_models import (
    LeadDB,
    LeadUpdate,
)  # LeadUpdate já é um SQLModel


class LeadRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self, lead_data: LeadDB
    ) -> LeadDB:  # Espera LeadDB diretamente, pois LeadCreate pode ser similar
        """Cria um novo lead no banco de dados."""
        # Assume-se que lead_data é uma instância de LeadDB pronta para ser adicionada,
        # ou um schema compatível que LeadDB.model_validate pode processar.
        # Se LeadCreate for usado, seria: db_lead = LeadDB.model_validate(lead_data)
        db_lead = lead_data
        try:
            self.db.add(db_lead)
            self.db.commit()
            self.db.refresh(db_lead)
            return db_lead
        except Exception as e:
            self.db.rollback()
            # Considerar levantar uma exceção mais específica ou logar
            raise e  # Repassar a exceção por enquanto

    def get_by_id(self, lead_id: int) -> Optional[LeadDB]:
        """Busca um lead pelo ID."""
        return self.db.get(LeadDB, lead_id)

    def list_all(self, skip: int = 0, limit: int = 100) -> List[LeadDB]:
        """Lista todos os leads com paginação."""
        statement = (
            select(LeadDB).offset(skip).limit(limit)
        )  # Adicionar order_by se necessário
        return self.db.exec(statement).all()

    def update(self, lead_id: int, lead_data: LeadUpdate) -> Optional[LeadDB]:
        """Atualiza um lead existente."""
        db_lead = self.db.get(LeadDB, lead_id)
        if not db_lead:
            return None

        update_data = lead_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_lead, key, value)

        try:
            self.db.add(db_lead)
            self.db.commit()
            self.db.refresh(db_lead)
            return db_lead
        except Exception as e:
            self.db.rollback()
            raise e

    def delete(self, lead_id: int) -> bool:
        """Remove um lead do banco de dados."""
        db_lead = self.db.get(LeadDB, lead_id)
        if not db_lead:
            return False
        try:
            self.db.delete(db_lead)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e

    def get_paginated(
        self, skip: int = 0, limit: int = 100
    ) -> Tuple[List[LeadDB], int]:
        """Retorna uma lista paginada de leads e o total de registros."""
        items_statement = select(LeadDB).offset(skip).limit(limit)  # Adicionar order_by
        items = self.db.exec(items_statement).all()

        total_items_query = select(LeadDB)
        total = len(
            self.db.exec(total_items_query).all()
        )  # Contagem simples, otimizar se necessário

        return items, total
