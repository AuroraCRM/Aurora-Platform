from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import or_, and_
from fastapi import HTTPException

from aurora.models.cliente_model import ClienteDB
from aurora.schemas.cliente_schemas import ClienteCreate, ClienteUpdate


class ClienteRepository:
    """
    Repositório para a entidade Cliente.
    Segue o padrão Repository e abstrai a sessão do SQLAlchemy.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(self, cliente_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria um novo cliente no banco de dados.

        Args:
            cliente_data: Dicionário com os dados do cliente

        Returns:
            Dict: Cliente criado

        Raises:
            HTTPException: Se ocorrer um erro ao criar o cliente
        """
        try:
            db_cliente = ClienteDB(**cliente_data)
            self.db.add(db_cliente)
            self.db.commit()
            self.db.refresh(db_cliente)

            # Converte o objeto SQLAlchemy para um dicionário
            return {
                c.name: getattr(db_cliente, c.name)
                for c in db_cliente.__table__.columns
            }
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

    def get_by_id(self, cliente_id: int) -> Optional[ClienteDB]:
        """
        Busca um cliente pelo ID.

        Args:
            cliente_id: ID do cliente

        Returns:
            ClienteDB: Cliente encontrado ou None
        """
        return self.db.query(ClienteDB).filter(ClienteDB.id == cliente_id).first()

    def get_by_cnpj(self, cnpj: str) -> Optional[ClienteDB]:
        """
        Busca um cliente pelo CNPJ.

        Args:
            cnpj: CNPJ do cliente

        Returns:
            ClienteDB: Cliente encontrado ou None
        """
        return self.db.query(ClienteDB).filter(ClienteDB.cnpj == cnpj).first()

    def get_by_email(self, email: str) -> Optional[ClienteDB]:
        """
        Busca um cliente pelo email.

        Args:
            email: Email do cliente

        Returns:
            ClienteDB: Cliente encontrado ou None
        """
        return self.db.query(ClienteDB).filter(ClienteDB.email == email).first()

    def list_all(self, skip: int = 0, limit: int = 100) -> List[ClienteDB]:
        """
        Lista todos os clientes com paginação.

        Args:
            skip: Número de registros para pular
            limit: Número máximo de registros a retornar

        Returns:
            List[ClienteDB]: Lista de clientes
        """
        return (
            self.db.query(ClienteDB)
            .order_by(ClienteDB.razao_social)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(
        self, cliente_id: int, cliente_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Atualiza um cliente existente.

        Args:
            cliente_id: ID do cliente
            cliente_data: Dicionário com os dados a atualizar

        Returns:
            Dict: Cliente atualizado ou None se não encontrado
        """
        db_cliente = self.get_by_id(cliente_id)
        if not db_cliente:
            return None

        try:
            # Atualiza cada campo do modelo
            for key, value in cliente_data.items():
                if hasattr(db_cliente, key):
                    setattr(db_cliente, key, value)

            self.db.add(db_cliente)
            self.db.commit()
            self.db.refresh(db_cliente)

            # Converte o objeto SQLAlchemy para um dicionário
            return {
                c.name: getattr(db_cliente, c.name)
                for c in db_cliente.__table__.columns
            }
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500, detail=f"Erro ao atualizar cliente: {str(e)}"
            )

    def delete(self, cliente_id: int) -> bool:
        """
        Remove um cliente do banco de dados.

        Args:
            cliente_id: ID do cliente

        Returns:
            bool: True se o cliente foi removido, False se não encontrado
        """
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

    def search_by_name(
        self, search_term: str, skip: int = 0, limit: int = 100
    ) -> List[ClienteDB]:
        """
        Busca clientes por nome (razão social ou nome fantasia).

        Args:
            search_term: Termo de busca
            skip: Número de registros para pular
            limit: Número máximo de registros a retornar

        Returns:
            List[ClienteDB]: Lista de clientes que correspondem à busca
        """
        search_pattern = f"%{search_term}%"
        return (
            self.db.query(ClienteDB)
            .filter(
                or_(
                    ClienteDB.razao_social.ilike(search_pattern),
                    ClienteDB.nome_fantasia.ilike(search_pattern),
                )
            )
            .order_by(ClienteDB.razao_social)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def filter_by_segment(
        self, segment: str, skip: int = 0, limit: int = 100
    ) -> List[ClienteDB]:
        """
        Filtra clientes por segmento.

        Args:
            segment: Segmento para filtrar
            skip: Número de registros para pular
            limit: Número máximo de registros a retornar

        Returns:
            List[ClienteDB]: Lista de clientes do segmento especificado
        """
        return (
            self.db.query(ClienteDB)
            .filter(ClienteDB.segmento == segment)
            .order_by(ClienteDB.razao_social)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_date_range(
        self, start_date: datetime, end_date: datetime, skip: int = 0, limit: int = 100
    ) -> List[ClienteDB]:
        """
        Busca clientes criados dentro de um intervalo de datas.

        Args:
            start_date: Data inicial
            end_date: Data final
            skip: Número de registros para pular
            limit: Número máximo de registros a retornar

        Returns:
            List[ClienteDB]: Lista de clientes criados no período especificado
        """
        return (
            self.db.query(ClienteDB)
            .filter(
                and_(
                    ClienteDB.data_criacao >= start_date,
                    ClienteDB.data_criacao <= end_date,
                )
            )
            .order_by(ClienteDB.data_criacao.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_all(self) -> int:
        """
        Conta o número total de clientes.

        Returns:
            int: Número total de clientes
        """
        return self.db.query(ClienteDB).count()

    def get_paginated(
        self, skip: int = 0, limit: int = 100
    ) -> Tuple[List[ClienteDB], int]:
        """
        Retorna uma lista paginada de clientes e o total de registros.

        Args:
            skip: Número de registros para pular
            limit: Número máximo de registros a retornar

        Returns:
            Tuple[List[ClienteDB], int]: Lista de clientes e total de registros
        """
        total = self.count_all()
        items = self.list_all(skip=skip, limit=limit)
        return items, total
