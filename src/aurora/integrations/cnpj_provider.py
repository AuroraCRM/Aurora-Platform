# src/aurora/integrations/cnpj_provider.py

import httpx
from typing import Dict, Any
import logging
from fastapi import HTTPException, status
from aurora.config import settings

logger = logging.getLogger(__name__)

class CNPJaProvider:
    """
    Implementação para o MVP que consulta a API pública do cnpj.ws.
    O nome da classe é mantido para evitar alterações na injeção de dependência.
    """
    def __init__(self):
        self.base_url = settings.get("CNPJWS_PUBLIC_URL", "").rstrip('/')
        if not self.base_url:
            raise ValueError("A URL da API (CNPJWS_PUBLIC_URL) não está configurada.")

    async def get_cnpj_data(self, cnpj: str) -> tuple[Dict[str, Any], str]:
        """
        Busca os dados de um CNPJ na API pública cnpj.ws.
        """
        cnpj_limpo = "".join(filter(str.isdigit, cnpj))
        url = f"{self.base_url}/cnpj/{cnpj_limpo}"
        
        logger.info(f"Modo MVP: Consultando CNPJ na API pública {url}")

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, timeout=10.0)
                response.raise_for_status()
                return response.json(), "gratuita"
            except httpx.HTTPStatusError as e:
                logger.error(f"Erro HTTP ao consultar cnpj.ws: {e.response.status_code}")
                raise HTTPException(
                    status_code=e.response.status_code, 
                    detail=f"O serviço de CNPJ retornou um erro: {e.response.status_code}"
                )
            except httpx.RequestError as e:
                logger.error(f"Erro de conexão ao tentar acessar cnpj.ws: {e}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
                    detail="Serviço de consulta de CNPJ indisponível."
                )