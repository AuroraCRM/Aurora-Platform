# src/aurora/middleware/error_handler.py

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import logging
from uuid import uuid4

logger = logging.getLogger(__name__)

async def error_handler_middleware(request: Request, call_next):
    """
    Middleware para tratamento centralizado de exceções.
    Captura exceções, registra logs estruturados e retorna respostas JSON padronizadas.
    """
    # Gera um ID único para cada requisição para facilitar o rastreamento nos logs
    request_id = str(uuid4())
    request.state.request_id = request_id
    
    try:
        response = await call_next(request)
        return response
    except RequestValidationError as e:
        # Erro específico para falhas de validação do Pydantic
        logger.warning(f"Erro de validação: {str(e)}", extra={"request_id": request_id})
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": "Dados inválidos", "errors": e.errors()}
        )
    except SQLAlchemyError as e:
        # Erro específico para problemas com o banco de dados
        logger.error(f"Erro de banco de dados: {str(e)}", extra={"request_id": request_id})
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Ocorreu um erro ao processar sua solicitação em nosso banco de dados."}
        )
    except Exception as e:
        # Captura genérica para qualquer outra exceção não tratada
        logger.error(f"Erro não tratado: {str(e)}", extra={"request_id": request_id}, exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Ocorreu um erro interno inesperado no servidor."}
        )