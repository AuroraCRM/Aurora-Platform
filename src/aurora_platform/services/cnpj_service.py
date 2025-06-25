# C:\Users\winha\Aurora\Aurora-Platform\src\aurora_platform\services\cnpj_service.py

from aurora_platform.integrations.cnpj_provider import CNPJaProvider


class CNPJService:
    """
    Serviço responsável por consultar dados de CNPJ utilizando o provider CNPJa.
    """

    def __init__(self):
        self.provider = CNPJaProvider()

    def buscar_dados_cnpj(self, cnpj: str) -> dict:
        """
        Consulta o CNPJ e retorna os dados obtidos.
        """
        return self.provider.get_company_data(cnpj)
