from typing import Optional
from sqlmodel import SQLModel, Field


# Propriedades compartilhadas por todos os schemas relacionados ao usuário
class UsuarioBase(SQLModel):
    email: str = Field(unique=True, index=True, nullable=False)
    nome: Optional[str] = Field(default=None)
    is_active: bool = True
    cliente_id: Optional[int] = Field(default=None, foreign_key="clientes.id")


# Propriedades para receber na criação do usuário via API
class UsuarioCreate(UsuarioBase):
    password: str  # Senha em texto plano


# Propriedades contidas no modelo do BD mas não em UsuarioBase
class UsuarioInDBBase(UsuarioBase):
    id: int
    hashed_password: str


# Propriedades para retornar ao cliente (não inclui hashed_password)
class UsuarioRead(SQLModel):
    id: int
    email: str
    nome: Optional[str]
    is_active: bool
    cliente_id: Optional[int]


# Propriedades para atualizar um usuário
class UsuarioUpdate(SQLModel):
    email: Optional[str] = Field(default=None)
    nome: Optional[str] = Field(default=None)
    password: Optional[str] = Field(default=None)  # Para atualização de senha
    is_active: Optional[bool] = Field(default=None)
    cliente_id: Optional[int] = Field(default=None)


# Schema adicional que pode ser usado pelo repositório para criação interna
# onde a senha já está hasheada.
class UsuarioCreateRepo(UsuarioBase):
    hashed_password: str
