from pydantic import BaseModel, Field, EmailStr
>>>>>>> e07c843 (Configuração inicial do repositório CRM-Q)
from typing import Optional, List
from datetime import datetime

class ClienteBase(BaseModel):
    razao_social: str
    nome_fantasia: Optional[str] = None
    cnpj: str
    inscricao_estadual: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[EmailStr] = None
    nome_fantasia: Optional[str] = None
    inscricao_estadual: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[EmailStr] = None

    id: int
    data_criacao: datetime
    data_atualizacao: Optional[datetime] = None
=======
class Cliente(ClienteBase):
    id: int
    data_criacao: datetime
    data_atualizacao: Optional[datetime] = None

    class Config:
        orm_mode = True
        from_attributes = True
>>>>>>> e07c843 (Configuração inicial do repositório CRM-Q)
