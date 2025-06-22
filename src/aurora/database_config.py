# src/aurora/database_config.py

from sqlalchemy.orm import DeclarativeBase

# CORREÇÃO: No SQLAlchemy 2.0, a 'Base' declarativa é uma classe da qual os modelos herdam.
# Isso substitui o antigo 'declarative_base()'. Todos os nossos modelos de ORM
# (como Cliente, Lead, etc.) devem herdar desta classe 'Base'.
class Base(DeclarativeBase):
    """
    Classe base para todos os modelos ORM do projeto Aurora.
    Ela serve como um registro central para os metadados do SQLAlchemy.
    """
    pass