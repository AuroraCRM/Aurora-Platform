from typing import Optional
from sqlmodel import Session, select, SQLModel, Field  # Adicionado Field
from fastapi import (
    HTTPException,
)  # Para consistência com ClienteRepository, embora não usado ainda

from aurora_platform.models.usuario_model import Usuario


# Schema interno para criação de usuário no repositório
class UsuarioCreateRepo(SQLModel):
    email: str = Field(
        unique=True, index=True, nullable=False
    )  # Adicionado para espelhar modelo
    hashed_password: str
    nome: Optional[str] = None
    cliente_id: Optional[int] = None
    is_active: bool = True
    # Adicionar outros campos que vêm do processo de criação de usuário


class UsuarioRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, usuario_id: int) -> Optional[Usuario]:
        """Busca um usuário pelo ID."""
        return self.db.get(Usuario, usuario_id)

    def get_by_email(self, email: str) -> Optional[Usuario]:
        """Busca um usuário pelo email."""
        if not email:
            return None
        statement = select(Usuario).where(Usuario.email == email)
        return self.db.exec(statement).first()

    def create(self, usuario_data: UsuarioCreateRepo) -> Usuario:
        """Cria um novo usuário no banco de dados."""
        # Aqui, assumimos que usuario_data já contém a senha hasheada
        # e todos os campos necessários conforme definido em UsuarioCreateRepo
        # e compatíveis com o modelo Usuario.

        # Validação para email único pode ser feita aqui antes de tentar inserir,
        # ou tratar a IntegrityError do banco.
        existing_user = self.get_by_email(usuario_data.email)
        if existing_user:
            raise HTTPException(
                status_code=409,  # Conflict
                detail=f"Usuário com email '{usuario_data.email}' já existe.",
            )

        db_usuario = Usuario.model_validate(usuario_data)
        try:
            self.db.add(db_usuario)
            self.db.commit()
            self.db.refresh(db_usuario)
            return db_usuario
        except (
            Exception
        ) as e:  # Idealmente capturar IntegrityError mais especificamente
            self.db.rollback()
            # Logar o erro e talvez levantar uma exceção mais genérica ou específica
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao criar usuário: {str(e)}",
            )

    # Outros métodos como update, delete, list_all podem ser adicionados conforme necessidade.
    # def update(self, usuario_id: int, usuario_data: UsuarioUpdateRepo) -> Optional[Usuario]:
    #     ...
    # def delete(self, usuario_id: int) -> bool:
    #     ...
