import requests
from aurora.integrations.cnpj_adapter import CNPJAdapter
from src.schemas.cnpj_schema import CNPJResponse
from aurora.services.exceptions import ExternalAPIException

class CNPJService:
    API_URL = "https://www.receitaws.com.br/v1/cnpj/{cnpj}"
    
    @classmethod
    def consultar_cnpj(cls, cnpj: str) -> CNPJResponse:
        try:
            response = requests.get(
                cls.API_URL.format(cnpj=cnpj),
                timeout=10,
                headers={'Accept': 'application/json; charset=latin1'}  # Força encoding correto
            )
            
            # Força decodificação com fallback
            response.encoding = response.apparent_encoding
            data = response.json()
            
            adapted_data = CNPJAdapter.adapt_receitaws_response(data)
            if not adapted_data:
                raise ExternalAPIException("Dados inválidos da API")
                
            return CNPJResponse(**adapted_data)
            
        except (requests.exceptions.RequestException, UnicodeDecodeError) as e:
            raise ExternalAPIException(f"Erro na comunicação com API: {str(e)}")