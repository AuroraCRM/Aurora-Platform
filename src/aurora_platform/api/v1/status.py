from fastapi import APIRouter
from pydantic import BaseModel
import datetime

router = APIRouter()

class StatusResponse(BaseModel):
    status: str
    timestamp: str

@router.get("/status", response_model=StatusResponse)
async def get_status():
    """
    Retorna o status operacional da plataforma.
    """
    return StatusResponse(
        status="Operational",
        timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
    )
