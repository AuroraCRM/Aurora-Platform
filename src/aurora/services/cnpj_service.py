# src/aurora/services/cnpj_service.py
from aurora.integrations.cnpj_provider import CNPJaProvider
# Correção: O nome da classe foi alterado de 'CNPJSchema' para 'CnpjSchema' para corresponder à definição.
from aurora.schemas.cnpj_schema import CnpjSchema
from fastapi import Depends

class CNPJService:
    """
    Serviço para lidar com a lógica de negócio relacionada à consulta de CNPJ.
    """
    def __init__(self, cnpj_provider: CNPJaProvider = Depends()):
        """
        Inicializa o serviço com uma dependência do provedor de CNPJ.
        
        Args:
            cnpj_provider (CNPJaProvider): Provedor de dados de CNPJ injetado pelo FastAPI.
        """
        self.cnpj_provider = cnpj_provider

    async def get_cnpj_data(self, cnpj: str) -> CnpjSchema:
        """
        Busca dados de um CNPJ, utilizando o provedor injetado.

        Args:
            cnpj (str): O número do CNPJ a ser consultado.

        Returns:
            CnpjSchema: Os dados da empresa correspondente ao CNPJ, validados pelo schema.
        
        Raises:
            Qualquer exceção levantada pelo cnpj_provider em caso de erro na API.
        """
        # Busca os dados brutos do provedor externo.
        data = await self.cnpj_provider.get_cnpj_data(cnpj)
        
        # Valida e converte os dados para o schema Pydantic, garantindo a consistência.
        return CnpjSchema(**data)