from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from aurora.database_config import Base


class ClienteDB(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    razao_social = Column(String(100), nullable=False)
    nome_fantasia = Column(String(100))
    cnpj = Column(String(18), unique=True, nullable=False)
    inscricao_estadual = Column(String(20))
    telefone = Column(String(20))
    email = Column(String(100))
    site = Column(String(100))
    segmento = Column(String(50))
    observacoes = Column(Text)
    data_criacao = Column(DateTime(timezone=True), server_default=func.now())
    data_atualizacao = Column(DateTime(timezone=True), onupdate=func.now())
