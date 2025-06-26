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
        # Lazily load the model on the first request to this endpoint
        # or ensure it's loaded if it hasn't been already.
        if phi3_handler.pipe is None:
            print("Phi-3 model not loaded yet. Loading now...")
            phi3_handler.load_model()
            print("Phi-3 model loaded.")

        response_text = phi3_handler.generate_text(
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
