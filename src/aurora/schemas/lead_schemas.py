# src/aurora/schemas/lead_schemas.py

from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime

class LeadBase(BaseModel):
    nome: str
    email: EmailStr
    telefone: Optional[str] = None
    empresa: Optional[str] = None
    cargo: Optional[str] = None
    origem: Optional[str] = None
    interesse: Optional[str] = None
    observacoes: Optional[str] = None

class LeadCreate(LeadBase):
    pass

class LeadUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    empresa: Optional[str] = None
    cargo: Optional[str] = None
    origem: Optional[str] = None
    interesse: Optional[str] = None
    observacoes: Optional[str] = None
    status: Optional[str] = None

class LeadRead(LeadBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    status: str
    data_criacao: datetime
    data_atualizacao: Optional[datetime] = None