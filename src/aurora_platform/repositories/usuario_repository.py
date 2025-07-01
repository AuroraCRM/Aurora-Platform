import logging
from typing import Optional, Sequence
from sqlmodel import Session, select, SQLModel, Field
from fastapi import HTTPException

from aurora_platform.models.usuario_model import Usuario

logger = logging.getLogger(__name__)

# Schema interno para criação de usuário no repositório
class UsuarioCreateRepo(SQLModel):
    email: str = Field(
        unique=True, index=True, nullable=False
    )
    hashed_password: str
    nome: Optional[str] = None
    cliente_id: Optional[int] = None
    is_active: bool = True


class UsuarioRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, usuario_id: int) -> Optional[Usuario]:
        """Busca um usuário pelo ID."""
        logger.info(f"Attempting to retrieve user with ID: {usuario_id}")
        user = self.db.get(Usuario, usuario_id)
        if user:
            logger.info(f"User with ID: {usuario_id} found.")
        else:
            logger.info(f"User with ID: {usuario_id} not found.")
        return user

    def get_by_email(self, email: str) -> Optional[Usuario]:
        """Busca um usuário pelo email."""
        logger.info(f"Attempting to retrieve user with email: {email}")
        if not email:
            logger.warning("Attempted to retrieve user with empty email.")
            return None
        statement = select(Usuario).where(Usuario.email == email)
        user = self.db.exec(statement).first()
        if user:
            logger.info(f"User with email: {email} found.")
        else:
            logger.info(f"User with email: {email} not found.")
        return user

    def create(self, usuario_data: UsuarioCreateRepo) -> Usuario:
        """Cria um novo usuário no banco de dados."""
        logger.info(f"Attempting to create new user with email: {usuario_data.email}")
        existing_user = self.get_by_email(usuario_data.email)
        if existing_user:
            logger.warning(f"User creation failed: User with email '{usuario_data.email}' already exists.")
            raise HTTPException(
                status_code=409,
                detail=f"Usuário com email '{usuario_data.email}' já existe.",
            )

        db_usuario = Usuario.model_validate(usuario_data)
        try:
            self.db.add(db_usuario)
            self.db.commit()
            self.db.refresh(db_usuario)
            logger.info(f"User created successfully: {db_usuario.email} (ID: {db_usuario.id})")
            return db_usuario
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating user {usuario_data.email}: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao criar usuário: {str(e)}",
            )
