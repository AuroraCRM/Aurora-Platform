# src/aurora/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Configura a classe para ler as variáveis de um arquivo .env
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra='ignore'
    )

    # Banco de Dados
    DATABASE_URL: str
    TEST_DATABASE_URL: str

    # Segurança JWT
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # APIs Externas
    CNPJA_API_URL: str
    CNPJA_AUTH_TYPE: str = "Bearer"

    # --- CORREÇÃO APLICADA AQUI ---
    CNPJA_API_KEY: str # Declarando o campo que faltava
    # ---------------------------------

    GEMINI_API_KEY: Optional[str] = None

# Cria uma instância única das configurações que será usada em todo o projeto
settings = Settings()