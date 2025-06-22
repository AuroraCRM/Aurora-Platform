# src/aurora/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from aurora.config import settings
from aurora.routers import auth_router, cliente_router, cnpj_routes, lead_router

# Cria a instância principal da aplicação FastAPI
# O título e a versão são carregados dinamicamente a partir do nosso sistema de configuração
app = FastAPI(
    title=settings.get("PROJECT_NAME", "Aurora Platform"),
    version=settings.get("PROJECT_VERSION", "1.0.0"),
    description="API central para a plataforma Aurora, gerenciando CRM, integrações e serviços de IA."
)

# --- Configuração de Middleware ---

# Configura o CORS (Cross-Origin Resource Sharing) para permitir que
# o frontend (ou outras aplicações) acessem a API a partir de diferentes origens.
# Em produção, a lista de 'origins' deve ser restrita aos domínios autorizados.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get("ALLOWED_ORIGINS", ["*"]),  # O '*' é permissivo demais para produção
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
app.include_router(cnpj_routes.router, prefix="/integracoes", tags=["Integrações Externas"])


# --- Endpoint Raiz ---

@app.get("/", tags=["Root"])
async def read_root():
    """
    Endpoint raiz que fornece uma mensagem de boas-vindas e a versão da API.
    Útil para health checks e para verificar se a API está online.
    """
    return {
        "message": f"Bem-vindo à {app.title}",
        "version": app.version
    }

# --- Eventos de Ciclo de Vida (Opcional) ---

@app.on_event("startup")
async def startup_event():
    """
    Função executada uma única vez na inicialização da aplicação.
    Útil para inicializar conexões (ex: pool de Redis) ou carregar modelos de IA.
    """
    print("INFO:     Aplicação Aurora iniciada com sucesso.")
    # Exemplo: conectar_ao_redis_pool()

@app.on_event("shutdown")
async def shutdown_event():
    """
    Função executada uma única vez no encerramento da aplicação.
    Útil para fechar conexões de forma graciosa.
    """
    print("INFO:     Aplicação Aurora encerrada.")
    # Exemplo: fechar_conexao_redis_pool()