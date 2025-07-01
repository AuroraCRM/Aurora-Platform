from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

from sqlmodel import (
    Field,
    SQLModel,
    Column,
    String as SQLString,
    Text as SQLText,
    DateTime as SQLDateTime,
    Relationship,
)  # Adicionado Relationship
from sqlalchemy.sql import func

if TYPE_CHECKING:
    from .usuario_model import Usuario  # Necessário para o type hint do relacionamento


class Cliente(SQLModel, table=True):
    __tablename__: str = "clientes" # type: ignore

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    # ... (outros campos existentes)

    # Relacionamento: Um cliente pode ter múltiplos usuários
    usuarios: List["Usuario"] = Relationship(back_populates="cliente")
    razao_social: str = Field(sa_column=Column(SQLString(100), nullable=False))
    nome_fantasia: Optional[str] = Field(default=None, sa_column=Column(SQLString(100)))
    cnpj: str = Field(sa_column=Column(SQLString(18), unique=True, nullable=False))
    inscricao_estadual: Optional[str] = Field(
        default=None, sa_column=Column(SQLString(20))
    )
    telefone: Optional[str] = Field(default=None, sa_column=Column(SQLString(20)))
    email: Optional[str] = Field(
        default=None, sa_column=Column(SQLString(100))
    )  # Email de contato da empresa
    site: Optional[str] = Field(default=None, sa_column=Column(SQLString(100)))
    segmento: Optional[str] = Field(default=None, sa_column=Column(SQLString(50)))
    # hashed_password foi removido desta entidade
    observacoes: Optional[str] = Field(default=None, sa_column=Column(SQLText))

    data_criacao: Optional[datetime] = Field(
        default=None,  # SQLModel lida com default_factory para Pydantic, SQLAlchemy usa server_default
        sa_column=Column(
            SQLDateTime(timezone=True), server_default=func.now(), nullable=False
        ),
    )
    data_atualizacao: Optional[datetime] = Field(
        default=None,  # SQLModel lida com default_factory para Pydantic, SQLAlchemy usa onupdate
        sa_column=Column(
            SQLDateTime(timezone=True),
            onupdate=func.now(),
            server_default=func.now(),
            nullable=False,
        ),  # Adicionado server_default para garantir valor na criação
    )
