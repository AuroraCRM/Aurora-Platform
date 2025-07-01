# src/aurora_platform/models/lead_models.py
from typing import Optional
from datetime import datetime
import enum
from pydantic import EmailStr # Movido para o topo

from sqlmodel import (
    Field,
    SQLModel,
    Column,
    Enum as SQLEnum,
    String as SQLString,
    Text as SQLText,
    DateTime as SQLDateTime,
)
from sqlalchemy.sql import func


class StatusLead(str, enum.Enum):
    NOVO = "novo"
    CONTATADO = "contatado"
    QUALIFICADO = "qualificado"
    PROPOSTA = "proposta"
    GANHO = "ganho"
    PERDIDO = "perdido"


from sqlalchemy.ext.declarative import declared_attr

class LeadDB(SQLModel, table=True):
    __tablename__: str = "leads" # type: ignore

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    nome: str = Field(sa_column=Column(SQLString(100), nullable=False))
    email: str = Field(
        sa_column=Column(SQLString(100), nullable=False)
    )  # Idealmente com unique=True e index=True dependendo da lógica de negócios
    telefone: Optional[str] = Field(default=None, sa_column=Column(SQLString(20)))
    empresa: Optional[str] = Field(default=None, sa_column=Column(SQLString(100)))
    cargo: Optional[str] = Field(default=None, sa_column=Column(SQLString(50)))
    origem: Optional[str] = Field(default=None, sa_column=Column(SQLString(50)))
    interesse: Optional[str] = Field(default=None, sa_column=Column(SQLString(100)))
    observacoes: Optional[str] = Field(default=None, sa_column=Column(SQLText))
    status: StatusLead = Field(
        default=StatusLead.NOVO, sa_column=Column(SQLEnum(StatusLead), nullable=False)
    )

    data_criacao: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            SQLDateTime(timezone=True), server_default=func.now(), nullable=False
        ),
    )
    data_atualizacao: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            SQLDateTime(timezone=True),
            onupdate=func.now(),
            server_default=func.now(),
            nullable=False,
        ),
    )


# Para compatibilidade ou uso em Pydantic, podemos definir um modelo Lead sem o 'DB'
class Lead(SQLModel):
    nome: str
    email: EmailStr  # Alterado para EmailStr para validação automática
    telefone: Optional[str] = None
    empresa: Optional[str] = None
    cargo: Optional[str] = None
    origem: Optional[str] = None
    interesse: Optional[str] = None
    observacoes: Optional[str] = None
    status: StatusLead = StatusLead.NOVO


class LeadCreate(Lead):
    pass


class LeadRead(Lead):
    id: int
    data_criacao: datetime
    data_atualizacao: datetime


class LeadUpdate(SQLModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    empresa: Optional[str] = None
    cargo: Optional[str] = None
    origem: Optional[str] = None
    interesse: Optional[str] = None
    observacoes: Optional[str] = None
    status: Optional[StatusLead] = None
