# src/aurora/services/servico_crm.py

from typing import Dict, Any
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from aurora.repositories.cliente_repository import ClienteRepository
from aurora.integrations.cnpj_provider import CNPJaProvider
from aurora.database_config import get_db_session
from aurora.cache.redis_cache import RedisCache

logger = logging.getLogger(__name__)

# Instâncias únicas das dependências
_cnpj_provider = CNPJaProvider()
_redis_cache = RedisCache()

def get_cnpj_provider() -> CNPJaProvider:
    return _cnpj_provider

def get_redis_cache() -> RedisCache:
    return _redis_cache

class ServicoCRM:
    def __init__(
        self,
        db: Session = Depends(get_db_session),
        cnpj_provider: CNPJaProvider = Depends(get_cnpj_provider),
        cache: RedisCache = Depends(get_redis_cache),
    ):
        self._db = db
        self._cliente_repository = ClienteRepository(db)
        self._cnpj_provider = cnpj_provider
        self._cache = cache

    def _normalizar_dados_cnpj(self, dados_brutos: dict, fonte: str) -> dict:
        """Normaliza dados de diferentes fontes de CNPJ para um schema consistente."""
        if fonte == "api_gratuita":
            dados_normalizados = {
                "razao_social": dados_brutos.get("name"),
                "cnpj": dados_brutos.get("taxId"),
                "logradouro": dados_brutos.get("offices", [{}])[0]
                                      .get("address", {}).get("street"),
                "numero": dados_brutos.get("offices", [{}])[0]
                                     .get("address", {}).get("number"),
                "municipio": dados_brutos.get("offices", [{}])[0]
                                       .get("address", {}).get("city"),
                "uf": dados_brutos.get("offices", [{}])[0]
                                 .get("address", {}).get("state"),
                "cep": dados_brutos.get("offices", [{}])[0]
                                  .get("address", {}).get("zipCode"),
                "telefone": (dados_brutos.get("offices", [{}])[0]
                                      .get("phones", [None])[0]),
            }
            # Remove campos None para não sobrescrever defaults do schema
            return {k: v for k, v in dados_normalizados.items() if v is not None}

        # API paga já retorna no formato esperado
        return dados_brutos

    async def criar_cliente_por_cnpj(self, cnpj: str) -> Dict[str, Any]:
        """
        Cria um cliente a partir de um CNPJ, consultando cache e provider,
        normalizando os dados, validando com Pydantic e salvando no repositório.
        """
        # Importação tardia para quebrar dependência circular
        from aurora.schemas.cliente import ClienteCreate

        try:
            cnpj_limpo = "".join(filter(str.isdigit, cnpj))

            # Verifica existência prévia
            if self._cliente_repository.get_by_cnpj(cnpj=cnpj_limpo):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cliente com CNPJ {cnpj_limpo} já cadastrado."
                )

            cache_key = f"cnpj:{cnpj_limpo}"
            cached = await self._cache.get(cache_key)

            if cached:
                logger.info(f"[Cache] CNPJ {cnpj_limpo} encontrado.")
                dados_brutos, fonte = cached
            else:
                logger.info(f"[API] Buscando CNPJ {cnpj_limpo} na fonte externa.")
                dados_brutos, fonte = await self._cnpj_provider.consultar(cnpj_limpo)
                await self._cache.set(cache_key, (dados_brutos, fonte), expire=86400)

            if not dados_brutos:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Nenhum dado encontrado para CNPJ {cnpj_limpo}."
                )

            # 2.1: Normaliza dados antes da validação
            dados_normalizados = self._normalizar_dados_cnpj(dados_brutos, fonte)

            # 2.2: Valida e converte com Pydantic
            cliente_data = ClienteCreate(**dados_normalizados)

            # Persiste no banco e retorna o registro
            return await self._cliente_repository.adicionar(cliente_data)

        except HTTPException:
            # Repassa exceções HTTP já tratadas
            raise
        except Exception as e:
            logger.error(f"Erro ao criar cliente por CNPJ {cnpj}: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Erro interno ao processar CNPJ {cnpj}."
            )
