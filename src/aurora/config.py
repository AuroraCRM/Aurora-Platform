# src/aurora/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """
    Gerencia as configurações da aplicação. Agora com suporte para
    múltiplas chaves de API e URLs para a lógica de fallback.
    """
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra='ignore')

    # Variáveis do Banco de Dados
    DATABASE_URL: str
    TEST_DATABASE_URL: Optional[str] = None

    # Configurações para a lógica de fallback do CNPJ
    CNPJA_PAID_URL: str = "https://api.cnpja.com/office"
    CNPJA_FREE_URL: str = "https://publica.cnpj.ws/cnpj"
    
    # Chaves de API lidas do .env (são opcionais na definição)
    CNPJA_PRIMARY_KEY: Optional[str] = None
    CNPJA_SECONDARY_KEY: Optional[str] = None
    CNPJA_AUTH_TYPE: str = "Bearer"

    # Variável do Redis
    REDIS_URL: str

    # Variáveis de Autenticação (JWT)
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Variáveis do Azure Key Vault
    AZURE_KEY_VAULT_URI: Optional[str] = None

# Cria uma instância única das configurações
settings = Settings()
