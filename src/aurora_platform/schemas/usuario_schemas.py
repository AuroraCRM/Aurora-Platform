from typing import Optional
from sqlmodel import SQLModel, Field


# Propriedades compartilhadas por todos os schemas relacionados ao usuário
class UsuarioBase(SQLModel):
    email: str = Field(unique=True, index=True, nullable=False)
    nome: Optional[str] = None
    is_active: bool = True
    cliente_id: Optional[int] = Field(default=None, foreign_key="clientes.id")


# Propriedades para receber na criação do usuário via API
class UsuarioCreate(UsuarioBase):
    password: str  # Senha em texto plano


# Propriedades contidas no modelo do BD mas não em UsuarioBase
class UsuarioInDBBase(UsuarioBase):
    id: int
    hashed_password: str


from pydantic import ConfigDict # Adicionar import

# Propriedades para retornar ao cliente (não inclui hashed_password)
class UsuarioRead(UsuarioBase):
    model_config = ConfigDict(from_attributes=True) # Adicionado
    id: int


# Propriedades para atualizar um usuário
class UsuarioUpdate(SQLModel):
    email: Optional[str] = None
    nome: Optional[str] = None
    password: Optional[str] = None  # Para atualização de senha
    is_active: Optional[bool] = None
    cliente_id: Optional[int] = None


# Schema adicional que pode ser usado pelo repositório para criação interna
# onde a senha já está hasheada.
class UsuarioCreateRepo(UsuarioBase):
    hashed_password: str
