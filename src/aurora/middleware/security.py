# src/aurora/middleware/security.py

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging
import re
from typing import List, Optional
from aurora.config import settings

logger = logging.getLogger(__name__)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware para implementar controles de segurança HTTP.
    Implementa as melhores práticas de segurança OWASP.
    """
    
    def __init__(self, app, **options):
        super().__init__(app)
        self.allowed_hosts: List[str] = options.get('allowed_hosts', ['localhost', '127.0.0.1'])
        self.allowed_paths: List[str] = options.get('allowed_paths', ['/api', '/docs', '/redoc', '/openapi.json'])
        self.max_content_length: int = options.get('max_content_length', 10 * 1024 * 1024)  # 10MB
        
    async def dispatch(self, request: Request, call_next):
        try:
            # Validação de Host
            if not self._validate_host(request):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Host inválido"
                )
            
            # Validação de Path
            if not self._validate_path(request):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Recurso não encontrado"
                )
            
            # Validação de tamanho do conteúdo
            content_length = request.headers.get('content-length')
            if content_length and int(content_length) > self.max_content_length:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="Conteúdo muito grande"
                )
            
            # Validação de métodos HTTP
            if request.method not in ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']:
                raise HTTPException(
                    status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                    detail="Método não permitido"
                )
            
            response = await call_next(request)
            
            # Adiciona cabeçalhos de segurança
            response.headers.update({
                # Proteção contra Clickjacking
                "X-Frame-Options": "DENY",
                
                # Proteção contra MIME-sniffing
                "X-Content-Type-Options": "nosniff",
                
                # Proteção XSS
                "X-XSS-Protection": "1; mode=block",
                
                # Força HTTPS
                "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
                
                # Content Security Policy
                "Content-Security-Policy": (
                    "default-src 'self'; "
                    "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                    "style-src 'self' 'unsafe-inline'; "
                    "img-src 'self' data:; "
                    "font-src 'self'; "
                    "frame-ancestors 'none'; "
                    "form-action 'self'"
                ),
                
                # Controle de Cache
                "Cache-Control": "no-store, no-cache, must-revalidate, proxy-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
                
                # Política de Referrer
                "Referrer-Policy": "strict-origin-when-cross-origin",
                
                # Permissões
                "Permissions-Policy": (
                    "accelerometer=(), "
                    "camera=(), "
                    "geolocation=(), "
                    "gyroscope=(), "
                    "magnetometer=(), "
                    "microphone=(), "
                    "payment=(), "
                    "usb=()"
                ),
            })
            
            # Remove cabeçalhos sensíveis
            response.headers.pop("Server", None)
            response.headers.pop("X-Powered-By", None)
            
            return response
            
        except HTTPException as e:
            logger.warning(f"Violação de segurança: {e.detail}")
            raise e
        except Exception as e:
            logger.error(f"Erro de segurança não tratado: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno de segurança"
            )
    
    def _validate_host(self, request: Request) -> bool:
        """Valida o cabeçalho Host contra uma lista de hosts permitidos."""
        host = request.headers.get('host', '').split(':')[0]
        return host in self.allowed_hosts
    
    def _validate_path(self, request: Request) -> bool:
        """Valida o path da requisição contra padrões permitidos."""
        path = request.url.path
        
        # Verifica paths permitidos
        for allowed_path in self.allowed_paths:
            if path.startswith(allowed_path):
                return True
        
        # Verifica por tentativas de path traversal
        if '..' in path or '//' in path:
            return False
        
        # Verifica por caracteres especiais suspeitos
        if re.search(r'[<>\'";]', path):
            return False
        
        return True