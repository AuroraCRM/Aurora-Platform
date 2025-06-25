from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Schema para os dados contidos dentro de um token JWT,
    tipicamente o 'sub' (subject/username) e outros campos.
    """

    sub: Optional[str] = None  # 'sub' é o campo padrão para o identificador do usuário
    # Adicionar outros campos que você coloca no payload do token, se houver.
    # Ex: type: Optional[str] = None (se você usar 'type' no payload como "access" ou "refresh")
