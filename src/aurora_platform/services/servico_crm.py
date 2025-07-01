from aurora_platform.models.cliente_model import Cliente
from aurora_platform.schemas.cliente_schemas import ClienteCreate
from aurora_platform.repositories.cliente_repository import ClienteRepository
from aurora_platform.schemas.cnpj_schema import CNPJResponseSchema
from aurora_platform.services.cnpj_service import CNPJService
from typing import List, Optional, Dict, Any, Sequence
from sqlmodel import Session


class ServicoCRM:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ClienteRepository(db)
        self.cnpj_service = CNPJService()

    # AURORA: Nome do método e chamada ao repo atualizados para 'create'
    def create_cliente(self, cliente: ClienteCreate) -> Cliente:
        return self.repo.create(cliente)

    # AURORA: Nome do método e chamada ao repo atualizados para 'get_all'
    def get_all_clientes(self) -> Sequence[Cliente]:
        return self.repo.get_all()

    # AURORA: Nome do método e chamada ao repo atualizados para 'get_by_id'
    def get_cliente_by_id(self, cliente_id: int) -> Optional[Cliente]:
        return self.repo.get_by_id(cliente_id)

    async def buscar_dados_cnpj(self, cnpj: str) -> CNPJResponseSchema:
        dados: Dict[str, Any] = await self.cnpj_service.buscar_dados_cnpj(cnpj)
        # AURORA: Adicionado um 'model_dump' para garantir que os dados sejam um dict
        # antes de passar para o construtor do schema, uma boa prática.
        return CNPJResponseSchema(
            cnpj=str(dados.get("cnpj", "")),
            razao_social=str(dados.get("razao_social", "")),
            nome_fantasia=str(dados.get("nome_fantasia", "")),
            situacao_cadastral=str(dados.get("situacao_cadastral", "")),
            natureza_juridica=str(dados.get("natureza_juridica", "")),
            data_abertura=str(dados.get("data_abertura", "")),
            capital_social=float(dados.get("capital_social", 0.0)),
            porte=str(dados.get("porte", "")),
            atividade_principal=str(dados.get("atividade_principal", "")),
            logradouro=str(dados.get("logradouro", "")),
            numero=str(dados.get("numero", "")),
            complemento=str(dados.get("complemento", "")),
            bairro=str(dados.get("bairro", "")),
            municipio=str(dados.get("municipio", "")),
            uf=str(dados.get("uf", "")),
            cep=str(dados.get("cep", ""))
        )