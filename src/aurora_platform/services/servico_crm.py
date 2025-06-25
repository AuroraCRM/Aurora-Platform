# C:\Users\winha\Aurora\Aurora-Platform\src\aurora_platform\services\servico_crm.py

from aurora_platform.models.cliente_model import Cliente
from aurora_platform.schemas.cliente_schemas import ClienteCreate
from aurora_platform.repositories.cliente_repository import ClienteRepository
from aurora_platform.schemas.cnpj_schema import CNPJResponseSchema
from aurora_platform.services.cnpj_service import CNPJService  # Corrigido o nome da classe
from typing import List, Optional
from sqlalchemy.orm import Session


class ServicoCRM:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ClienteRepository(db)
        self.cnpj_service = CNPJService()

    def criar_cliente(self, cliente: ClienteCreate) -> Cliente:
        return self.repo.criar(cliente)

    def listar_clientes(self) -> List[Cliente]:
        return self.repo.listar_todos()

    def buscar_cliente_por_id(self, cliente_id: int) -> Optional[Cliente]:
        return self.repo.buscar_por_id(cliente_id)

    def buscar_dados_cnpj(self, cnpj: str) -> CNPJResponseSchema:
        dados = self.cnpj_service.buscar_dados_cnpj(cnpj)
        return CNPJResponseSchema(**dados)
