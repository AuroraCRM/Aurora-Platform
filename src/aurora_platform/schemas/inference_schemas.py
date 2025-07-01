# src/aurora_platform/schemas/inference_schemas.py

from pydantic import BaseModel, Field

class Phi3PromptRequest(BaseModel):
    prompt: str = Field(..., json_schema_extra={"example": "Explique o que é um Large Language Model em português."})
    max_new_tokens: int = Field(default=250, gt=0, le=1024, json_schema_extra={"example": 100})

class Phi3Response(BaseModel):
    response: str
