# src/aurora/middleware/rate_limiter.py

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
from typing import Dict, Tuple, Optional
import asyncio

logger = logging.getLogger(__name__)

class RateLimiter(BaseHTTPMiddleware):
    """
    Middleware para limitar a taxa de requisições por IP.
    Protege contra ataques de força bruta e DoS.
    """
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts: Dict[str, Tuple[int, float]] = {}
        self.lock = asyncio.Lock()
    
    async def dispatch(self, request: Request, call_next):
        # Obtém o IP do cliente
        client_ip = self._get_client_ip(request)
        
        # Verifica se o cliente excedeu o limite
        async with self.lock:
            current_time = time.time()
            
            # Limpa entradas antigas (mais de 1 minuto)
            self._clean_old_entries(current_time)
            
            # Verifica e atualiza a contagem para o IP atual
            if client_ip in self.request_counts:
                count, timestamp = self.request_counts[client_ip]
                
                # Se a última requisição foi há menos de 1 minuto
                if current_time - timestamp < 60:
                    if count >= self.requests_per_minute:
                        logger.warning(f"Rate limit excedido para IP: {client_ip}")
                        raise HTTPException(
                            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                            detail="Muitas requisições. Por favor, tente novamente mais tarde."
                        )
                    
                    # Incrementa a contagem
                    self.request_counts[client_ip] = (count + 1, timestamp)
                else:
                    # Reinicia a contagem se passou mais de 1 minuto
                    self.request_counts[client_ip] = (1, current_time)
            else:
                # Primeira requisição deste IP
                self.request_counts[client_ip] = (1, current_time)
        
        # Processa a requisição normalmente
        return await call_next(request)
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Obtém o IP real do cliente, considerando proxies.
        """
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # Pega o primeiro IP da lista (cliente original)
            return forwarded.split(",")[0].strip()
        
        # Fallback para o IP direto
        return request.client.host if request.client else "unknown"
    
    def _clean_old_entries(self, current_time: float) -> None:
        """
        Remove entradas antigas do dicionário de contagem.
        """
        to_remove = []
        for ip, (count, timestamp) in self.request_counts.items():
            if current_time - timestamp >= 60:
                to_remove.append(ip)
        
        for ip in to_remove:
            del self.request_counts[ip]