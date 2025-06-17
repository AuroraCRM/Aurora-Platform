# src/aurora/models/lead_models.py

from sqlalchemy import Column, Integer, String, DateTime, Text, Enum
from sqlalchemy.sql import func
import enum
from aurora.database_config import Base

class StatusLead(str, enum.Enum):
    NOVO = "novo"
    CONTATADO = "contatado"
    QUALIFICADO = "qualificado"
    PROPOSTA = "proposta"
    GANHO = "ganho"
    PERDIDO = "perdido"

class LeadDB(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    telefone = Column(String(20))
    empresa = Column(String(100))
    cargo = Column(String(50))
    origem = Column(String(50))
    interesse = Column(String(100))
    observacoes = Column(Text)
    status = Column(Enum(StatusLead), default=StatusLead.NOVO)
    data_criacao = Column(DateTime(timezone=True), server_default=func.now())
    data_atualizacao = Column(DateTime(timezone=True), onupdate=func.now())