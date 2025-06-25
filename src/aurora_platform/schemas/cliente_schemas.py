from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional # Removido List
from datetime import datetime


class ClienteBase(BaseModel):
    razao_social: str
    nome_fantasia: Optional[str] = None
    cnpj: str
    inscricao_estadual: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[EmailStr] = None
    email_secundario: Optional[str] = None
    site: Optional[str] = None
    segmento: Optional[str] = None
    observacoes: Optional[str] = None


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(BaseModel):
    razao_social: Optional[str] = None
    nome_fantasia: Optional[str] = None
    inscricao_estadual: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[EmailStr] = None
    email_secundario: Optional[str] = None
    site: Optional[str] = None
    segmento: Optional[str] = None
    observacoes: Optional[str] = None


class ClienteRead(ClienteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    data_criacao: datetime
    data_atualizacao: Optional[datetime] = None


# Alias para compatibilidade com código existente
Cliente = ClienteRead
