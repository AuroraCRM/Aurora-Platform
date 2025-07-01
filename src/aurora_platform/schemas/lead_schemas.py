# src/aurora/schemas/lead_schemas.py

from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import Union
from datetime import datetime


class LeadBase(BaseModel):
    nome: str
    email: EmailStr
    telefone: Union[str, None] = Field(default=None)
    empresa: Union[str, None] = Field(default=None)
    cargo: Union[str, None] = Field(default=None)
    origem: Union[str, None] = Field(default=None)
    interesse: Union[str, None] = Field(default=None)
    observacoes: Union[str, None] = Field(default=None)


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    nome: Union[str, None] = Field(default=None)
    email: Union[EmailStr, None] = Field(default=None)
    telefone: Union[str, None] = Field(default=None)
    empresa: Union[str, None] = Field(default=None)
    cargo: Union[str, None] = Field(default=None)
    origem: Union[str, None] = Field(default=None)
    interesse: Union[str, None] = Field(default=None)
    observacoes: Union[str, None] = Field(default=None)
    status: Union[str, None] = Field(default=None)


class LeadRead(LeadBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    data_criacao: datetime
    data_atualizacao: Union[datetime, None] = Field(default=None)
