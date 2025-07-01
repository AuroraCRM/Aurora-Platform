# src/aurora_platform/api/v1/api.py

from fastapi import APIRouter

# AURORA: As importações relativas foram substituídas por importações absolutas
# para maior clareza e robustez. Elas agora apontam para o diretório 'routers'
# que contém os módulos de roteamento.
from aurora_platform.routers import auth_router


api_router = APIRouter()

# Inclui os roteadores na API principal, cada um com seu prefixo e tags.
api_router.include_router(
    auth_router.router, prefix="/auth", tags=["Authentication"]
)
