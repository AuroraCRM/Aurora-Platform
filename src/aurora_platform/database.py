# src/aurora_platform/database.py - Versão Final Corrigida

from typing import Generator, Any
from sqlmodel import create_engine, Session, SQLModel

# Vamos usar uma configuração de banco de dados placeholder por enquanto.
# Isso será lido do arquivo .env quando integrarmos as configurações.
DATABASE_URL = "sqlite:///./aurora_platform.db"
engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False})

def create_db_and_tables():
    """
    Cria todas as tabelas registradas no metadata do SQLModel.
    """
    SQLModel.metadata.create_all(engine)

# --- INÍCIO DA CORREÇÃO ---
# A anotação de tipo correta para uma função geradora que produz uma Sessão do BD
def get_session() -> Generator[Session, Any, None]:
# --- FIM DA CORREÇÃO ---
    """
    Fornece uma sessão do banco de dados como uma dependência do FastAPI.
    """
    with Session(engine) as session:
        yield session