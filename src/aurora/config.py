# src/aurora/config.py
import os
from dynaconf import Dynaconf

# Define o diretório base do projeto para que o Dynaconf encontre os arquivos.
# __file__ -> /app/src/aurora/config.py
# os.path.dirname(__file__) -> /app/src/aurora
# os.path.dirname(...) -> /app/src
# os.path.dirname(...) -> /app
# Isso garante que ele funcione tanto localmente quanto no Docker.
ROOT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

settings = Dynaconf(
    envvar_prefix="AURORA",
    root_path=ROOT_PATH,
    settings_files=['settings.toml', '.secrets.toml'], # Arquivos de configuração padrão
    environments=True, # Habilita o suporte a ambientes [development], [production]
    load_dotenv=True, # Carrega variáveis de arquivos .env
    env_switcher="AURORA_ENV", # Variável de ambiente para mudar de [development] para [production]
)

# `envvar_prefix` faz com que `AURORA_DATABASE__URL` sobrescreva `database.url` no TOML.
# `load_dotenv` carrega o .env para o ambiente.