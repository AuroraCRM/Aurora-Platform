# src/aurora/routers/cnpj_routes.py
from fastapi import APIRouter, Depends # Removido HTTPException
from aurora_platform.services.cnpj_service import CNPJService

# CORREÇÃO: Removido 'src.' do caminho de importação
from aurora_platform.schemas.cnpj_schema import CNPJResponseSchema

router = APIRouter()


@router.get("/cnpj/{cnpj}", response_model=CNPJResponseSchema)
async def get_cnpj(cnpj: str, cnpj_service: CNPJService = Depends()):
    # O CNPJService.get_cnpj_data já retorna CNPJResponse e levanta HTTPExceptions apropriadas.
    # Não é necessário try-except genérico aqui se o serviço já trata os erros.
    cnpj_data = await cnpj_service.buscar_dados_cnpj(cnpj)
    return cnpj_data  # Retorna diretamente o objeto CNPJResponse
