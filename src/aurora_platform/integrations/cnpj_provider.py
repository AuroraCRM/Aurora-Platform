# src/aurora/integrations/cnpj_provider.py

# --- Importações da Biblioteca Padrão ---
import json
import logging
from typing import Any, Dict, cast

# --- Importações de Terceiros ---
import httpx
from fastapi import HTTPException, status

# --- Importações Locais da Aplicação ---
from aurora_platform.config import settings

# --- Configuração do Logger ---
# Esta linha define a variável 'logger' que estava faltando
logger = logging.getLogger(__name__)


class CNPJaProvider:
    """
    Implementação para o MVP que consulta a API pública do cnpj.ws.
    O nome da classe foi mantido para evitar alterações na injeção de dependência.
    """

    def __init__(self):
        self.base_url = str(cast(Dict[str, Any], settings).get("CNPJWS_PUBLIC_URL", "")).rstrip("/")
        if not self.base_url:
            raise ValueError("A URL da API (CNPJWS_PUBLIC_URL) não está configurada.")

    async def get_cnpj_data(self, cnpj: str) -> tuple[Dict[str, Any], str]:
        """
        Busca os dados de um CNPJ na API pública cnpj.ws.
        """
        cnpj_limpo = "".join(filter(str.isdigit, cnpj))
        # O método _make_api_call agora lida com a montagem da URL completa
        dados_brutos = await self._make_api_call(self.base_url, cnpj_limpo)

        return dados_brutos, "gratuita"

    async def _make_api_call(self, url: str, cnpj: str) -> Dict[str, Any]:
        """
        Função auxiliar para realizar uma única chamada HTTP,
        com o Protocolo Padrão de Decodificação Robusta.
        """
        full_url = f"{url}/cnpj/{cnpj}"
        headers = {"Accept": "application/json"}

        logger.info(f"Modo MVP: Consultando API externa: {full_url}")

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(full_url, headers=headers, timeout=10.0)
                response.raise_for_status()

                # --- INÍCIO DO PROTOCOLO DE DECODIFICAÇÃO ---
                try:
                    response_text = response.content.decode("utf-8")
                except UnicodeDecodeError:
                    logger.warning(
                        f"Falha ao decodificar a resposta de {full_url} como UTF-8. Tentando como latin-1."
                    )
                    response_text = response.content.decode("latin-1")

                data = json.loads(response_text)
                # --- FIM DO PROTOCOLO ---

                return data

            except httpx.HTTPStatusError as e:
                logger.error(
                    f"Erro de status HTTP ao consultar {full_url}: {e.response.status_code}"
                )
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"O serviço de CNPJ retornou um erro: {e.response.status_code}",
                )
            except Exception as e:
                logger.error(f"Erro inesperado ao consultar {full_url}: {e}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Erro de comunicação com o serviço externo: {e}",
                )
