# src/aurora/config.py

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Classe central para gerenciamento de configurações da aplicação.
    Carrega variáveis a partir de um arquivo .env, valida seus tipos
    e aplica correções para garantir a robustez na leitura.
    """

    # --- Seção de Banco de Dados ---
    DATABASE_URL: str
    TEST_DATABASE_URL: str

    # --- Seção de Segurança / JWT ---
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # --- Seção de Serviços Externos ---
    # Variável padronizada para a única API funcional (cnpj.ws)
    CNPJWS_PUBLIC_URL: str
    
    # --- Seção de Cache ---
    REDIS_URL: str

    @field_validator("*", mode="before")
    @classmethod
    def _strip_inline_comment(cls, v):
        """
        Validador que roda antes da validação de tipo para limpar
        comentários inline (ex: '30 # comentario') de qualquer variável.
        """
        if isinstance(v, str):
            return v.split("#", 1)[0].strip()
        return v

    # Configuração do Pydantic para carregar do arquivo .env
    model_config = SettingsConfigDict(
        env_file=".env",                # Aponta para o arquivo .env na raiz do projeto
        env_file_encoding="utf-8",      # Força a leitura como UTF-8, corrigindo erros de unicode
        extra="ignore"                  # Ignora variáveis extras no .env que não estão definidas aqui
    )

# Cria uma instância única da classe Settings que será importada em toda a aplicação.
settings = Settings()
