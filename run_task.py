# run_task.py
import sys
import argparse
from pathlib import Path

# --- CORREÇÃO DE PATH DEFINITIVA ---
FILE = Path(__file__).resolve()
ROOT = FILE.parent
SRC_ROOT = ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
# --- FIM DA CORREÇÃO ---

from aurora.core.context_engine import ContextEngine

def main():
    parser = argparse.ArgumentParser(description="Orquestrador da Sinapse Aurora")
    parser.add_argument("task_description", type=str, help="Descrição da tarefa")
    args = parser.parse_args()

    engine = ContextEngine()
    context = engine.get_context_for_task(args.task_description)

    prompt = f"{context}\n{args.task_description}"

    print("\n" + "="*50)
    print("CONTEXTO GERADO PARA O AGENTE:")
    print("="*50)
    print(prompt)
    print("="*50 + "\n")

    engine.log_event({
        "event_type": "task_prompt_generated",
        "task_id": "USER_TASK",
        "status": "completed",
        "summary": f"Prompt gerado para: {args.task_description[:100]}...",
        "agent": "Aurora"
    })
    print("✅ Prompt gerado e evento registrado no ESKB com sucesso!")

if __name__ == "__main__":
    main()