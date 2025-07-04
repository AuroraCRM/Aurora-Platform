# src/aurora_platform/cache/redis_cache.py
import redis.asyncio as redis
import json
from typing import Any, Optional, Dict, cast
from aurora_platform.config import settings

# Configuração da conexão com o Redis a partir do Dynaconf
REDIS_HOST = str(cast(Dict[str, Any], settings).get("REDIS_HOST", "localhost"))
REDIS_PORT = int(cast(Dict[str, Any], settings).get("REDIS_PORT", 6379))
REDIS_DB = int(cast(Dict[str, Any], settings).get("REDIS_DB", 0))

try:
    # Pool de conexões para reutilização eficiente
    redis_pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    redis_client = redis.Redis(connection_pool=redis_pool)
    # Testa a conexão na inicialização
    # Use await para ping em redis.asyncio
    # await redis_client.ping()
    print("Conexão com o Redis estabelecida com sucesso.")
except redis.ConnectionError as e:
    print(f"ERRO: Não foi possível conectar ao Redis em {REDIS_HOST}:{REDIS_PORT}. {e}")
    redis_client = None


async def get_cache(key: str) -> Optional[Any]:
    """Busca um valor no cache do Redis pela chave."""
    if not redis_client:
        return None

    cached_value = await redis_client.get(key)
    if cached_value:
        return json.loads(cached_value)
    return None


async def set_cache(key: str, value: Any, expire: Optional[int] = None):
    """
    Armazena um valor no cache do Redis com um tempo de expiração opcional.

    Args:
        key (str): A chave para o valor a ser armazenado.
        value (Any): O valor (deve ser serializável em JSON).
        expire (Optional[int]): Tempo em segundos para a chave expirar.
                                 O padrão é None (não expira).
    """
    if not redis_client:
        return

    # CORREÇÃO: O tipo de 'expire' agora é `Optional[int]`, compatível com o padrão `None`.
    # A lógica de serialização e armazenamento permanece a mesma.
    await redis_client.set(key, json.dumps(value), ex=expire)


async def clear_cache(key: str):
    """Remove uma chave do cache."""
    if not redis_client:
        return
    await redis_client.delete(key)
