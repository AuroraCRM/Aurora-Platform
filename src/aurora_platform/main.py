# src/aurora/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from aurora_platform.config import settings
from aurora_platform.routers import (
    auth_router,
    cliente_router,
    cnpj_routes,
    lead_router,
)
from contextlib import asynccontextmanager  # Mover import para o topo
# Removida a re-importação de FastAPI


# --- Lifespan para Startup e Shutdown ---
@asynccontextmanager
async def lifespan(
    app_instance: FastAPI,
):  # Renomeado app para app_instance para evitar sombreamento
    # Código de startup aqui
    print("INFO:     Aplicação Aurora iniciando (via lifespan)...")
    # Exemplo: await conectar_ao_redis_pool()
    yield
    # Código de shutdown aqui
    print("INFO:     Aplicação Aurora encerrando (via lifespan)...")
    # Exemplo: await fechar_conexao_redis_pool()


# Cria a instância principal da aplicação FastAPI
# O título e a versão são carregados dinamicamente a partir do nosso sistema de configuração
app = FastAPI(
    title=settings.get("PROJECT_NAME", "Aurora Platform"),
    version=settings.get("PROJECT_VERSION", "1.0.0"),
    description="API central para a plataforma Aurora, gerenciando CRM, integrações e serviços de IA.",
    lifespan=lifespan,  # Agora lifespan está definido
)

# --- Configuração de Middleware ---

# Configura o CORS (Cross-Origin Resource Sharing) para permitir que
# o frontend (ou outras aplicações) acessem a API a partir de diferentes origens.
# Em produção, a lista de 'origins' deve ser restrita aos domínios autorizados.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get(
        "ALLOWED_ORIGINS", ["*"]
    ),  # O '*' é permissivo demais para produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Aqui poderiam ser adicionados outros middlewares, como o de tratamento de erros
# ou de rate limiting, caso fossem implementados como tal.


# --- Inclusão dos Roteadores Modulares ---

# A arquitetura é mantida limpa e modular incluindo os roteadores de cada domínio.
# Cada roteador gerencia um conjunto específico de endpoints.
app.include_router(auth_router.router, prefix="/auth", tags=["Autenticação"])
app.include_router(cliente_router.router, prefix="/clientes", tags=["Clientes CRM"])
app.include_router(lead_router.router, prefix="/leads", tags=["Leads CRM"])
app.include_router(
    cnpj_routes.router, prefix="/integracoes", tags=["Integrações Externas"]
)

# --- Inclusão dos Roteadores da API v1 (Módulos de IA) ---
from aurora_platform.api.v1 import code_assist_router as code_assist_v1_router

app.include_router(
    code_assist_v1_router.router, prefix="/api/v1", tags=["IA Services v1"]
)


# --- Endpoint Raiz ---


@app.get("/", tags=["Root"])
async def read_root():
    """
    Endpoint raiz que fornece uma mensagem de boas-vindas e a versão da API.
    Útil para health checks e para verificar se a API está online.
    """
    # Ajustado conforme diretiva para incluir docs_url e mensagem fixa
    return {
        "message": "Bem-vindo à Aurora Platform",  # app.title deve ser "Aurora Platform"
        "version": app.version,  # app.version deve ser "1.0.0"
        "docs_url": "/docs",
    }


# A função lifespan já foi movida para cima. Esta remoção é dos antigos @app.on_event
# que estavam no final do arquivo e foram substituídos pela função lifespan.
# Se o bloco SEARCH não encontrar nada, significa que a limpeza já foi feita
# na substituição anterior que moveu e definiu a função lifespan.
