# src/aurora/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from aurora.config import settings

# A URL do banco de dados é lida a partir do nosso objeto de configuração centralizado (Dynaconf)
DATABASE_URL = settings.get("DATABASE_URL", "sqlite:///./test.db")

# Cria a engine do SQLAlchemy
# O argumento 'connect_args' é específico para o SQLite para permitir o uso em múltiplos threads.
# Remova-o se estiver usando outro banco de dados como PostgreSQL.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Cria uma classe SessionLocal, que será usada para criar sessões de banco de dados individuais
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Função de dependência do FastAPI para injetar uma sessão de banco de dados em cada request.
    Garante que a sessão seja sempre fechada após a conclusão do request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()