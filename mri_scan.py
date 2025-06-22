import subprocess
import sys
import os

# --- Configuração ---
TARGET_DIRECTORY = "src"
REPORT_FILE = "mri_report.md"

# --- Ferramentas e Comandos ---
# Certifique-se de que estas ferramentas estão instaladas:
# pip install flake8 bandit mypy
TOOLS = {
    "quality": {
        "name": "Flake8 (Qualidade e Estilo)",
        "command": [
            sys.executable, "-m", "flake8", TARGET_DIRECTORY,
            "--count", "--select=E9,F63,F7,F82", "--show-source", "--statistics"
        ],
        "icon": "🩺"
    },
    "security": {
        "name": "Bandit (Segurança)",
        "command": [
            sys.executable, "-m", "bandit", "-r", TARGET_DIRECTORY, "-f", "txt"
        ],
        "icon": "🛡️"
    },
    "typing": {
        "name": "MyPy (Consistência de Tipos)",
        "command": [
            sys.executable, "-m", "mypy", TARGET_DIRECTORY, "--ignore-missing-imports"
        ],
        "icon": "🧬"
    }
}

def run_tool(tool_name, config):
    """Executa uma ferramenta de análise e captura o resultado."""
    print(f"\n{config['icon']} Executando {config['name']}...")
    try:
        process = subprocess.run(
            config["command"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=False  # Não levanta exceção se o comando falhar
        )
        print(f"-> Análise de {tool_name} concluída.")
        return process.stdout, process.stderr, process.returncode
    except FileNotFoundError:
        print(f"ERRO: Comando '{config['command'][0]}' não encontrado.")
        print("Por favor, instale as ferramentas com: pip install flake8 bandit mypy")
        return None, None, -1
    except Exception as e:
        print(f"Ocorreu um erro inesperado ao executar {tool_name}: {e}")
        return None, None, -1


def generate_report():
    """Orquestra a execução das ferramentas e gera um relatório em Markdown."""
    report_content = ["# 🤖 Relatório de Ressonância Magnética (MRI) do Projeto Aurora\n\n"]
    report_content.append(f"Análise profunda do diretório: `{os.path.abspath(TARGET_DIRECTORY)}`\n\n---")

    for key, tool_config in TOOLS.items():
        stdout, stderr, returncode = run_tool(key, tool_config)
        
        report_content.append(f"\n\n## {tool_config['icon']} {tool_config['name']}\n")
        
        if returncode == -1:
             report_content.append("Falha ao executar a ferramenta. Verifique se ela está instalada.\n")
             continue

        if stdout or stderr:
            report_content.append(f"**Resultado (Código de Saída: {returncode})**:\n")
            report_content.append("```text\n")
            if stdout:
                report_content.append(stdout)
            if stderr:
                report_content.append("\n--- ERROS ---\n")
                report_content.append(stderr)
            report_content.append("```\n")
        else:
            report_content.append("✅ Nenhuma questão encontrada por esta ferramenta.\n")

    try:
        with open(REPORT_FILE, "w", encoding='utf-8') as f:
            f.write("".join(report_content))
        print(f"\n\n✅ Relatório de Ressonância Magnética salvo em: {REPORT_FILE}")
    except IOError as e:
        print(f"\nERRO: Não foi possível escrever o arquivo de relatório: {e}")


if __name__ == "__main__":
    print("Iniciando a Ressonância Magnética do Código...")
    print("Ferramentas necessárias: flake8, bandit, mypy")
    generate_report()