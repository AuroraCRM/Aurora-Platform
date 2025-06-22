# src/aurora/routers/cnpj_routes.py
from fastapi import APIRouter, Depends, HTTPException
from aurora.services.cnpj_service import CNPJService
# CORREÇÃO: Removido 'src.' do caminho de importação
from aurora.schemas.cnpj_schema import CNPJResponse

router = APIRouter()

@router.get("/cnpj/{cnpj}", response_model=CNPJResponse)
async def get_cnpj(cnpj: str, cnpj_service: CNPJService = Depends()):
    try:
        cnpj_data = await cnpj_service.get_cnpj_data(cnpj)
        return CNPJResponse(**cnpj_data.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))