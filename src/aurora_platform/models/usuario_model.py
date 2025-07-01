from typing import Optional, TYPE_CHECKING # Removido List
from sqlmodel import Field, SQLModel, Relationship, Column, String as SQLString

if TYPE_CHECKING:
    from .cliente_model import Cliente  # Necessário para o type hint do relacionamento


class Usuario(SQLModel, table=True):
    __tablename__ = "usuarios"  # type: ignore

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    nome: Optional[str] = Field(default=None, sa_column=Column(SQLString(100)))
    email: str = Field(
        sa_column=Column(SQLString(100), unique=True, index=True, nullable=False)
    )
    hashed_password: str = Field(sa_column=Column(SQLString, nullable=False))
    is_active: bool = Field(default=True, nullable=False)

    cliente_id: Optional[int] = Field(
        default=None, foreign_key="clientes.id", nullable=True
    )  # Pode ser nulo se um usuário não estiver ligado a um cliente específico (ex: admin global)

    # Relacionamento: Um usuário pode pertencer a um cliente
    cliente: Optional["Cliente"] = Relationship(back_populates="usuarios")

    hashed_refresh_token: Optional[str] = Field(default=None, sa_column=Column(SQLString))

    # Adicionar outros campos relevantes para o usuário, se necessário, como:
    # is_superuser: bool = Field(default=False, nullable=False)
    # data_criacao: Optional[datetime] = Field(...)
    # data_atualizacao: Optional[datetime] = Field(...)
