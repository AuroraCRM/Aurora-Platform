# src/aurora/utils/security.py

import re
import hashlib
import secrets
import logging
import json
from typing import Any, Dict, Optional # Removido List, Union
from fastapi import Request, HTTPException, status
import html

logger = logging.getLogger(__name__)


class SecurityUtils:
    """Utilitários de segurança para proteção contra ataques comuns."""

    @staticmethod
    def sanitize_html(content: str) -> str:
        """
        Sanitiza conteúdo HTML para prevenir XSS.

        Args:
            content: Conteúdo HTML a ser sanitizado

        Returns:
            str: Conteúdo HTML sanitizado
        """
        return html.escape(content)

    @staticmethod
    def sanitize_sql(content: str) -> str:
        """
        Sanitiza conteúdo para prevenir SQL Injection.

        Args:
            content: Conteúdo a ser sanitizado

        Returns:
            str: Conteúdo sanitizado
        """
        # Remove caracteres potencialmente perigosos para SQL
        return re.sub(r"['\"\\;--]", "", content)

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitiza nomes de arquivos para prevenir path traversal.

        Args:
            filename: Nome do arquivo a ser sanitizado

        Returns:
            str: Nome do arquivo sanitizado
        """
        # Remove caracteres perigosos e limita o tamanho
        sanitized = re.sub(r'[\\/*?:"<>|]', "", filename)
        sanitized = re.sub(r"\.\.|\./", "", sanitized)
        return sanitized[:255]  # Limita a 255 caracteres

    @staticmethod
    def generate_csrf_token() -> str:
        """
        Gera um token CSRF seguro.

        Returns:
            str: Token CSRF
        """
        return secrets.token_hex(32)

    @staticmethod
    def verify_csrf_token(request_token: str, session_token: str) -> bool:
        """
        Verifica um token CSRF.

        Args:
            request_token: Token da requisição
            session_token: Token da sessão

        Returns:
            bool: True se o token for válido
        """
        if not request_token or not session_token:
            return False

        # Usa comparação de tempo constante para evitar timing attacks
        return secrets.compare_digest(request_token, session_token)

    @staticmethod
    def hash_data(data: str, salt: Optional[str] = None) -> Dict[str, str]:
        """
        Gera um hash seguro para dados sensíveis.

        Args:
            data: Dados a serem hasheados
            salt: Salt opcional

        Returns:
            Dict: Hash e salt utilizados
        """
        if not salt:
            salt = secrets.token_hex(16)

        # Usa SHA-256 para hash
        hash_obj = hashlib.sha256()
        hash_obj.update((data + salt).encode("utf-8"))
        hashed = hash_obj.hexdigest()

        return {"hash": hashed, "salt": salt}

    @staticmethod
    def validate_json(json_str: str) -> Dict[str, Any]:
        """
        Valida e sanitiza uma string JSON.

        Args:
            json_str: String JSON a ser validada

        Returns:
            Dict: Objeto JSON validado

        Raises:
            HTTPException: Se o JSON for inválido
        """
        try:
            # Tenta fazer o parse do JSON
            data = json.loads(json_str)

            # Verifica se é um dicionário
            if not isinstance(data, dict):
                raise ValueError("JSON deve ser um objeto")

            return data
        except json.JSONDecodeError as e:
            logger.warning(f"JSON inválido: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"JSON inválido: {str(e)}",
            )
        except ValueError as e:
            logger.warning(f"Erro de validação JSON: {str(e)}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    @staticmethod
    def detect_xss(content: str) -> bool:
        """
        Detecta possíveis ataques XSS.

        Args:
            content: Conteúdo a ser verificado

        Returns:
            bool: True se detectar possível XSS
        """
        # Padrões comuns de XSS
        xss_patterns = [
            r"<script.*?>",
            r"javascript:",
            r"onerror=",
            r"onload=",
            r"onclick=",
            r"onmouseover=",
            r"eval\(",
            r"document\.cookie",
            r"alert\(",
            r"String\.fromCharCode\(",
            r"&#x[0-9A-Fa-f]+;",
            r"&#[0-9]+;",
        ]

        for pattern in xss_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True

        return False

    @staticmethod
    def detect_sql_injection(content: str) -> bool:
        """
        Detecta possíveis ataques de SQL Injection.

        Args:
            content: Conteúdo a ser verificado

        Returns:
            bool: True se detectar possível SQL Injection
        """
        # Padrões comuns de SQL Injection
        sql_patterns = [
            r"(\s|^)SELECT(\s|$)",
            r"(\s|^)INSERT(\s|$)",
            r"(\s|^)UPDATE(\s|$)",
            r"(\s|^)DELETE(\s|$)",
            r"(\s|^)DROP(\s|$)",
            r"(\s|^)UNION(\s|$)",
            r"(\s|^)OR(\s|$).*?=",
            r"(\s|^)AND(\s|$).*?=",
            r"--",
            r"/\*.*?\*/",
            r";.*?$",
        ]

        for pattern in sql_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True

        return False

    @staticmethod
    async def validate_request_security(request: Request) -> None:
        """
        Valida a segurança de uma requisição HTTP.

        Args:
            request: Objeto de requisição

        Raises:
            HTTPException: Se detectar problemas de segurança
        """
        # Verifica o tamanho do corpo da requisição
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Conteúdo muito grande",
            )

        # Verifica o User-Agent
        user_agent = request.headers.get("user-agent", "")
        if not user_agent or len(user_agent) < 5:
            logger.warning(f"User-Agent suspeito: {user_agent}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="User-Agent inválido"
            )

        # Verifica o Content-Type para requisições POST/PUT
        if request.method in ["POST", "PUT"]:
            content_type = request.headers.get("content-type", "")
            if not content_type:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Content-Type não especificado",
                )

        # Verifica parâmetros de consulta
        for param, values in request.query_params.items():
            if SecurityUtils.detect_xss(param) or SecurityUtils.detect_xss(values):
                logger.warning(f"Possível XSS detectado em parâmetro: {param}={values}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parâmetro de consulta inválido",
                )

            if SecurityUtils.detect_sql_injection(
                param
            ) or SecurityUtils.detect_sql_injection(values):
                logger.warning(
                    f"Possível SQL Injection detectado em parâmetro: {param}={values}"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parâmetro de consulta inválido",
                )
