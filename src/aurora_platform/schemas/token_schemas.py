from pydantic import BaseModel, Field
from typing import Union


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: Union[str, None] = Field(default=None)


class TokenData(BaseModel):
    """
    Schema para os dados contidos dentro de um token JWT,
    tipicamente o 'sub' (subject/username) e outros campos.
    """

    sub: Union[str, None] = Field(default=None)  # 'sub' é o campo padrão para o identificador do usuário
    # Adicionar outros campos que você coloca no payload do token, se houver.
    # Ex: type: Union[str, None] = Field(default=None) (se você usar 'type' no payload como "access" ou "refresh")
