import json
from typing import Any, Optional

import redis

from aurora.config import settings

# Conexão com o Redis
redis_client = redis.from_url(settings.REDIS_URL)

def set_cache(key: str, value: Any, expiration: int = 3600) -> bool:
    """
    Armazena um valor no cache.
    
    Args:
        key: Chave para armazenar o valor
        value: Valor a ser armazenado
        expiration: Tempo de expiração em segundos (padrão: 1 hora)
        
    Returns:
        bool: True se o valor foi armazenado com sucesso
    """
    try:
        serialized_value = json.dumps(value)
        return redis_client.setex(key, expiration, serialized_value)
    except Exception:
        return False

def get_cache(key: str) -> Optional[Any]:
    """
    Recupera um valor do cache.
    
    Args:
        key: Chave do valor a ser recuperado
        
    Returns:
        Any: Valor armazenado ou None se não encontrado
    """
    try:
        value = redis_client.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception:
        return None

def delete_cache(key: str) -> bool:
    """
    Remove um valor do cache.
    
    Args:
        key: Chave do valor a ser removido
        
    Returns:
        bool: True se o valor foi removido com sucesso
    """
    try:
        return redis_client.delete(key) > 0
    except Exception:
        return False