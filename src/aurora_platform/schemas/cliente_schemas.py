# Caminho: C:\Users\winha\Aurora\Aurora-Platform\src\aurora_platform\schemas\cliente_schemas.py

from pydantic import BaseModel, EmailStr
from typing import Optional


class ClienteCreate(BaseModel):
    nome: str
    email: EmailStr
    telefone: Optional[str] = None
    cnpj: Optional[str] = None


class ClienteResponse(BaseModel):
    id: int
    nome: str
    email: EmailStr
    telefone: Optional[str] = None
    cnpj: Optional[str] = None

    class Config:
        from_attributes = True


class ClienteUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    cnpj: Optional[str] = None
