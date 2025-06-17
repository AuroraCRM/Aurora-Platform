import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Obtém a URL do banco de dados da variável de ambiente
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("A variável de ambiente DATABASE_URL não está definida no arquivo .env")

# Cria o engine do SQLAlchemy
engine = create_engine(DATABASE_URL)

# Cria uma classe de sessão local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Cria a classe Base da qual todos os modelos irão herdar
Base = declarative_base()

# Função para obter uma sessão do banco de dados
>>>>>>> e07c843 (Configuração inicial do repositório CRM-Q)
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()