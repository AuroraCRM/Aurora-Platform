# Recomendações de Melhorias de Segurança - Aurora Platform

Este documento apresenta recomendações específicas para melhorar a segurança da Aurora Platform, com base na auditoria realizada. As recomendações estão organizadas por prioridade e incluem exemplos de código para implementação.

## Melhorias de Alta Prioridade

### 1. Remover Credenciais Hardcoded

**Problema**: O arquivo `servico_crm.py` contém constantes para chaves de API que podem ser usadas para armazenar credenciais.

**Solução**: Mover todas as credenciais para variáveis de ambiente.

**Implementação**:

```python
# Antes
CNPJA_API_KEY_PRIMARY = None
CNPJA_API_KEY_SECONDARY = None

# Depois
from aurora.config import settings

# Remover as constantes e usar settings.CNPJA_API_KEY
```

### 2. Implementar Validação Adicional de Entrada

**Problema**: Alguns endpoints podem não ter validação suficiente de entrada, especialmente para dados de clientes.

**Solução**: Adicionar validadores Pydantic mais rigorosos e validação adicional nos endpoints.

**Implementação**:

```python
# Adicionar ao arquivo cliente_schemas.py
from pydantic import BaseModel, EmailStr, validator, constr
import re

class ClienteCreate(BaseModel):
    razao_social: constr(min_length=3, max_length=100)
    nome_fantasia: Optional[constr(max_length=100)] = None
    cnpj: constr(min_length=14, max_length=18)
    inscricao_estadual: Optional[constr(max_length=20)] = None
    telefone: Optional[constr(max_length=20)] = None
    email: Optional[EmailStr] = None
    site: Optional[constr(max_length=100)] = None
    segmento: Optional[constr(max_length=50)] = None
    observacoes: Optional[str] = None
    
    @validator('cnpj')
    def validate_cnpj(cls, v):
        # Remove caracteres não numéricos
        cnpj = re.sub(r'[^0-9]', '', v)
        if len(cnpj) != 14:
            raise ValueError('CNPJ deve ter 14 dígitos')
        # Adicionar validação de dígito verificador do CNPJ
        return v
    
    @validator('site')
    def validate_site(cls, v):
        if v and not (v.startswith('http://') or v.startswith('https://')):
            v = 'https://' + v
        return v
```

### 3. Padronizar Tratamento de Erros

**Problema**: Diferentes partes do código tratam erros de maneiras diferentes, o que pode levar a vazamento de informações.

**Solução**: Implementar um sistema centralizado de tratamento de erros.

**Implementação**:

```python
# Criar um novo arquivo: src/aurora/utils/error_handler.py

from fastapi import HTTPException, status
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class AppError(Exception):
    """Classe base para erros da aplicação."""
    
    def __init__(
        self, 
        message: str, 
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details
        super().__init__(self.message)

class NotFoundError(AppError):
    """Erro para recursos não encontrados."""
    
    def __init__(self, resource: str, resource_id: Any):
        super().__init__(
            message=f"{resource} com ID {resource_id} não encontrado",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="RESOURCE_NOT_FOUND",
            details={"resource": resource, "id": resource_id}
        )

class ValidationError(AppError):
    """Erro para validação de dados."""
    
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details={"field": field} if field else None
        )

class DuplicateError(AppError):
    """Erro para recursos duplicados."""
    
    def __init__(self, resource: str, field: str, value: Any):
        super().__init__(
            message=f"{resource} com {field} '{value}' já existe",
            status_code=status.HTTP_409_CONFLICT,
            error_code="DUPLICATE_RESOURCE",
            details={"resource": resource, "field": field, "value": value}
        )

def handle_app_error(error: AppError) -> HTTPException:
    """Converte AppError para HTTPException."""
    # Log do erro
    if error.status_code >= 500:
        logger.error(
            f"Erro interno: {error.message}",
            extra={"error_code": error.error_code, "details": error.details}
        )
    else:
        logger.info(
            f"Erro de cliente: {error.message}",
            extra={"error_code": error.error_code, "details": error.details}
        )
    
    # Retorna HTTPException
    return HTTPException(
        status_code=error.status_code,
        detail={
            "message": error.message,
            "error_code": error.error_code,
            "details": error.details
        }
    )
```

## Melhorias de Média Prioridade

### 1. Implementar Armazenamento Persistente para Tokens Revogados

**Problema**: Tokens revogados são armazenados em memória, o que não é persistente entre reinicializações.

**Solução**: Usar Redis para armazenar tokens revogados.

**Implementação**:

```python
# Modificar o arquivo auth/security.py

from aurora.cache.redis_cache import RedisCache

# Substituir o dicionário em memória
# revoked_tokens = {}

# Injetar o cache Redis
async def revoke_token(token: str, cache: RedisCache = Depends()) -> bool:
    """
    Revoga um token JWT.
    
    Args:
        token: Token JWT a ser revogado
        cache: Instância do cache Redis
        
    Returns:
        bool: True se o token foi revogado com sucesso
    """
    try:
        # Decodifica o token para obter o JTI e a expiração
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        jti = payload.get("jti")
        exp = payload.get("exp")
        
        if jti:
            # Armazena o JTI no Redis até sua expiração
            ttl = exp - datetime.utcnow().timestamp()
            if ttl > 0:
                await cache.set(f"revoked_token:{jti}", "1", expire=int(ttl))
                return True
    except Exception as e:
        logger.error(f"Erro ao revogar token: {str(e)}")
    
    return False

# Modificar a função get_current_user para verificar tokens revogados no Redis
async def get_current_user(
    request: Request, 
    token: str = Depends(oauth2_scheme),
    cache: RedisCache = Depends()
) -> Dict[str, Any]:
    # ...
    
    # Verifica se o token foi revogado
    is_revoked = await cache.get(f"revoked_token:{jti}")
    if is_revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token revogado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # ...
```

### 2. Adicionar Logs de Auditoria para Ações Sensíveis

**Problema**: Falta de logs de auditoria para ações sensíveis.

**Solução**: Implementar um sistema de logs de auditoria.

**Implementação**:

```python
# Criar um novo arquivo: src/aurora/utils/audit_log.py

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import Request, Depends
from aurora.auth.security import get_current_user

# Configurar logger específico para auditoria
audit_logger = logging.getLogger("aurora.audit")

class AuditLog:
    """Classe para registrar logs de auditoria."""
    
    def __init__(self):
        self.logger = audit_logger
    
    async def log_action(
        self,
        request: Request,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        current_user: Dict[str, Any] = None
    ):
        """
        Registra uma ação de auditoria.
        
        Args:
            request: Objeto de requisição
            action: Tipo de ação (create, read, update, delete)
            resource_type: Tipo de recurso (cliente, lead, etc.)
            resource_id: ID do recurso (opcional)
            details: Detalhes adicionais (opcional)
            current_user: Dados do usuário atual (opcional)
        """
        # Obter informações do usuário
        username = "anonymous"
        if current_user:
            username = current_user.get("username", "anonymous")
        
        # Obter informações da requisição
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("User-Agent", "unknown")
        method = request.method
        path = request.url.path
        
        # Criar log estruturado
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "username": username,
            "client_ip": client_ip,
            "user_agent": user_agent,
            "method": method,
            "path": path,
            "details": details
        }
        
        # Registrar log
        self.logger.info(json.dumps(log_data))

# Instância global
audit_log = AuditLog()
```

### 3. Implementar Escaneamento Automático de Imagens Docker

**Problema**: Falta de escaneamento automático de imagens Docker para vulnerabilidades.

**Solução**: Adicionar escaneamento de imagens Docker ao pipeline CI/CD.

**Implementação**:

```yaml
# Adicionar ao arquivo .github/workflows/security-checks.yml

name: Security Checks

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  schedule:
    - cron: '0 0 * * 0'  # Executa todo domingo à meia-noite

jobs:
  docker-scan:
    name: Docker Image Scan
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Build Docker image
        run: docker build -t aurora-platform:test .

      - name: Scan Docker image
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'aurora-platform:test'
          format: 'table'
          exit-code: '1'
          ignore-unfixed: true
          severity: 'CRITICAL,HIGH'
```

## Melhorias de Baixa Prioridade

### 1. Adicionar Testes de Segurança Automatizados

**Problema**: Falta de testes específicos para segurança.

**Solução**: Implementar testes de segurança automatizados.

**Implementação**:

```python
# Criar um novo arquivo: tests/security/test_security.py

import pytest
from fastapi.testclient import TestClient
import jwt
from datetime import datetime, timedelta

from aurora.main import app
from aurora.config import settings
from aurora.auth.security import create_access_token

client = TestClient(app)

def test_invalid_token():
    """Testa acesso com token inválido."""
    response = client.get(
        "/api/v1/clientes/",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401

def test_expired_token():
    """Testa acesso com token expirado."""
    # Cria token expirado
    data = {"sub": "testuser", "scopes": ["user"]}
    expires = datetime.utcnow() - timedelta(minutes=1)
    token = create_access_token(data, expires_delta=expires - datetime.utcnow())
    
    response = client.get(
        "/api/v1/clientes/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401
    assert "expirado" in response.json()["detail"].lower()

def test_insufficient_permissions():
    """Testa acesso com permissões insuficientes."""
    # Cria token sem permissões de admin
    data = {"sub": "testuser", "scopes": ["user"]}
    token = create_access_token(data)
    
    response = client.get(
        "/api/v1/admin/clientes/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403

def test_sql_injection_protection():
    """Testa proteção contra SQL Injection."""
    # Tenta injetar SQL na consulta
    response = client.get(
        "/api/v1/clientes/?search=test' OR '1'='1",
        headers={"Authorization": f"Bearer {valid_token()}"}
    )
    assert response.status_code != 500

def test_xss_protection():
    """Testa proteção contra XSS."""
    # Tenta injetar script
    payload = {
        "razao_social": "<script>alert('XSS')</script>",
        "cnpj": "12345678901234"
    }
    response = client.post(
        "/api/v1/clientes/",
        json=payload,
        headers={"Authorization": f"Bearer {valid_token()}"}
    )
    assert response.status_code == 422  # Deve falhar na validação

def valid_token():
    """Helper para criar um token válido para testes."""
    data = {"sub": "testuser", "scopes": ["admin", "user"]}
    return create_access_token(data)
```

### 2. Implementar Rotação Automática de Segredos

**Problema**: Falta de rotação automática de segredos.

**Solução**: Implementar um sistema de rotação automática de segredos.

**Implementação**:

```python
# Criar um novo arquivo: src/aurora/utils/secret_rotation.py

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
import json
import asyncio

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

from aurora.config import settings

logger = logging.getLogger(__name__)

class SecretRotator:
    """Classe para rotação automática de segredos."""
    
    def __init__(self):
        self.credential = DefaultAzureCredential()
        self.secret_client = SecretClient(
            vault_url=settings.AZURE_KEYVAULT_URL,
            credential=self.credential
        )
        self.metadata_file = "secret_rotation_metadata.json"
    
    async def rotate_if_needed(self, secret_name: str, rotation_days: int = 90):
        """
        Verifica se um segredo precisa ser rotacionado e o rotaciona se necessário.
        
        Args:
            secret_name: Nome do segredo
            rotation_days: Dias para rotação
        """
        try:
            # Verifica se o segredo precisa ser rotacionado
            if self._needs_rotation(secret_name, rotation_days):
                # Implementa a lógica específica de rotação para cada tipo de segredo
                if secret_name == "jwt-secret-key":
                    await self._rotate_jwt_secret()
                elif secret_name == "cnpja-api-key":
                    await self._rotate_cnpja_api_key()
                else:
                    logger.warning(f"Rotação não implementada para o segredo: {secret_name}")
        except Exception as e:
            logger.error(f"Erro ao rotacionar segredo {secret_name}: {str(e)}")
    
    def _needs_rotation(self, secret_name: str, rotation_days: int) -> bool:
        """Verifica se um segredo precisa ser rotacionado."""
        try:
            # Carrega os metadados de rotação
            metadata = self._load_rotation_metadata()
            
            # Verifica a última rotação
            last_rotation = metadata.get(secret_name, {}).get("last_rotation")
            if not last_rotation:
                return True
            
            # Converte para datetime
            last_rotation_date = datetime.fromisoformat(last_rotation)
            
            # Verifica se passou o tempo de rotação
            return datetime.utcnow() > last_rotation_date + timedelta(days=rotation_days)
        except Exception as e:
            logger.error(f"Erro ao verificar rotação para {secret_name}: {str(e)}")
            return False
    
    async def _rotate_jwt_secret(self):
        """Rotaciona a chave secreta JWT."""
        try:
            # Gera nova chave
            new_secret = os.urandom(32).hex()
            
            # Armazena no Key Vault
            self.secret_client.set_secret("jwt-secret-key", new_secret)
            
            # Atualiza os metadados
            self._update_rotation_metadata("jwt-secret-key")
            
            logger.info("Chave JWT rotacionada com sucesso")
        except Exception as e:
            logger.error(f"Erro ao rotacionar chave JWT: {str(e)}")
    
    async def _rotate_cnpja_api_key(self):
        """
        Rotaciona a chave da API CNPJá.
        Nota: Esta é uma implementação de exemplo. Na prática, você precisaria
        integrar com a API do provedor para gerar uma nova chave.
        """
        logger.info("Rotação de chave CNPJá requer intervenção manual")
        # Enviar notificação para equipe de operações
    
    def _load_rotation_metadata(self) -> Dict[str, Any]:
        """Carrega os metadados de rotação."""
        try:
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, "r") as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Erro ao carregar metadados de rotação: {str(e)}")
            return {}
    
    def _update_rotation_metadata(self, secret_name: str):
        """Atualiza os metadados de rotação."""
        try:
            metadata = self._load_rotation_metadata()
            
            if secret_name not in metadata:
                metadata[secret_name] = {}
            
            metadata[secret_name]["last_rotation"] = datetime.utcnow().isoformat()
            
            with open(self.metadata_file, "w") as f:
                json.dump(metadata, f)
        except Exception as e:
            logger.error(f"Erro ao atualizar metadados de rotação: {str(e)}")

# Função para executar a rotação periódica
async def run_secret_rotation():
    """Executa a rotação periódica de segredos."""
    rotator = SecretRotator()
    
    while True:
        try:
            # Verifica e rotaciona segredos
            await rotator.rotate_if_needed("jwt-secret-key", 90)
            await rotator.rotate_if_needed("cnpja-api-key", 180)
            
            # Aguarda 24 horas
            await asyncio.sleep(86400)
        except Exception as e:
            logger.error(f"Erro no processo de rotação de segredos: {str(e)}")
            await asyncio.sleep(3600)  # Tenta novamente em 1 hora
```

### 3. Reforçar a Política de CSP

**Problema**: A política de CSP poderia ser mais restritiva.

**Solução**: Implementar uma política de CSP mais restritiva.

**Implementação**:

```python
# Modificar o arquivo middleware/security.py

# Substituir a política de CSP atual por uma mais restritiva
"Content-Security-Policy": (
    "default-src 'none'; "
    "script-src 'self'; "
    "connect-src 'self'; "
    "img-src 'self' data:; "
    "style-src 'self'; "
    "font-src 'self'; "
    "frame-ancestors 'none'; "
    "form-action 'self'; "
    "base-uri 'self'; "
    "manifest-src 'self'"
)
```

## Conclusão

Implementar estas melhorias de segurança fortalecerá significativamente a postura de segurança da Aurora Platform. Recomenda-se priorizar as melhorias de alta prioridade, seguidas pelas de média e baixa prioridade.

É importante lembrar que a segurança é um processo contínuo, e novas vulnerabilidades podem surgir com o tempo. Portanto, é essencial realizar auditorias de segurança regulares e manter-se atualizado sobre as melhores práticas de segurança.

---

**Autor**: [NOME DO AUTOR]

**Data**: [DATA ATUAL]