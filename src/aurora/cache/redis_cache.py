# src/aurora/cache/redis_cache.py

from typing import Any, Optional
import json
# --- CORREÇÃO: Importar o cliente assíncrono da biblioteca 'redis' oficial ---
from redis.asyncio import Redis
from aurora.config import settings

class RedisCache:
    """
    Encapsula a lógica de interação com o cache do Redis,
    utilizando o cliente assíncrono oficial da biblioteca redis-py.
    """
    def __init__(self):
        # A URL é obtida diretamente do módulo de configurações centralizado.
        # --- CORREÇÃO: Usa 'Redis.from_url' em vez de 'aioredis.from_url' ---
        self.redis_client: Redis = Redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    
    async def get(self, key: str) -> Optional[Any]:
        """Recupera um valor do cache."""
        # Usa o cliente oficial
        data = await self.redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    
    async def set(self, key: str, value: Any, expire: int = None) -> bool:
        """Armazena um valor no cache com tempo de expiração opcional."""
        data = json.dumps(value)
        # Usa o cliente oficial
        if expire:
            return await self.redis_client.setex(key, expire, data)
        return await self.redis_client.set(key, data)
    
    async def delete(self, key: str) -> int:
        """Remove um valor do cache."""
        return await self.redis_client.delete(key)
    
    async def clear(self) -> bool:
        """Limpa todo o cache."""
        return await self.redis_client.flushdb()

