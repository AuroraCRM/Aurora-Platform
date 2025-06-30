# src/aurora_platform/routers/inference_router.py

from fastapi import APIRouter, HTTPException, Body
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from aurora_platform.models import phi3_handler
from aurora_platform.schemas.inference_schemas import Phi3PromptRequest, Phi3Response

router = APIRouter()

@router.post("/inference/phi3", response_model=Phi3Response, tags=["Inference"])
async def run_phi3_inference(
    request_data: Phi3PromptRequest = Body(...)
):
    """
    Receives a prompt and returns a response from the Phi-3 model.
    """
    try:
        phi3_instance = phi3_handler.Phi3Handler()
        response_text = phi3_instance.generate_response(
            prompt=request_data.prompt,
            max_new_tokens=request_data.max_new_tokens
        )
        return Phi3Response(response=response_text)
    except Exception as e:
        # Log the exception details for debugging
        print(f"Error during Phi-3 inference: {str(e)}")
        # Optionally, include more detailed error information if appropriate
        # import traceback
        # print(traceback.format_exc())
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get response from Phi-3 model: {str(e)}"
        )

@router.get("/inference/phi3/status", tags=["Inference"])
async def get_phi3_status():
    """
    Returns the current status of the Phi-3 model (loaded or not).
    """
    return {"status": "Phi-3 inference endpoint is available."}