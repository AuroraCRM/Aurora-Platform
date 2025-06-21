# src/aurora/services/servico_crm.py

from typing import Dict, Any, Optional, List
import httpx
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

# Importações para a classe ServicoCRM
from aurora.repositories.cliente_repository import ClienteRepository
from aurora.integrations.cnpj_provider import CNPJaProvider
from aurora.schemas.cliente_schemas import ClienteCreate, ClienteUpdate
from aurora.database_config import get_db_session
from aurora.cache.redis_cache import RedisCache
from aurora.models.cliente_model import ClienteDB

import logging

logger = logging.getLogger(__name__)

# Constantes para a API CNPJ
CNPJA_OPEN_API_URL = "https://api.cnpja.com/open"
CNPJA_PAID_API_URL = "https://api.cnpja.com/v1"
CNPJA_API_KEY_PRIMARY = None
CNPJA_API_KEY_SECONDARY = None


class ServicoCRM:
    """
    Serviço que orquestra a lógica de negócio do CRM.
    Agora com Repository, Provedor de API e Cache.
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
        """Cria um cliente a partir dos dados de um CNPJ, usando cache."""
        cnpj_limpo = "".join(filter(str.isdigit, cnpj))

        if self.cliente_repo.get_by_cnpj(cnpj=cnpj_limpo):
            raise HTTPException(
                status_code=400,
                detail=f"Cliente com CNPJ {cnpj_limpo} já cadastrado.",
            )

        # Verificação de cache antes da chamada externa
        cache_key = f"cnpj:{cnpj_limpo}"
        cached_data = await self.cache.get(cache_key)

        if cached_data:
            logger.info(f"Dados do CNPJ {cnpj_limpo} encontrados no cache")
            data = cached_data
        else:
            logger.info(
                "Dados do CNPJ %s não encontrados no cache. "
                "Buscando na API externa.",
                cnpj_limpo,
            )
            try:
                dados_brutos, fonte = await self.cnpj_provider.get_cnpj_data(
                    cnpj_limpo,
                )
                # Armazenamento do novo resultado no cache por 24 horas
                await self.cache.set(cache_key, dados_brutos, expire=86400)
                data = dados_brutos
            except HTTPException as e:
                raise e
            except Exception as exc:
                logger.error(
                    "Erro inesperado ao consultar CNPJ %s: %s",
                    cnpj_limpo,
                    str(exc),
                )
                raise HTTPException(
                    status_code=500,
                    detail="Erro interno ao processar solicitação",
                )

        try:
            cliente_schema = self._map_cnpj_data_to_cliente(data, cnpj_limpo)
            return self.cliente_repo.create(cliente_schema.model_dump())
        except Exception as exc:
            logger.error(
                "Erro ao processar dados do CNPJ %s: %s",
                cnpj_limpo,
                str(exc),
            )
            raise HTTPException(
                status_code=422, detail="Erro ao processar dados do CNPJ"
            )

    def _map_cnpj_data_to_cliente(
        self, data: Dict[str, Any], cnpj_limpo: str
    ) -> ClienteCreate:
        """Mapeia os dados da API externa para o schema de cliente."""
        if "company" in data:
            company_data = data.get("company", {})
            razao_social = company_data.get("name", "")
            nome_fantasia = data.get("alias", "")
            cnpj = data.get("taxId", cnpj_limpo)
            emails = data.get("emails", [])
            phones = data.get("phones", [])
            email = (
                emails[0].get("address", "contato@exemplo.com")
                if emails
                else "contato@exemplo.com"
            )
            telefone = ""
            if phones:
                area = phones[0].get("area", "")
                number = phones[0].get("number", "")
                telefone = f"{area}{number}" if area and number else ""
        else:
            razao_social = data.get("name", data.get("RAZAO SOCIAL", ""))
            nome_fantasia = data.get("alias", data.get("NOME FANTASIA", ""))
            cnpj = data.get("taxId", cnpj_limpo)
            email = data.get("email", "contato@exemplo.com")
            telefone = data.get("phone", data.get("TELEFONE", ""))

        return ClienteCreate(
            razao_social=razao_social,
            nome_fantasia=nome_fantasia,
            cnpj=cnpj,
            email=email,
            telefone=telefone,
        )


# Funções auxiliares para operações CRUD
def cadastrar_novo_cliente(
    db: Session,
    cliente_in: ClienteCreate,
) -> ClienteDB:
    """Cadastra um novo cliente no banco de dados."""
    try:
        # Converte o schema Pydantic para um dicionário
        if hasattr(cliente_in, "model_dump"):
            cliente_data = cliente_in.model_dump()
        else:
            cliente_data = cliente_in.dict()

        # Cria uma nova instância do modelo ClienteDB
        db_cliente = ClienteDB(**cliente_data)

        # Adiciona à sessão e persiste no banco
        db.add(db_cliente)
        db.commit()
        db.refresh(db_cliente)
        return db_cliente
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=(
                "Erro de integridade: Cliente com CNPJ ",
                f"{cliente_in.cnpj} já existe.",
            ),
        )
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao cadastrar cliente: {exc}",
        )


def buscar_cliente_por_id(db: Session, cliente_id: int) -> Optional[ClienteDB]:
    """Busca um cliente pelo ID."""
    return db.query(ClienteDB).filter(ClienteDB.id == cliente_id).first()


def listar_todos_os_clientes(
    db: Session, skip: int = 0, limit: int = 100
) -> List[ClienteDB]:
    """Lista todos os clientes com paginação."""
    return (
        db.query(ClienteDB)
        .order_by(ClienteDB.razao_social)
        .offset(skip)
        .limit(limit)
        .all()
    )


def atualizar_cliente(
    db: Session, cliente_id: int, cliente_update: ClienteUpdate
) -> Optional[ClienteDB]:
    """Atualiza os dados de um cliente existente."""
    db_cliente = buscar_cliente_por_id(db, cliente_id)
    if not db_cliente:
        return None

    # Converte o schema Pydantic em dicionário, excluindo campos não definidos
    if hasattr(cliente_update, "model_dump"):
        update_data = cliente_update.model_dump(exclude_unset=True)
    else:
        update_data = cliente_update.dict(exclude_unset=True)

    # Atualiza cada campo do modelo
    for key, value in update_data.items():
        setattr(db_cliente, key, value)

    # Persiste as alterações
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente


def deletar_cliente(db: Session, cliente_id: int) -> Optional[ClienteDB]:
    """Remove um cliente do banco de dados."""
    db_cliente = buscar_cliente_por_id(db, cliente_id)
    if not db_cliente:
        return None

    # Remove o cliente
    db.delete(db_cliente)
    db.commit()
    return db_cliente


# Função para chamar a API CNPJ
async def call_cnpja_api(
    base_url: str, cnpj: str, api_key: str = None
) -> Dict[str, Any]:
    """
    Função para chamar a API CNPJá com tratamento de erros.
    """
    url = f"{base_url}/{cnpj}"
    headers = {"Accept": "application/json"}

    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        status_code = exc.response.status_code
        try:
            error_data = exc.response.json()
            detail = error_data.get("message", str(exc))
        except Exception:
            detail = str(exc)

        raise HTTPException(status_code=status_code, detail=detail)
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Erro de conexão: {exc}",
        )
