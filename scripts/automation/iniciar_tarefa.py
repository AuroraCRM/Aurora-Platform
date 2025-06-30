import sys
import datetime
import os

def iniciar_tarefa(nome_da_tarefa):
    # Define o caminho absoluto para a raiz do projeto
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    # Define os caminhos para os novos arquivos de log da ESKB
    eskb_dir = os.path.join(project_root, '.aurora_eskb')
    log_paths = [
        os.path.join(eskb_dir, 'features_log.md'),
        os.path.join(eskb_dir, 'error_resolution_log.md')
    ]

    # Garante que o diretório ESKB exista, conforme a diretriz operacional
    os.makedirs(eskb_dir, exist_ok=True)

    # Obtém a data e hora atual
    data_hora_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Cria o cabeçalho formatado em Markdown para marcar o início da tarefa
    marcador_tarefa = f"""
---
**TAREFA INICIADA:** {nome_da_tarefa}
**TIMESTAMP:** {data_hora_atual}
---
"""

    # Anexa o marcador de início de tarefa aos logs da ESKB
    for log_file in log_paths:
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(marcador_tarefa)
            print(f"Marcador da tarefa '{nome_da_tarefa}' adicionado a {os.path.basename(log_file)}")
        except FileNotFoundError:
            # O agente principal é responsável por criar os arquivos. Este script apenas anexa.
            print(f"AVISO: O arquivo de log {os.path.basename(log_file)} não existe. O marcador não foi adicionado.")
        except IOError as e:
            print(f"ERRO: Não foi possível escrever em {log_file}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python scripts/automation/iniciar_tarefa.py \"Nome da Tarefa\"")
        sys.exit(1)
    
    # Junta todos os argumentos após o nome do script para permitir nomes de tarefa com espaços
    nome_da_tarefa = " ".join(sys.argv[1:])
    iniciar_tarefa(nome_da_tarefa)
