# src/aurora/cache/redis_cache.py

from typing import Any, Optional
import json
import aioredis
from aurora.config import settings

class RedisCache:
    """
    Encapsula a lógica de interação com o cache do Redis.
    """
    def __init__(self):
        self.redis = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    
    async def get(self, key: str) -> Optional[Any]:
        """Recupera um valor do cache."""
        data = await self.redis.get(key)
        if data:
            return json.loads(data)
        return None
    
    async def set(self, key: str, value: Any, expire: int = None) -> bool:
        """Armazena um valor no cache com tempo de expiração opcional."""
        data = json.dumps(value)
        if expire:
            return await self.redis.setex(key, expire, data)
        return await self.redis.set(key, data)
    
    async def delete(self, key: str) -> int:
        """Remove um valor do cache."""
        return await self.redis.delete(key)
    
    async def clear(self) -> bool:
        """Limpa todo o cache."""
        return await self.redis.flushdb()