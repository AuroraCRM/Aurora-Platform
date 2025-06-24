from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import or_, and_
from fastapi import HTTPException

from aurora.models.cliente_model import Cliente
from aurora.schemas.cliente_schemas import ClienteCreate, ClienteUpdate


class ClienteRepository:
    """
    Repositório para a entidade Cliente.
    Segue o padrão Repository e abstrai a sessão do SQLAlchemy.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(self, cliente_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria um novo cliente no banco de dados."""
        try:
            db_cliente = Cliente(**cliente_data)
            self.db.add(db_cliente)
            self.db.commit()
            self.db.refresh(db_cliente)
            return {c.name: getattr(db_cliente, c.name) for c in db_cliente.__table__.columns}
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=409,
                detail=f"Cliente com CNPJ {cliente_data.get('cnpj')} já existe",
            )
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500, detail=f"Erro ao criar cliente: {str(e)}"
            )

    def get_by_id(self, cliente_id: int) -> Optional[Cliente]:
        """Busca um cliente pelo ID."""
        return self.db.query(Cliente).filter(Cliente.id == cliente_id).first()

    def get_by_cnpj(self, cnpj: str) -> Optional[Cliente]:
        """Busca um cliente pelo CNPJ."""
        return self.db.query(Cliente).filter(Cliente.cnpj == cnpj).first()

    def get_by_email(self, email: str) -> Optional[Cliente]:
        """Busca um cliente pelo email."""
        return self.db.query(Cliente).filter(Cliente.email == email).first()

    def list_all(self, skip: int = 0, limit: int = 100) -> List[Cliente]:
        """Lista todos os clientes com paginação."""
        return (
            self.db.query(Cliente)
            .order_by(Cliente.razao_social)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(self, cliente_id: int, cliente_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Atualiza um cliente existente."""
        db_cliente = self.get_by_id(cliente_id)
        if not db_cliente:
            return None

        try:
            for key, value in cliente_data.items():
                setattr(db_cliente, key, value)
            self.db.commit()
            self.db.refresh(db_cliente)
            return {c.name: getattr(db_cliente, c.name) for c in db_cliente.__table__.columns}
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500, detail=f"Erro ao atualizar cliente: {str(e)}"
            )

    def delete(self, cliente_id: int) -> bool:
        """Remove um cliente do banco de dados."""
        db_cliente = self.get_by_id(cliente_id)
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

    def search_by_name(self, search_term: str, skip: int = 0, limit: int = 100) -> List[Cliente]:
        """Busca clientes por nome (razão social ou nome fantasia)."""
        search_pattern = f"%{search_term}%"
        return (
            self.db.query(Cliente)
            .filter(
                or_(
                    Cliente.razao_social.ilike(search_pattern),
                    Cliente.nome_fantasia.ilike(search_pattern),
                )
            )
            .order_by(Cliente.razao_social)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def filter_by_segment(self, segment: str, skip: int = 0, limit: int = 100) -> List[Cliente]:
        """Filtra clientes por segmento."""
        return (
            self.db.query(Cliente)
            .filter(Cliente.segmento == segment)
            .order_by(Cliente.razao_social)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_date_range(
        self, start_date: datetime, end_date: datetime, skip: int = 0, limit: int = 100
    ) -> List[Cliente]:
        """Busca clientes criados dentro de um intervalo de datas."""
        return (
            self.db.query(Cliente)
            .filter(
                and_(
                    Cliente.data_criacao >= start_date,
                    Cliente.data_criacao <= end_date,
                )
            )
            .order_by(Cliente.data_criacao.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_all(self) -> int:
        """Conta o número total de clientes."""
        return self.db.query(Cliente).count()

    def get_paginated(self, skip: int = 0, limit: int = 100) -> Tuple[List[Cliente], int]:
        """Retorna uma lista paginada de clientes e o total de registros."""
        total = self.count_all()
        items = self.list_all(skip=skip, limit=limit)
        return items, total
