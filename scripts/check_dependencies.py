# scripts/check_dependencies.py

import importlib
import sys

def main():
    """
    Verifica a presença de todas as dependências conhecidas do projeto Aurora
    e gera um comando para instalar as que estiverem faltando.
    """
    
    # Dicionário mapeando o nome de import para o nome do pacote pip
    # Isso lida com casos onde os nomes são diferentes (ex: 'dotenv' -> 'python-dotenv')
    dependencies_map = {
        # Produção
        "fastapi": "fastapi",
        "uvicorn": "uvicorn",
        "pydantic": "pydantic",
        "pydantic_settings": "pydantic-settings",
        "sqlalchemy": "SQLAlchemy",
        "psycopg2": "psycopg2-binary",
        "redis": "redis",
        "httpx": "httpx",
        "dotenv": "python-dotenv",
        "passlib": "passlib[bcrypt]",
        "jose": '"python-jose[cryptography]"',
        "email_validator": "email-validator",
        "pyotp": "pyotp",          # <-- ADICIONADO
        "qrcode": "qrcode[pil]",  # <-- ADICIONADO (com suporte a imagem)

        # Desenvolvimento e Testes
        "pytest": "pytest",
        "flake8": "flake8",
        "black": "black",
    }

    print("--- Iniciando verificação de dependências do projeto Aurora ---")
    
    missing_packages = []
    
    for import_name, package_name in dependencies_map.items():
        try:
            importlib.import_module(import_name)
            print(f"  [ ✓ ] {import_name}")
        except ImportError:
            print(f"  [ ✗ ] {import_name} (Faltando!)")
            missing_packages.append(package_name)
            
    print("\n--- Verificação Concluída ---")
    
    if not missing_packages:
        print("\n[ ✓ ] Ótima notícia! Todas as dependências necessárias estão instaladas.")
    else:
        print("\n[ ! ] As seguintes dependências estão faltando ou precisam ser instaladas:")
        for pkg in missing_packages:
            print(f"    - {pkg}")
        
        # Gera o comando de instalação
        install_command = f"pip install {' '.join(missing_packages)}"
        print("\nPara instalar todas as dependências faltantes de uma só vez, execute o comando abaixo:")
        print("-" * 70)
        print(install_command)
        print("-" * 70)

if __name__ == "__main__":
    main()
