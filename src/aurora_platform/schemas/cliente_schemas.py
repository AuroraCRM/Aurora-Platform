# Caminho: C:\Users\winha\Aurora\Aurora-Platform\src\aurora_platform\schemas\cliente_schemas.py

from pydantic import BaseModel, EmailStr, validator, constr
from typing import Optional
import re


class ClienteCreate(BaseModel):
    nome: constr(min_length=3, max_length=100)
    email: EmailStr
    telefone: Optional[constr(min_length=8, max_length=20)] = None
    cnpj: Optional[constr(min_length=14, max_length=18)] = None

    @validator('cnpj')
    def validate_cnpj(cls, value):
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
    telefone: Optional[str] = None
    cnpj: Optional[str] = None

    class Config:
        from_attributes = True
