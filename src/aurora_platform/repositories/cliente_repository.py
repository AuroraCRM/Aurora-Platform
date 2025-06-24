from typing import Optional, List, Tuple
from sqlmodel import Session, select
from fastapi import HTTPException

from aurora_platform.models.cliente_model import Cliente
from aurora_platform.schemas.cliente_schemas import (
    ClienteCreate,
    ClienteUpdate,
)  # Importar schemas públicos


class ClienteRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self, cliente_data: ClienteCreate
    ) -> Cliente:  # Alterado para ClienteCreate
        """Cria um novo cliente no banco de dados."""
        # cliente_data é um schema Pydantic/SQLModel, model_validate cria o modelo de tabela
        db_cliente = Cliente.model_validate(cliente_data)
        try:
            self.db.add(db_cliente)
            self.db.commit()
            self.db.refresh(db_cliente)
            return db_cliente
        except Exception as e:
            self.db.rollback()
            # TODO: Tratar IntegrityError para CNPJ duplicado de forma mais específica
            raise HTTPException(
                status_code=409,
                detail=f"Erro ao criar cliente: {str(e)}",
            )

    def get_by_id(self, cliente_id: int) -> Optional[Cliente]:
        """Busca um cliente pelo ID."""
        return self.db.get(Cliente, cliente_id)

    def get_by_cnpj(self, cnpj: str) -> Optional[Cliente]:
        """Busca um cliente pelo CNPJ."""
        statement = select(Cliente).where(Cliente.cnpj == cnpj)
        return self.db.exec(statement).first()

    def get_by_email(self, email: str) -> Optional[Cliente]:
        """Busca um cliente pelo email de contato da empresa."""
        if not email:
            return None
        statement = select(Cliente).where(
            Cliente.email == email
        )  # Assumindo que Cliente.email é o de contato
        return self.db.exec(statement).first()

    def list_all(self, skip: int = 0, limit: int = 100) -> List[Cliente]:
        """Lista todos os clientes com paginação."""
        statement = (
            select(Cliente).order_by(Cliente.razao_social).offset(skip).limit(limit)
        )
        return self.db.exec(statement).all()

    def update(
        self, cliente_id: int, cliente_data: ClienteUpdate
    ) -> Optional[Cliente]:  # Alterado para ClienteUpdate
        """Atualiza um cliente existente."""
        db_cliente = self.db.get(Cliente, cliente_id)
        if not db_cliente:
            return None

        update_data = cliente_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_cliente, key, value)

        try:
            self.db.add(db_cliente)
            self.db.commit()
            self.db.refresh(db_cliente)
            return db_cliente
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500, detail=f"Erro ao atualizar cliente: {str(e)}"
            )

    def delete(self, cliente_id: int) -> bool:
        """Remove um cliente do banco de dados."""
        db_cliente = self.db.get(Cliente, cliente_id)
        if not db_cliente:
            return False
        try:
            self.db.delete(db_cliente)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500, detail=f"Erro ao remover cliente: {str(e)}"
            )

    def search_by_name(
        self, search_term: str, skip: int = 0, limit: int = 100
    ) -> List[Cliente]:
        search_pattern = f"%{search_term}%"
        statement = (
            select(Cliente)
            .where(
                (Cliente.razao_social.ilike(search_pattern))
                | (Cliente.nome_fantasia.ilike(search_pattern))
            )
            .order_by(Cliente.razao_social)
            .offset(skip)
            .limit(limit)
        )
        return self.db.exec(statement).all()

    def filter_by_segment(
        self, segment: str, skip: int = 0, limit: int = 100
    ) -> List[Cliente]:
        statement = (
            select(Cliente)
            .where(Cliente.segmento == segment)
            .order_by(Cliente.razao_social)
            .offset(skip)
            .limit(limit)
        )
        return self.db.exec(statement).all()

    def get_paginated(
        self, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Cliente], int]:
        items_statement = (
            select(Cliente).order_by(Cliente.razao_social).offset(skip).limit(limit)
        )
        items = self.db.exec(items_statement).all()

        # TODO: Implementar contagem eficiente para produção
        total_items_query = select(
            Cliente
        )  # Simplificado para contar todos os registros
        total = len(self.db.exec(total_items_query).all())

        return items, total
