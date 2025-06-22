# src/aurora/schemas/cnpj_schema.py
from pydantic import BaseModel
from typing import Optional

class CNPJResponse(BaseModel):
    """Schema para resposta de dados de CNPJ."""
    cnpj: str
    razao_social: str
    nome_fantasia: Optional[str] = None
    situacao_cadastral: str
    data_abertura: str
    cnae_principal: str
    endereco: dict
    contato: dict

    # CORREÇÃO: Atualizado para json_schema_extra (Pydantic V2)
    model_config = {
        "json_schema_extra": {
            "example": {
                "cnpj": "12345678000199",
                "razao_social": "Empresa Exemplo LTDA",
                "nome_fantasia": "Exemplo Comércio",
                "situacao_cadastral": "ATIVA",
                "data_abertura": "2020-01-01",
                "cnae_principal": "6201-5/00",
                "endereco": {
                    "logradouro": "Rua Exemplo",
                    "numero": "123",
                    "complemento": "Sala 456",
                    "bairro": "Centro",
                    "municipio": "São Paulo",
                    "uf": "SP",
                    "cep": "01001000"
                },
                "contato": {
                    "telefone": "1122223333",
                    "email": "contato@exemplo.com"
                }
            }
        }
    }