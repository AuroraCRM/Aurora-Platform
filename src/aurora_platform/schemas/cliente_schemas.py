# Caminho: C:\Users\winha\Aurora\Aurora-Platform\src\aurora_platform\schemas\cliente_schemas.py

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from pydantic.functional_validators import field_validator
from typing import Union
import re


class ClienteCreate(BaseModel):
    razao_social: str = Field(min_length=3, max_length=100)
    nome_fantasia: Union[str, None] = Field(default=None, max_length=100)
    cnpj: str = Field(min_length=14, max_length=18)
    inscricao_estadual: Union[str, None] = Field(default=None, max_length=20)
    telefone: Union[str, None] = Field(default=None, max_length=20)
    email: Union[EmailStr, None] = Field(default=None)
    site: Union[str, None] = Field(default=None, max_length=100)
    segmento: Union[str, None] = Field(default=None, max_length=50)
    observacoes: Union[str, None] = Field(default=None)

    @field_validator('cnpj')
    @classmethod
    def validate_cnpj(cls, value: str) -> str:
        if value:
            # Remove non-numeric characters
            cnpj_digits = re.sub(r'[^0-9]', '', value)
            if len(cnpj_digits) not in [14, 18]: # 14 for CNPJ, 18 for CNPJ with branch
                raise ValueError('CNPJ must have 14 or 18 digits (after removing non-numeric characters)')
            # Basic check for all same digits (e.g., "00.000.000/0000-00")
            if cnpj_digits == cnpj_digits[0] * len(cnpj_digits):
                raise ValueError('Invalid CNPJ format')
            # Add more robust CNPJ validation logic here if needed
        return value


class ClienteUpdate(BaseModel):
    razao_social: Union[str, None] = Field(default=None, min_length=3, max_length=100)
    nome_fantasia: Union[str, None] = Field(default=None, max_length=100)
    cnpj: Union[str, None] = Field(default=None, min_length=14, max_length=18)
    inscricao_estadual: Union[str, None] = Field(default=None, max_length=20)
    telefone: Union[str, None] = Field(default=None, max_length=20)
    email: Union[EmailStr, None] = Field(default=None)
    site: Union[str, None] = Field(default=None, max_length=100)
    segmento: Union[str, None] = Field(default=None, max_length=50)
    observacoes: Union[str, None] = Field(default=None)

    @field_validator('cnpj')
    @classmethod
    def validate_cnpj(cls, value: str) -> str:
        if value:
            # Remove non-numeric characters
            cnpj_digits = re.sub(r'[^0-9]', '', value)
            if len(cnpj_digits) not in [14, 18]: # 14 for CNPJ, 18 for CNPJ with branch
                raise ValueError('CNPJ must have 14 or 18 digits (after removing non-numeric characters)')
            # Basic check for all same digits (e.g., "00.000.000/0000-00")
            if cnpj_digits == cnpj_digits[0] * len(cnpj_digits):
                raise ValueError('Invalid CNPJ format')
            # Add more robust CNPJ validation logic here if needed
        return value


class ClienteResponse(BaseModel):
    id: int
    nome: str
    email: EmailStr
    telefone: Union[str, None] = Field(default=None)
    cnpj: Union[str, None] = Field(default=None)

    model_config = ConfigDict(from_attributes=True)