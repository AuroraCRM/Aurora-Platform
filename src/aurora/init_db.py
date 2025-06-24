# src/aurora/init_db.py

import logging
from sqlalchemy.exc import SQLAlchemyError
from aurora.database_config import engine, Base
from aurora.models.cliente_model import Cliente
from aurora.models.lead_models import LeadDB

logger = logging.getLogger(__name__)


def init_db():
    """
    Inicializa o banco de dados criando todas as tabelas definidas nos modelos.
    """
    try:
        logger.info("Criando tabelas no banco de dados...")
        Base.metadata.create_all(bind=engine)
        logger.info("Tabelas criadas com sucesso!")
    except SQLAlchemyError as e:
        logger.error(f"Erro ao criar tabelas: {str(e)}")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_db()
