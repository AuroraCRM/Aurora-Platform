from typing import Optional, Tuple, cast, Any, Sequence
from sqlmodel import Session, select
from fastapi import HTTPException
from sqlalchemy import func, String
from sqlalchemy.sql.expression import ColumnElement

from aurora_platform.models.cliente_model import Cliente
from aurora_platform.schemas.cliente_schemas import (
    ClienteCreate,
    ClienteUpdate,
)

class ClienteRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, cliente_data: ClienteCreate) -> Cliente:
        """Cria um novo cliente no banco de dados."""
        db_cliente = Cliente.model_validate(cliente_data)
        try:
            self.db.add(db_cliente)
            self.db.commit()
            self.db.refresh(db_cliente)
            return db_cliente
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=409,
                detail=f"Erro ao criar cliente: {str(e)}",
            )

    def get_by_id(self, cliente_id: int) -> Optional[Cliente]:
        """Busca um cliente pelo ID."""
        return self.db.get(Cliente, cliente_id)

    # AURORA: Adicionado o método get_all() que estava faltando.
    def get_all(self) -> Sequence[Cliente]:
        """Busca todos os clientes no banco de dados."""
        return list(self.db.exec(select(Cliente)).all())

    def get_by_cnpj(self, cnpj: str) -> Optional[Cliente]:
        """Busca um cliente pelo CNPJ."""
        statement = select(Cliente).where(Cliente.cnpj == cnpj)
        return self.db.exec(statement).first()

    def update(
        self, cliente_id: int, cliente_data: ClienteUpdate
    ) -> Optional[Cliente]:
        """Atualiza um cliente existente."""
        db_cliente = self.get_by_id(cliente_id)
        if db_cliente:
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
        return None

    def delete(self, cliente_id: int) -> bool:
        """Deleta um cliente pelo ID."""
        db_cliente = self.get_by_id(cliente_id)
        if db_cliente:
            try:
                self.db.delete(db_cliente)
                self.db.commit()
                return True
            except Exception as e:
                self.db.rollback()
                raise HTTPException(
                    status_code=500, detail=f"Erro ao deletar cliente: {str(e)}"
                )
        return False

    def search_by_name(
        self, search_term: str, skip: int = 0, limit: int = 100
    ) -> Sequence[Cliente]:
        search_pattern = f"%{search_term}%"
        statement = (
            select(Cliente)
            .where(
                (Cliente.razao_social.ilike(search_pattern)) # type: ignore
                | (Cliente.nome_fantasia.ilike(search_pattern)) # type: ignore
            )
            .order_by(Cliente.razao_social)
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.exec(statement).all())

    def filter_by_segment(
        self, segment: str, skip: int = 0, limit: int = 100
    ) -> Sequence[Cliente]:
        statement = (
            select(Cliente)
            .where(Cliente.segmento == segment)
            .order_by(Cliente.razao_social)
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.exec(statement).all())

    def get_paginated(
        self, skip: int = 0, limit: int = 100
    ) -> Tuple[Sequence[Cliente], int]:
        items_statement = (
            select(Cliente).order_by(Cliente.razao_social).offset(skip).limit(limit)
        )
        items = list(self.db.exec(items_statement).all())
        total_count = self.db.exec(select(func.count(cast(ColumnElement[Any], Cliente.id)))).one()
        return items, total_count