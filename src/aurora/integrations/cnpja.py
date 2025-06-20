import httpx
from typing import Dict, Any, Optional

from aurora.config import settings
from aurora.cache.redis import get_cache, set_cache


class CNPJAIntegration:
    """Integração com a API CNPJA para consulta de dados de empresas."""

    def __init__(self):
        self.api_url = settings.CNPJA_API_URL
        self.api_key = settings.CNPJA_API_KEY
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    async def get_company_data(self, cnpj: str) -> Optional[Dict[str, Any]]:
        """
        Consulta dados de uma empresa pelo CNPJ.

        Args:
            cnpj: CNPJ da empresa (apenas números)

        Returns:
            Dict: Dados da empresa ou None em caso de erro
        """
        # Verifica se os dados estão em cache
        cache_key = f"cnpja:company:{cnpj}"
        cached_data = get_cache(cache_key)
        if cached_data:
            return cached_data

        # Se não estiver em cache, consulta a API
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_url}/companies/{cnpj}", headers=self.headers
                )

                if response.status_code == 200:
                    data = response.json()
                    # Armazena em cache por 24 horas
                    set_cache(cache_key, data, 86400)
                    return data

                return None
        except Exception:
            return None
