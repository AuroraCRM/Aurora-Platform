from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handles HTTPException, returning a standardized JSON response.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
"detail": exc.detail
},
    )

async def generic_exception_handler(request: Request, exc: Exception):
    """
    Handles all other exceptions, returning a generic error message
    and logging the full traceback for internal debugging.
    """
    logger.exception(f"Unhandled exception for request: {request.url}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
"detail": "An unexpected error occurred."
},
    )