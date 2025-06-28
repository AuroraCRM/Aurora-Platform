# src/aurora/middleware/security.py

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import re
from typing import List

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware para implementar controles de segurança HTTP.
    Implementa as melhores práticas de segurança OWASP.
    """

    def __init__(self, app, **options):
        super().__init__(app)
        # Incluímos "testserver" para que o TestClient possa passar na validação de Host
        self.allowed_hosts: List[str] = options.get(
            "allowed_hosts",
            ["localhost", "127.0.0.1", "testserver"],
        )
        self.allowed_paths: List[str] = options.get(
            "allowed_paths",
            ["/api", "/docs", "/redoc", "/openapi.json", "/favicon.ico"],
        )
        self.max_content_length: int = options.get(
            "max_content_length", 10 * 1024 * 1024
        )  # 10MB

    async def dispatch(self, request: Request, call_next):
        try:
            # Validação de Host
            if not self._validate_host(request):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Host inválido"
                )

            # Validação de Path
            if not self._validate_path(request):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Recurso não encontrado",
                )

            # Validação de tamanho do conteúdo
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > self.max_content_length:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="Conteúdo muito grande",
                )

            # Validação de métodos HTTP
            if request.method not in ["GET", "POST", "PUT", "DELETE", "OPTIONS"]:
                raise HTTPException(
                    status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                    detail="Método não permitido",
                )

            response = await call_next(request)

            # Política CSP ajustada para carregar os recursos de /docs corretamente
            csp_policy = (
                "default-src 'self'; "
                "script-src 'self' cdn.jsdelivr.net; "
                "style-src 'self' cdn.jsdelivr.net; "
                "img-src 'self' data:; "
                "font-src 'self'; "
                "frame-ancestors 'none'; "
                "form-action 'self'"
            )

            # Cabeçalhos de segurança
            response.headers.update(
                {
                    "X-Frame-Options": "DENY",
                    "X-Content-Type-Options": "nosniff",
                    "X-XSS-Protection": "1; mode=block",
                    "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
                    "Content-Security-Policy": csp_policy,
                    "Cache-Control": "no-store, no-cache, must-revalidate, proxy-revalidate",
                    "Pragma": "no-cache",
                    "Expires": "0",
                    "Referrer-Policy": "strict-origin-when-cross-origin",
                    "Permissions-Policy": (
                        "accelerometer=(), camera=(), geolocation=(), gyroscope=(), "
                        "magnetometer=(), microphone=(), payment=(), usb=()"
                    ),
                }
            )

            # Remove cabeçalhos sensíveis de forma compatível com MutableHeaders
            if "server" in response.headers:
                del response.headers["server"]
            if "x-powered-by" in response.headers:
                del response.headers["x-powered-by"]

            return response

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro de segurança não tratado: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno de segurança",
            )

    def _validate_host(self, request: Request) -> bool:
        """Valida o cabeçalho Host contra a lista de hosts permitidos."""
        host = request.headers.get("host", "").split(":")[0]
        return host in self.allowed_hosts

    def _validate_path(self, request: Request) -> bool:
        """Valida o path da requisição contra padrões permitidos."""
        path = request.url.path
        for allowed_path in self.allowed_paths:
            if path.startswith(allowed_path):
                return True
        if ".." in path or "//" in path or re.search(r'[<>\'";]', path):
            return False
        return True
