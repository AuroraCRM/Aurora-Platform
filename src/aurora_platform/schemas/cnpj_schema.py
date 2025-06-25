from pydantic import BaseModel, Field
from typing import Optional

class CNPJResponseSchema(BaseModel):
    cnpj: str = Field(..., description="CNPJ da empresa")
    razao_social: Optional[str] = Field(None, description="Razão social da empresa")
    nome_fantasia: Optional[str] = Field(None, description="Nome fantasia da empresa")
    situacao_cadastral: Optional[str] = Field(None, description="Situação cadastral da empresa")
    natureza_juridica: Optional[str] = Field(None, description="Natureza jurídica")
    data_abertura: Optional[str] = Field(None, description="Data de abertura")
    capital_social: Optional[float] = Field(None, description="Capital social")
    porte: Optional[str] = Field(None, description="Porte da empresa")
    atividade_principal: Optional[str] = Field(None, description="Atividade principal")
    logradouro: Optional[str] = Field(None, description="Endereço - logradouro")
    numero: Optional[str] = Field(None, description="Endereço - número")
    complemento: Optional[str] = Field(None, description="Endereço - complemento")
    bairro: Optional[str] = Field(None, description="Endereço - bairro")
    municipio: Optional[str] = Field(None, description="Endereço - município")
    uf: Optional[str] = Field(None, description="Endereço - UF")
    cep: Optional[str] = Field(None, description="Endereço - CEP")

    class Config:
        orm_mode = True
