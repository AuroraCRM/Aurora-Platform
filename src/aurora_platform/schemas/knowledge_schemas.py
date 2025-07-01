# src/aurora_platform/schemas/knowledge_schemas.py

from pydantic import BaseModel, Field
from typing import List, Dict, Any

class DocumentCreate(BaseModel):
    doc_text: str
    doc_id: str
    metadata: Dict[str, Any]

class KnowledgeQuery(BaseModel):
    query_text: str
    n_results: int = Field(default=3, json_schema_extra={"description": "Número de resultados a serem retornados", "example": 3})

class SearchResult(BaseModel):
    results: List[str]
    