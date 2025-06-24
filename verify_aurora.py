# verify_aurora.py
import sys
import os
from importlib.metadata import version, PackageNotFoundError

# --- Configuração ---
LIBRARIES_TO_CHECK = [
    "fastapi",
    "sqlalchemy",
    "pydantic",
    "dynaconf",
    "flake8",
    "bandit",
    "mypy",
]

FILES_TO_VERIFY = {
    "src/aurora/database_config.py": "class Base(DeclarativeBase):",
    "src/integrations/cnpj_adapter.py": "return data if isinstance(data, dict) else {}",
    "src/aurora/core/context_engine.py": "from typing import Dict, Any, Optional",
}

# --- Funções de Verificação ---


def print_header(title):
    print("\n" + "=" * 60)
    print(f"🔬 {title}")
    print("=" * 60)


def verify_python_version():
    print_header("Verificação da Versão do Python")
    version_info = sys.version_info
    print(
        f"Versão detectada: {version_info.major}.{version_info.minor}.{version_info.micro}"
    )
    if version_info.major < 3 or version_info.minor < 10:
        print(
            "❌ ALERTA: Versão do Python é mais antiga que a 3.10. Recomenda-se Python 3.10+."
        )
    else:
        print("✅ Versão do Python compatível.")


def verify_library_versions():
    print_header("Verificação das Versões das Bibliotecas")
    for lib in LIBRARIES_TO_CHECK:
        try:
            lib_version = version(lib)
            print(f"- {lib:<15}: {lib_version}", end="")
            if lib == "sqlalchemy" and not lib_version.startswith("2."):
                print("  -> ❌ ALERTA CRÍTICO: Versão do SQLAlchemy não é 2.x!")
            else:
                print("  -> ✅")
        except PackageNotFoundError:
            print(f"- {lib:<15}: ❌ NÃO ENCONTRADA!")


def verify_file_contents():
    print_header("Verificação do Conteúdo dos Arquivos Corrigidos")
    all_files_ok = True
    for file_path, expected_string in FILES_TO_VERIFY.items():
        print(f"- Verificando '{file_path}'...")
        if not os.path.exists(file_path):
            print(f"  ❌ ERRO: Arquivo não encontrado.")
            all_files_ok = False
            continue

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            if expected_string in content:
                print(f"  ✅ Conteúdo esperado encontrado.")
            else:
                print(f"  ❌ ALERTA: O arquivo não contém a correção esperada.")
                print(f"    (Esperava encontrar: '{expected_string}')")
                all_files_ok = False
        except Exception as e:
            print(f"  ❌ ERRO ao ler o arquivo: {e}")
            all_files_ok = False

    if all_files_ok:
        print(
            "\n✅ Todos os arquivos parecem estar com as últimas correções aplicadas."
        )
    else:
        print(
            "\n❌ ALERTA: Um ou mais arquivos não estão atualizados. As correções anteriores precisam ser reaplicadas."
        )


# --- Execução Principal ---
if __name__ == "__main__":
    print("Iniciando diagnóstico completo do ambiente e código do Projeto Aurora...")
    verify_python_version()
    verify_library_versions()
    verify_file_contents()
    print("\n" + "=" * 60)
    print("Diagnóstico concluído.")
    print("=" * 60)
