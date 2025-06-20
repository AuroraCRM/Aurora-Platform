# src/aurora/routers/cnpj_routes.py

from fastapi import APIRouter, Depends, HTTPException, status
import logging

# --- CORREÇÃO: Importar os componentes corretos ---
from aurora.services.servico_crm import ServicoCRM
from aurora.schemas.cliente_schemas import Cliente

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/clientes/cnpj/{cnpj}", response_model=Cliente, status_code=status.HTTP_201_CREATED)
async def criar_cliente_via_cnpj(
    cnpj: str,
    # --- CORREÇÃO: Injetamos o serviço diretamente ---
    # FastAPI irá criar o ServicoCRM e suas dependências (db, provider, cache)
    service: ServicoCRM = Depends()
):
    """
    Busca os dados de um CNPJ em um serviço externo, cria um novo cliente
    no banco de dados e retorna os dados do cliente criado.

    Utiliza uma camada de cache para otimizar chamadas repetidas.
    """
    logger.info(f"Requisição recebida para criar cliente a partir do CNPJ: {cnpj}")

    try:
        # A rota apenas delega a responsabilidade para o serviço
        # Linha 30 (corrigida)
        novo_cliente = await service.criar_cliente_por_cnpj(cnpj=cnpj)
        return novo_cliente
    except HTTPException as e:
        # Se o serviço levantar uma HTTPException, nós a repassamos.
        # Nosso error_handler_middleware irá capturá-la.
        raise e
    except Exception as e:
        # Para qualquer outro erro inesperado no serviço
        logger.error(f"Erro inesperado ao criar cliente via CNPJ {cnpj}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro inesperado ao processar a solicitação."
        )
