from fastapi import APIRouter, Depends, HTTPException # Removido Body
from typing import Optional # Removido Dict, Any
from pydantic import ( # Movido para o topo
    BaseModel,
    Field as PydanticField,
)

from aurora_platform.services.code_assist_service import CodeAssistService

# Adicionar schemas Pydantic/SQLModel para entrada e saída se necessário
# Ex: from aurora_platform.schemas.code_assist_schemas import CodeAssistRequest, CodeAssistResponse

# Inicializar o router para a v1 da API de Code Assist
# O prefixo /api/v1 será adicionado no main.py ao incluir este router
router = APIRouter(
    prefix="/code-assist",  # Prefixo específico para este router
    tags=["Code Assistance AI"],  # Tag para a documentação da API (Swagger UI)
)

# --- Injeção de Dependência do Serviço ---
# O FastAPI pode injetar o serviço automaticamente se ele tiver dependências padrão (como settings)
# ou se for uma classe simples. Para configurações mais complexas, pode-se usar Depends com uma função factory.
# Aqui, vamos assumir que o CodeAssistService pode ser injetado diretamente ou com um Depends simples.
# Se o CodeAssistService precisar de 'settings' do Dynaconf, isso pode ser gerenciado
# na sua inicialização ou através de uma dependência que carrega as settings.


class CodeSuggestionRequest(BaseModel):
    language: str = PydanticField(
        ...,
        json_schema_extra={"example": "python"},
        description="Linguagem de programação do snippet.",
    )
    code_snippet: str = PydanticField(
        "",
        json_schema_extra={"example": "def hello():\n  "},
        description="Trecho de código atual.",
    )
    user_intent: Optional[str] = PydanticField(
        None,
        json_schema_extra={"example": "print hello world"},
        description="Intenção do usuário para o código.",
    )
    # Adicionar outros campos relevantes que o CodeAssistService.generate_code_suggestion espera no 'context'


class CodeSuggestionResponse(BaseModel):
    suggestion: str
    confidence: Optional[float] = None
    model_used: Optional[str] = None
    # Adicionar outros campos da resposta do serviço


@router.post("/suggest", response_model=CodeSuggestionResponse)
async def get_code_suggestion(
    request_data: CodeSuggestionRequest,  # Usa o schema para validar o corpo do request
    code_assist_service: CodeAssistService = Depends(
        CodeAssistService
    ),  # Injeta o serviço
):
    """
    Gera uma sugestão de código com base no contexto fornecido.
    """
    try:
        # O método do serviço espera um dicionário de contexto.
        # request_data.model_dump() converte o schema Pydantic para um dict.
        suggestion_result = await code_assist_service.generate_code_suggestion(
            request_data.model_dump()
        )

        # Mapear o resultado do serviço para o schema de resposta da API, se necessário.
        # Se CodeSuggestionResponse for idêntico ou um subconjunto do dict retornado,
        # a conversão direta funciona.
        return CodeSuggestionResponse(**suggestion_result)

    except Exception as e:
        # Em um cenário real, tratar exceções específicas do serviço de IA
        # e retornar códigos de erro HTTP apropriados.
        # Ex: se o modelo de IA não suportar a linguagem, retornar 4xx.
        # Se houver um erro interno no serviço de IA, retornar 5xx.
        raise HTTPException(
            status_code=500, detail=f"Erro ao gerar sugestão de código: {str(e)}"
        )


# Adicionar mais endpoints conforme necessário para o CodeAssistService
# Exemplo:
# @router.post("/complete", ...)
# async def complete_snippet(...): ...

# Este router precisa ser incluído no FastAPI app principal (main.py)
# Exemplo em main.py:
# from aurora_platform.api.v1 import code_assist_router as code_assist_v1_router
# app.include_router(code_assist_v1_router.router, prefix="/api/v1")
