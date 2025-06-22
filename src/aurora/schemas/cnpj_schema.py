from pydantic import BaseModel

class EnderecoCNPJ(BaseModel):
    logradouro: str = ""
    numero: str = ""
    complemento: str = ""
    cep: str = ""
    municipio: str = ""
    uf: str = ""

class CNPJResponse(BaseModel):
    cnpj: str
    razao_social: str = ""
    nome_fantasia: str = ""
    atividade_principal: str = ""
    situacao_cadastral: str = ""
    endereco: EnderecoCNPJ = EnderecoCNPJ()
    
    class Config:
        # Permite carregar objetos com campos extras
        extra = "ignore" 