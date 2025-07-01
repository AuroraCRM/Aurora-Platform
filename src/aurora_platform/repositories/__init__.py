# Versão Corrigida para:
# src/aurora_platform/repositories/__init__.py

from .cliente_repository import ClienteRepository
from .usuario_repository import UsuarioRepository

# O __all__ define a API pública deste pacote de repositórios.
__all__ = [
    "ClienteRepository",
    "UsuarioRepository",
]