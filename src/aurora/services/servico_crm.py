# src/aurora/services/servico_crm.py

from typing import Dict, Any
import logging

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from aurora.database_config import get_db_session
from aurora.repositories.cliente_repository import ClienteRepository
from aurora.integrations.cnpj_provider import CNPJaProvider
from aurora.cache.redis_cache import RedisCache
from aurora.schemas.cliente_schemas import ClienteCreate

logger = logging.getLogger(__name__)

class ServicoCRM:
    """
    Serviço que orquestra a lógica de negócio do CRM, utilizando os padrões
    Repository, Provider de API e Cache para uma arquitetura limpa e robusta.
    """

    def __init__(
        self,
        db: Session = Depends(get_db_session),
        cnpj_provider: CNPJaProvider = Depends(),
        cache: RedisCache = Depends(),
    ):
        self.cliente_repo = ClienteRepository(db)
        self.cnpj_provider = cnpj_provider
        self.cache = cache

    async def create_cliente_from_cnpj(self, cnpj: str) -> Dict[str, Any]:
        """
        Cria um novo cliente a partir da consulta de um CNPJ.
        Orquestra a verificação no banco de dados, a consulta ao cache,
        a chamada à API externa e a criação final do registro.
        """
        cnpj_limpo = "".join(filter(str.isdigit, cnpj))

        # 1. Verifica se o cliente já existe no banco de dados via repositório
        if self.cliente_repo.get_by_cnpj(cnpj=cnpj_limpo):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cliente com CNPJ {cnpj_limpo} já cadastrado.",
            )

        # 2. Tenta obter os dados do cache
        cache_key = f"cnpj:{cnpj_limpo}"
        cached_data = await self.cache.get(cache_key)

        if cached_data:
            logger.info(f"Dados do CNPJ {cnpj_limpo} encontrados no cache.")
            # **CORREÇÃO APLICADA**: Desempacota a tupla (dados, fonte) do cache
            dados_brutos, fonte = cached_data
        else:
            logger.info(f"Dados do CNPJ {cnpj_limpo} não encontrados no cache. Buscando na API externa.")
            try:
                dados_brutos, fonte = await self.cnpj_provider.get_cnpj_data(cnpj_limpo)
                # **CORREÇÃO APLICADA**: Salva a tupla completa no cache para manter o contexto da fonte
                await self.cache.set(cache_key, (dados_brutos, fonte), expire=86400) # 24 horas
            except HTTPException as e:
                # Re-lança exceções da API (ex: 404, 503) para o router tratar
                raise e
            except Exception as exc:
                logger.error("Erro inesperado ao consultar CNPJ %s: %s", cnpj_limpo, str(exc))
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Erro interno ao processar a solicitação de CNPJ.",
                )

        # 3. Normaliza os dados usando o padrão Adapter
        try:
            dados_normalizados = self._normalizar_dados_cnpj(dados_brutos, fonte)
            cliente_schema = ClienteCreate(**dados_normalizados)
            
            # 4. Usa o repositório para criar o cliente no banco de dados
            return self.cliente_repo.create(cliente_schema)
        
        except Exception as exc:
            logger.error("Erro ao normalizar ou criar cliente para o CNPJ %s: %s", cnpj_limpo, str(exc))
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail=f"Erro ao processar os dados recebidos do CNPJ: {exc}"
            )

    def _normalizar_dados_cnpj(self, dados_brutos: dict, fonte: str) -> dict:
        """
        Normaliza dados da API cnpj.ws para o schema ClienteCreate.
        Esta função é o "Adapter" do nosso sistema.
        """
        if fonte == 'gratuita':
            est = dados_brutos.get("estabelecimento", {})
            
            dados_normalizados = {
                "razao_social": dados_brutos.get("razao_social"),
                "nome_fantasia": est.get("nome_fantasia"),
                "cnpj": est.get("cnpj"),
                "inscricao_estadual": est.get("inscricoes_estaduais", [{}])[0].get("inscricao_estadual") if est.get("inscricoes_estaduais") else None,
                "telefone": f"({est.get('ddd1')}) {est.get('telefone1')}" if est.get('ddd1') and est.get('telefone1') else None,
                "email": est.get("email"),
                "logradouro": est.get("logradouro"),
                "numero": est.get("numero"),
                "complemento": est.get("complemento"),
                "bairro": est.get("bairro"),
                "municipio": est.get("cidade", {}).get("nome"),
                "uf": est.get("estado", {}).get("sigla"),
                "cep": est.get("cep"),
            }
            return {k: v for k, v in dados_normalizados.items() if v is not None}
        
        return dados_brutos