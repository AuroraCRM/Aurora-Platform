import logging
from typing import List, Optional  # Adicionado List, Optional

from fastapi import Depends, HTTPException, status

# Removido Session de sqlalchemy.orm, pois get_db agora retorna sqlmodel.Session
# from sqlalchemy.orm import Session
from sqlmodel import Session  # Adicionado Session do sqlmodel

from aurora_platform.database import get_db
from aurora_platform.repositories.cliente_repository import ClienteRepository
from aurora_platform.integrations.cnpj_provider import CNPJaProvider

# from aurora_platform.cache.redis_cache import RedisCache # Removida importação de RedisCache
from aurora_platform.schemas.cliente_schemas import (
    ClienteCreate,
    ClienteUpdate,
)  # Adicionado ClienteUpdate
from aurora_platform.models.cliente_model import Cliente
from aurora_platform.utils.exceptions import (
    CRMServiceError,
)  # Para levantar em caso de não encontrado

logger = logging.getLogger(__name__)


class ServicoCRM:
    def __init__(
        self,
        db: Session = Depends(get_db),  # db é agora sqlmodel.Session
        cnpj_provider: CNPJaProvider = Depends(),
        # cache: RedisCache = Depends(), # Cache pode precisar de revisão se interage com Session
        # Removendo cache por enquanto para simplificar, pode ser adicionado depois
    ):
        self.cliente_repo = ClienteRepository(db)
        self.cnpj_provider = cnpj_provider
        # self.cache = cache

    async def create_cliente_from_cnpj(self, cnpj: str) -> Cliente:
        cnpj_limpo = "".join(filter(str.isdigit, cnpj))

        existing_cliente = self.cliente_repo.get_by_cnpj(cnpj=cnpj_limpo)
        if existing_cliente:
            raise HTTPException(  # Usar HTTPException diretamente aqui é mais comum em serviços FastAPI
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cliente com CNPJ {cnpj_limpo} já cadastrado.",
            )

        # cache_key = f"cnpj:{cnpj_limpo}"
        # cached_data = await self.cache.get(cache_key) # Cache removido temporariamente

        # if cached_data:
        #     logger.info(f"Dados do CNPJ {cnpj_limpo} encontrados no cache.")
        #     dados_brutos, fonte = cached_data
        # else:
        #     logger.info(
        #         f"Dados do CNPJ {cnpj_limpo} não encontrados no cache. Buscando na API externa."
        #     )
        try:
            dados_brutos, fonte = await self.cnpj_provider.get_cnpj_data(cnpj_limpo)
            # await self.cache.set(cache_key, (dados_brutos, fonte), expire=86400) # Cache removido
        except HTTPException as e:  # Se o provider já levanta HTTPException
            raise e
        except Exception as exc:
            logger.error(
                "Erro inesperado ao consultar CNPJ %s: %s", cnpj_limpo, str(exc)
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,  # Mudado para 503
                detail="Erro de comunicação com o serviço externo de CNPJ.",
            )

        try:
            dados_normalizados = self._normalizar_dados_cnpj(dados_brutos, fonte)
            # Garantir que todos os campos obrigatórios de ClienteCreate estejam presentes
            # Se houver campos não opcionais em ClienteCreate que não vêm da normalização,
            # precisará de tratamento aqui (ex: valores padrão ou erro).
            cliente_schema = ClienteCreate(**dados_normalizados)
            return self.cliente_repo.create(cliente_schema)
        except (
            Exception
        ) as exc:  # Pode ser um erro de validação Pydantic ou do repositório
            logger.error(
                "Erro ao normalizar ou criar cliente para o CNPJ %s: %s",
                cnpj_limpo,
                str(exc),
            )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Erro ao processar os dados recebidos do CNPJ: {str(exc)}",
            )

    def _normalizar_dados_cnpj(self, dados_brutos: dict, fonte: str) -> dict:
        # Esta função mapeia os dados da API CNPJ para o schema ClienteCreate.
        # É importante garantir que os campos retornados correspondam aos esperados por ClienteCreate.
        if fonte == "gratuita":  # Assumindo cnpj.ws como fonte gratuita
            est = dados_brutos.get("estabelecimento", {})
            dados_normalizados = {
                "razao_social": dados_brutos.get("razao_social"),
                "nome_fantasia": est.get("nome_fantasia"),
                "cnpj": est.get("cnpj", "")
                .replace(".", "")
                .replace("/", "")
                .replace("-", ""),  # Limpar CNPJ
                "telefone": (
                    f"({est.get('ddd1')}) {est.get('telefone1')}"
                    if est.get("ddd1") and est.get("telefone1")
                    else None
                ),
                "email": est.get("email"),
                # Adicionar outros campos de ClienteCreate que podem vir da API CNPJ
                # Ex: "inscricao_estadual", "site", "segmento", "observacoes"
                # Se não vierem, serão None ou o default do schema.
            }
            # Remover chaves com valor None para não sobrescrever defaults do schema Pydantic, se houver
            return {k: v for k, v in dados_normalizados.items() if v is not None}
        # Adicionar lógica para outras fontes se necessário
        return dados_brutos

    # --- Métodos CRUD Adicionais ---
    def create_cliente(self, cliente_data: ClienteCreate) -> Cliente:
        """Cria um novo cliente diretamente com os dados fornecidos."""
        # Verificar se CNPJ já existe, pois é unique
        if cliente_data.cnpj:
            cnpj_limpo = "".join(filter(str.isdigit, cliente_data.cnpj))
            existing_cliente = self.cliente_repo.get_by_cnpj(cnpj=cnpj_limpo)
            if existing_cliente:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Cliente com CNPJ {cnpj_limpo} já cadastrado.",
                )
        # Aqui, cliente_data já é ClienteCreate, que é o que o repositório espera
        return self.cliente_repo.create(cliente_data)

    def get_all_clientes(self, skip: int = 0, limit: int = 100) -> List[Cliente]:
        """Lista todos os clientes."""
        return self.cliente_repo.list_all(skip=skip, limit=limit)

    def get_cliente_by_id(self, cliente_id: int) -> Optional[Cliente]:
        """Busca um cliente pelo ID."""
        cliente = self.cliente_repo.get_by_id(cliente_id)
        if not cliente:
            raise CRMServiceError(
                message=f"Cliente com ID {cliente_id} não encontrado.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return cliente

    def update_cliente(
        self, cliente_id: int, cliente_data: ClienteUpdate
    ) -> Optional[Cliente]:
        """Atualiza um cliente existente."""
        # Primeiro, verifica se o cliente existe
        db_cliente = self.cliente_repo.get_by_id(cliente_id)
        if not db_cliente:
            raise CRMServiceError(
                message=f"Cliente com ID {cliente_id} não encontrado para atualização.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # Se o CNPJ está sendo atualizado, verificar se o novo CNPJ já existe para outro cliente
        if cliente_data.cnpj and db_cliente.cnpj != cliente_data.cnpj:
            cnpj_limpo = "".join(filter(str.isdigit, cliente_data.cnpj))
            existing_cliente_with_new_cnpj = self.cliente_repo.get_by_cnpj(
                cnpj=cnpj_limpo
            )
            if (
                existing_cliente_with_new_cnpj
                and existing_cliente_with_new_cnpj.id != cliente_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Outro cliente já possui o CNPJ {cnpj_limpo}.",
                )

        updated_cliente = self.cliente_repo.update(
            cliente_id=cliente_id, cliente_data=cliente_data
        )
        # O repositório já lida com o caso de não encontrar, mas uma dupla verificação ou
        # um tratamento de erro mais explícito pode ser adicionado se o repo retornar None.
        # No entanto, o get_by_id acima já deve garantir que o cliente existe.
        return updated_cliente

    def delete_cliente(self, cliente_id: int) -> bool:
        """Remove um cliente."""
        deleted = self.cliente_repo.delete(cliente_id)
        if not deleted:
            raise CRMServiceError(
                message=f"Cliente com ID {cliente_id} não encontrado para remoção.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return deleted
