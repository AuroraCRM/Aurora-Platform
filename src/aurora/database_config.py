import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração do banco de dados
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./aurora.db")

if not DATABASE_URL:
    print("Aviso: Usando banco de dados SQLite local")

# Cria o engine do SQLAlchemy
engine = create_engine(DATABASE_URL)

# Cria uma classe de sessão local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Cria a classe Base da qual todos os modelos irão herdar
Base = declarative_base()


# Função para obter uma sessão do banco de dados
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
