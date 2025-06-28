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
phi3_handler_instance = Phi3Handler()

@router.post("/suggest", response_model=CodeSuggestionResponse)
async def get_code_suggestion(
    request_data: CodeSuggestionRequest,
):
    """
    Gera uma sugestão de código com base no contexto fornecido usando o modelo Phi-3.
    """
    try:
        prompt = f"Language: {request_data.language}\nCode: {request_data.code_snippet}\nIntent: {request_data.user_intent}\n\nProvide a code suggestion:"
        
        suggestion = phi3_handler_instance.generate_response(prompt)

        return CodeSuggestionResponse(suggestion=suggestion, model_used=phi3_handler_instance.model_name)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating code suggestion with Phi-3: {str(e)}"
        )


# Adicionar mais endpoints conforme necessário para o CodeAssistService
# Exemplo:
# @router.post("/complete", ...)
# async def complete_snippet(...): ...

# Este router precisa ser incluído no FastAPI app principal (main.py)
# Exemplo em main.py:
# from aurora_platform.api.v1 import code_assist_router as code_assist_v1_router
# app.include_router(code_assist_v1_router.router, prefix="/api/v1")
