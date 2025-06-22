# diagnose_env.py
import sys
from pathlib import Path

print("=" * 60)
print("INÍCIO DO DIAGNÓSTICO FINAL DO AMBIENTE AURORA")
print("=" * 60)

# 1. Verificar qual Python está sendo executado
print("\n--- 1. EXECUTÁVEL PYTHON ---")
print(f"Caminho do Executável: {sys.executable}")
is_in_venv = ".venv" in sys.executable
print(f"Executando de dentro do '.venv'?: {is_in_venv}")

# 2. Verificar o Diretório de Trabalho Atual (CWD)
print("\n--- 2. DIRETÓRIO DE TRABALHO ATUAL (CWD) ---")
cwd = Path.cwd()
print(f"CWD: {cwd}")

# 3. Verificar a ESTRUTURA FÍSICA de Arquivos
print("\n--- 3. VERIFICAÇÃO DA ESTRUTURA FÍSICA DE ARQUIVOS ---")
root = Path(__file__).resolve().parent
src_path = root / "src"
aurora_path = src_path / "aurora"
core_path = aurora_path / "core"
engine_path = core_path / "context_engine.py"

print(f"Raiz do projeto detectada: {root}")
print(f"Verificando se 'src' existe em '{src_path}': {'SIM' if src_path.exists() else 'NÃO'}")
print(f"Verificando se 'src/aurora' existe em '{aurora_path}': {'SIM' if aurora_path.exists() else 'NÃO'}")
print(f"Verificando se 'src/aurora/core' existe em '{core_path}': {'SIM' if core_path.exists() else 'NÃO'}")
print(f"Verificando se 'context_engine.py' existe em '{engine_path}': {'SIM' if engine_path.exists() else 'NÃO'}")

# 4. Imprimir todos os caminhos de busca do Python (sys.path)
print("\n--- 4. CAMINHOS DE BUSCA DO PYTHON (sys.path) ---")
for i, path in enumerate(sys.path):
    print(f"  {i}: {path}")

print("\n" + "=" * 60)
print("FIM DO DIAGNÓSTICO")
print("=" * 60)