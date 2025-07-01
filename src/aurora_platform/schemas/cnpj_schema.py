from pydantic import BaseModel, Field, ConfigDict
from typing import Union

class CNPJResponseSchema(BaseModel):
    cnpj: str = Field(..., description="CNPJ da empresa")
    razao_social: Union[str, None] = Field(default=None, description="Razão social da empresa")
    nome_fantasia: Union[str, None] = Field(default=None, description="Nome fantasia da empresa")
    situacao_cadastral: Union[str, None] = Field(default=None, description="Situação cadastral da empresa")
    natureza_juridica: Union[str, None] = Field(default=None, description="Natureza jurídica")
    data_abertura: Union[str, None] = Field(default=None, description="Data de abertura")
    capital_social: Union[float, None] = Field(default=None, description="Capital social")
    porte: Union[str, None] = Field(default=None, description="Porte da empresa")
    atividade_principal: Union[str, None] = Field(default=None, description="Atividade principal")
    logradouro: Union[str, None] = Field(default=None, description="Endereço - logradouro")
    numero: Union[str, None] = Field(default=None, description="Endereço - número")
    complemento: Union[str, None] = Field(default=None, description="Endereço - complemento")
    bairro: Union[str, None] = Field(default=None, description="Endereço - bairro")
    municipio: Union[str, None] = Field(default=None, description="Endereço - município")
    uf: Union[str, None] = Field(default=None, description="Endereço - UF")
    cep: Union[str, None] = Field(default=None, description="Endereço - CEP")

    model_config = ConfigDict(from_attributes=True)
