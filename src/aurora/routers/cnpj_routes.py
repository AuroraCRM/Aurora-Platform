# C:\Users\winha\Aurora\CRM Q\src\aurora\routers\cnpj_routes.py

from fastapi import APIRouter, HTTPException
import logging

# Importa a função de serviço e as configurações do arquivo servico_crm.py
# CORRIGIDO: O nome do arquivo no diretório 'services' é 'servico_crm.py'
from ..services.servico_crm import (
    call_cnpja_api,
    CNPJA_OPEN_API_URL,
    CNPJA_PAID_API_URL,
    CNPJA_API_KEY_PRIMARY,
    CNPJA_API_KEY_SECONDARY
)

router = APIRouter() # Cria uma instância do APIRouter para agrupar as rotas

logger = logging.getLogger(__name__)

@router.post("/clientes/cnpj/{cnpj_number}")
async def buscar_cnpj(cnpj_number: str):
    """
    Endpoint para buscar dados de CNPJ, com fallback entre chaves pagas e API gratuita.
    """
    logger.info(f"Requisição recebida para buscar CNPJ: {cnpj_number}")

    # 1. Tentar a API paga com a chave primária
    if CNPJA_API_KEY_PRIMARY:
        try:
            logger.info("Tentando API paga com chave primária...")
            return call_cnpja_api(CNPJA_PAID_API_URL, cnpj_number, CNPJA_API_KEY_PRIMARY)
        except HTTPException as e:
            # Captura HTTPException para tratar erros específicos (401, 429, etc.)
            if e.status_code == 401 or e.status_code == 429:
                logger.warning(f"Erro ({e.status_code}) com chave primária. Tentando com chave secundária (se disponível).")
                if CNPJA_API_KEY_SECONDARY:
                    try:
                        logger.info("Tentando API paga com chave secundária...")
                        return call_cnpja_api(CNPJA_PAID_API_URL, cnpj_number, CNPJA_API_KEY_SECONDARY)
                    except HTTPException as e_secondary:
                        logger.error(f"Ambas as chaves pagas falharam ou excederam o limite. Recorrendo à API gratuita. Erro secundário: {e_secondary.detail}")
                        # Fallback para API gratuita se ambas as pagas falharem
                        return call_cnpja_api(CNPJA_OPEN_API_URL, cnpj_number)
                else:
                    logger.error(f"Chave primária falhou ({e.status_code}) e nenhuma chave secundária configurada. Recorrendo à API gratuita.")
                    # Fallback para API gratuita se a primária falhar e não houver secundária
                    return call_cnpja_api(CNPJA_OPEN_API_URL, cnpj_number)
            else:
                # Outros erros da API paga (400, 500, etc.), re-lançar
                raise e
    else:
        logger.warning("Nenhuma chave de API paga configurada. Recorrendo diretamente à API gratuita.")
        # Se não houver chave paga configurada, tenta direto a gratuita
        return call_cnpja_api(CNPJA_OPEN_API_URL, cnpj_number)