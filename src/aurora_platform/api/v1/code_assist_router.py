# src/aurora_platform/api/v1/code_assist_router.py
from fastapi import APIRouter, Depends, HTTPException, status # <-- Adicionado 'status'
from pydantic import BaseModel
from typing import Optional # Adicionar import opcional

# Importando o serviço que criamos anteriormente
# Assumindo que este serviço será movido para aurora_platform.services
# e que usará o Google Vertex AI
from aurora_platform.services.code_assist_service import CodeAssistService 

# Cria um novo roteador que será incluído na API principal
router = APIRouter(
    prefix="/assist",
    tags=["AI Assistance"],
)

class FimRequest(BaseModel):
    """Defines the request model for a Fill-in-the-Middle request."""
    code_with_fim: str
    # Podemos adicionar outros parâmetros no futuro, como 'model_preference'
    
class FimResponse(BaseModel):
    """Defines the response model for a completion."""
    completed_code: str

# AQUI ESTAVA O ERRO DE INDENTAÇÃO OU SINTAXE.
# Garanta que esta função esteja corretamente indentada e formatada.
@router.post("/fim", response_model=FimResponse)
async def get_fim_assistance(
    request: FimRequest,
    service: CodeAssistService = Depends(CodeAssistService)
):
    """
    Receives code with FIM tokens and returns the AI-completed code.
    This endpoint leverages the CodeAssistService to communicate with an
    external AI model (like DeepSeek or Vertex AI).
    """
    try:
        # Aqui chamaria o serviço para obter a complicação da IA
        # Supondo que service.assist_with_fim exista e retorne uma string
        completion = await service.generate_completion(
            code=request.code_with_fim
        )
        return FimResponse(completed_code=completion)
    except HTTPException as e:
        # Re-lança exceções HTTP que o serviço possa ter gerado
        raise e
    except Exception as e:
        # Captura qualquer outro erro inesperado
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An internal error occurred: {e}")