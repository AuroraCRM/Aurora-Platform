# src/aurora/integrations/cnpj_provider.py

from abc import ABC, abstractmethod
from typing import Dict, Any
import httpx
from fastapi import HTTPException
from aurora.config import settings
import logging

logger = logging.getLogger(__name__)

class CNPJProvider(ABC):
    """
    Define a interface abstrata para um provedor de dados de CNPJ.
    Qualquer provedor concreto deve implementar o método get_cnpj_data.
    """
    @abstractmethod
    async def get_cnpj_data(self, cnpj: str) -> Dict[str, Any]:
        pass

class CNPJaProvider(CNPJProvider):
    """
    Implementação concreta do CNPJProvider que utiliza a API da CNPJá.
    """
    def __init__(self, api_url: str = None, api_key: str = None, auth_type: str = None):
        self.api_url = api_url or settings.CNPJA_API_URL.rstrip('/')
        self.api_key = api_key or settings.CNPJA_API_KEY
        self.auth_type = auth_type or settings.CNPJA_AUTH_TYPE or "Bearer"
        
        if not self.api_url or not self.api_key:
            raise ValueError("URL ou Chave da API de CNPJ não configurada")
    
    async def get_cnpj_data(self, cnpj: str) -> Dict[str, Any]:
        """
        Busca os dados de um CNPJ na API externa da CNPJá.
        """
        cnpj_limpo = "".join(filter(str.isdigit, cnpj))
        url = f"{self.api_url}/{cnpj_limpo}"
        headers = {
            "Authorization": f"{self.auth_type} {self.api_key}",
            "Accept": "application/json"
        }
        
        logger.info(f"Consultando CNPJ {cnpj_limpo} na API CNPJá")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=10.0)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            try:
                error_data = e.response.json()
                detail_message = error_data.get("message", "Erro desconhecido")
            except:
                detail_message = str(e)
                
            logger.error(f"Erro ao consultar CNPJ {cnpj_limpo}: {detail_message}")
            
            if status_code == 401:
                detail_message = "Falha na autenticação com a API CNPJá"
                
            raise HTTPException(status_code=status_code, detail=f"Erro ao buscar CNPJ: {detail_message}")
        except httpx.RequestError as e:
            logger.error(f"Erro de conexão ao consultar CNPJ {cnpj_limpo}: {str(e)}")
            raise HTTPException(status_code=503, detail=f"Não foi possível se comunicar com o serviço de CNPJ")