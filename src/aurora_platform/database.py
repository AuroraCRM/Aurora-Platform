# src/aurora/database.py


# sqlalchemy.orm.sessionmaker não é mais necessário diretamente se usarmos sqlmodel.Session na factory
from aurora_platform.config import settings
from sqlmodel import (
    Session,
    create_engine as sqlmodel_create_engine,
)  # Importar Session e create_engine de SQLModel

# A URL do banco de dados é lida a partir do nosso objeto de configuração centralizado (Dynaconf)
DATABASE_URL = settings.get("DATABASE_URL", "sqlite:///./test.db")

# Cria a engine usando a create_engine do SQLModel (ou SQLAlchemy, mas SQLModel é preferível para consistência)
# O argumento 'connect_args' é específico para o SQLite.
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
engine = sqlmodel_create_engine(DATABASE_URL, connect_args=connect_args)

# SessionLocal agora será uma factory para sqlmodel.Session
# Não precisamos mais de sessionmaker diretamente se get_db lida com a criação da sessão.


def get_db() -> Session:  # Anotação de tipo para clareza
    """
    Função de dependência do FastAPI para injetar uma sessão de banco de dados em cada request.
    Garante que a sessão seja sempre fechada após a conclusão do request.
    """
    # Usar sqlmodel.Session diretamente com a engine
    with Session(engine) as session:
        yield session
    # A sessão é fechada automaticamente pelo context manager 'with'
