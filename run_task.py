# run_task.py

import argparse

# A importação agora busca o ContextEngine de sua nova localização estruturada
from aurora_platform.core.context_engine import ContextEngine

# Supondo que o agente de IA também terá sua classe em um local apropriado
# from aurora_platform.agents.base_agent import BaseAIAgent


def main():
    """Função principal para executar o orquestrador de tarefas."""
    parser = argparse.ArgumentParser(description="Orquestrador da Sinapse Aurora")
    parser.add_argument(
        "task_description",
        type=str,
        help="Descrição da tarefa a ser executada pela IA.",
    )
    args = parser.parse_args()

    print(f"Ordem de Serviço Recebida: '{args.task_description}'")

    # 1. Obter Contexto
    # A instância do ContextEngine é criada.
    engine = ContextEngine(knowledge_file="knowledge.yaml")

    # A chamada ao método foi simplificada para invocar o objeto diretamente.
    # CORREÇÃO: de 'engine.get_context_for_task(...)' para 'engine(...)'
    context = engine(args.task_description)

    print("Contexto Gerado:", context)

    # 2. Selecionar e Executar o Agente de IA (lógica futura)
    # agent = select_agent_for_task(context['task'])
    # result = agent.run(context)
    # print("Resultado da Tarefa:", result)

    # 3. Registrar o resultado (lógica futura)
    # log_event(task_description, context, result)

    print("\nAVISO: Execução do agente e logging ainda não implementados.")


if __name__ == "__main__":
    main()
