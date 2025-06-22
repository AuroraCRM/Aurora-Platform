from fastapi import APIRouter, HTTPException
from aurora.services.cnpj_service import CNPJService
from src.schemas.cnpj_schema import CNPJResponse
from aurora.services.exceptions import ExternalAPIException

router = APIRouter()

@router.get("/cnpj/{cnpj}", response_model=CNPJResponse)
def consultar_cnpj(cnpj: str):
    try:
        # Validação básica do CNPJ
        if not cnpj.isdigit() or len(cnpj) != 14:
            raise HTTPException(status_code=400, detail="CNPJ inválido")
            
        return CNPJService.consultar_cnpj(cnpj)
        
    except ExternalAPIException as e:
        raise HTTPException(
            status_code=502,
            detail=f"Erro na integração com serviço externo: {str(e)}"
        )