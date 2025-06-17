# src/aurora/repositories/cliente_repository.py

from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from aurora.models.cliente_model import ClienteDB

class ClienteRepository:
    """
    Repositório para operações de banco de dados relacionadas a clientes.
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
            return {c.name: getattr(db_cliente, c.name) for c in db_cliente.__table__.columns}
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=409,
                detail=f"Cliente com CNPJ {cliente_data.get('cnpj')} já existe"
            )
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao criar cliente: {str(e)}"
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
    
    def list_all(self, skip: int = 0, limit: int = 100) -> List[ClienteDB]:
        """
        Lista todos os clientes com paginação.
        
        Args:
            skip: Número de registros para pular
            limit: Número máximo de registros a retornar
            
        Returns:
            List[ClienteDB]: Lista de clientes
        """
        return self.db.query(ClienteDB).order_by(ClienteDB.razao_social).offset(skip).limit(limit).all()
    
    def update(self, cliente_id: int, cliente_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
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
            return {c.name: getattr(db_cliente, c.name) for c in db_cliente.__table__.columns}
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao atualizar cliente: {str(e)}"
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
                status_code=500,
                detail=f"Erro ao remover cliente: {str(e)}"
            )