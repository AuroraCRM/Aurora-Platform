# src/aurora/main.py

import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Importa os middlewares
from aurora.middleware.error_handler import error_handler_middleware
from aurora.middleware.security import SecurityHeadersMiddleware
from aurora.middleware.rate_limiter import RateLimiter

# Importa os roteadores
from aurora.routers import cnpj_routes, cliente_router, lead_router, auth_router

# Importa o módulo de autenticação
from aurora.auth.security import get_current_user
from aurora.auth.two_factor import require_2fa

# Carrega variáveis de ambiente do arquivo .env na raiz do projeto
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '.env'))

# Instância principal do FastAPI
app = FastAPI(
    title="Aurora CRM API",
    description="API para a Plataforma Aurora CRM e Suporte a Vendas",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configuração de CORS - Restringindo origens permitidas
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://aurora-crm.example.com"],  # Restringe origens permitidas
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Restringe métodos permitidos
    allow_headers=["Authorization", "Content-Type"],  # Restringe cabeçalhos permitidos
    expose_headers=["X-Request-ID"],
    max_age=600,  # Cache por 10 minutos
)

# Adiciona o middleware de segurança
app.add_middleware(SecurityHeadersMiddleware)

# Adiciona o middleware de limitação de taxa
app.add_middleware(RateLimiter, requests_per_minute=60)

# Registra o middleware de erro na aplicação
app.middleware("http")(error_handler_middleware)

# Inclui os roteadores na aplicação
# Rotas de autenticação
app.include_router(auth_router.router, prefix="/api/v1/auth", tags=["Autenticação"])

# Rotas públicas
app.include_router(cnpj_routes.router, prefix="/api/v1", tags=["CNPJ"])

# Rotas protegidas por autenticação
app.include_router(
    cliente_router.router, 
    prefix="/api/v1", 
    tags=["Clientes"],
    dependencies=[Depends(get_current_user)]  # Protege todas as rotas de clientes
)

app.include_router(
    lead_router.router, 
    prefix="/api/v1", 
    tags=["Leads"],
    dependencies=[Depends(get_current_user)]  # Protege todas as rotas de leads
)

# Rotas administrativas com 2FA
admin_router = FastAPI()
app.mount("/api/v1/admin", admin_router)
admin_router.include_router(
    cliente_router.router,
    prefix="/clientes",
    tags=["Admin - Clientes"],
    dependencies=[Depends(require_2fa)]  # Requer 2FA para acesso
)

@app.get("/")
async def read_root():
    return {
        "message": "Bem-vindo à API da Aurora CRM!",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "ok"}