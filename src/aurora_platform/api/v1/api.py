# src/aurora_platform/api/v1/api.py

from fastapi import APIRouter
from .endpoints import auth_router, users_router
# --- ADIÇÃO 1: Importe o novo roteador ---
from . import knowledge_router

api_router = APIRouter()

# Inclui os roteadores existentes
api_router.include_router(auth_router.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users_router.router, prefix="/users", tags=["Users"])
# --- ADIÇÃO 2: Inclua o novo roteador na API ---
api_router.include_router(knowledge_router.router)