# src/aurora/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Classe central para gerenciamento de configurações da aplicação.
    Carrega variáveis a partir de um arquivo .env e valida seus tipos.
    """

    # Configurações do Banco de Dados
    DATABASE_URL: str
    TEST_DATABASE_URL: str

    # Configurações de Segurança e JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Configurações de Serviços Externos
    # Usando o provedor cnpj.ws que validamos
    CNPJWS_PUBLIC_URL: str
    
    # Configuração do Cache (Redis)
    REDIS_URL: str

    # Configuração do Pydantic para carregar do arquivo .env
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        extra='ignore' # Ignora variáveis extras que possam estar no .env
    )

# Cria uma instância única da classe Settings que será usada em toda a aplicação.
# Qualquer arquivo que precisar de uma configuração fará: from aurora.config import settings
settings = Settings()