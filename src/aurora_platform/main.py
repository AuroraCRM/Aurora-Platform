# src/aurora/main.py

from typing import cast, Dict, Any, Callable

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from aurora_platform.config import settings
from aurora_platform.routers import (
    auth_router,
    cliente_router,
    cnpj_routes,
    lead_router,
)
from contextlib import asynccontextmanager
from aurora_platform.middleware.error_handler import http_exception_handler


# --- Lifespan para Startup e Shutdown ---
@asynccontextmanager
async def lifespan(
    app_instance: FastAPI,
):
    print("INFO:     Aplicação Aurora iniciando (via lifespan)...")
    yield
    print("INFO:     Aplicação Aurora encerrando (via lifespan)...")


# Cria a instância principal da aplicação FastAPI
app = FastAPI(
    title=str(cast(Dict[str, Any], settings).get("PROJECT_NAME", "Aurora Platform")),
    version=str(cast(Dict[str, Any], settings).get("PROJECT_VERSION", "1.0.0")),
    description="API central para a plataforma Aurora, gerenciando CRM, integrações e serviços de IA.",
    lifespan=lifespan,
)

app.add_exception_handler(Exception, http_exception_handler)


# --- Configuração de Middleware ---

app.add_middleware(
    CORSMiddleware,
    allow_origins=cast(Dict[str, Any], settings).get(
        "ALLOWED_ORIGINS", ["*"]
    ),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from aurora_platform.middleware.security import SecurityHeadersMiddleware

app.add_middleware(SecurityHeadersMiddleware)

# --- Inclusão dos Roteadores Modulares ---

app.include_router(auth_router.router, prefix="/auth", tags=["Autenticação"])
app.include_router(cliente_router.router, prefix="/clientes", tags=["Clientes CRM"])
app.include_router(lead_router.router, prefix="/leads", tags=["Leads CRM"])
app.include_router(
    cnpj_routes.router, prefix="/integracoes", tags=["Integrações Externas"]
)

# --- Inclusão dos Roteadores da API v1 (Módulos de IA) ---
from aurora_platform.api.v1 import code_assist_router as code_assist_v1_router
from aurora_platform.api.v1 import inference_router as inference_v1_router

app.include_router(
    code_assist_v1_router.router, prefix="/api/v1", tags=["IA Services v1"]
)
app.include_router(
    inference_v1_router.router, prefix="/api/v1", tags=["IA Services v1"]
)


# --- Endpoint Raiz ---


@app.get("/", tags=["Root"])
async def read_root():
    """
    Endpoint raiz que fornece uma mensagem de boas-vindas e a versão da API.
    Útil para health checks e para verificar se a API está online.
    """
    return {
        "message": "Bem-vindo à Aurora Platform",
        "version": app.version,
        "docs_url": "/docs",
    }
