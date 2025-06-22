import typer
import yaml
from pathlib import Path
import sys

print("✅ [CLI] Iniciando src/aurora/cli.py")
print(f"📂 sys.path: {sys.path}")
print(f"📁 Executando a partir de: {__file__}")

app = typer.Typer(help="CLI do Projeto Aurora")
gem_app = typer.Typer(help="Comandos relacionados à IA GEM (DeepSeek)")

@gem_app.command("run")
def run_task(task_id: str = typer.Option(..., "--task-id", "-t", help="ID da tarefa no YAML")):
    """
    Executa uma tarefa da IA DeepSeek definida no aurora-deepseek-config.yaml
    """
    print(f"🚀 Executando tarefa: {task_id}")

    config_path = Path("aurora-deepseek-config.yaml")
    if not config_path.exists():
        typer.echo("❌ Arquivo de configuração não encontrado.")
        raise typer.Exit(code=1)

    with config_path.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    task = next((t for t in config.get("deepseek_tasks", []) if t.get("id") == task_id), None)

    if not task:
        typer.echo(f"❌ Tarefa '{task_id}' não encontrada.")
        raise typer.Exit(code=1)

    typer.echo(f"\n🎯 Tarefa: {task['name']}")
    typer.echo(f"📌 Descrição:\n{task['description']}\n")
    typer.echo("🧠 Prompt de execução:")
    print("-" * 80)
    print(task["prompt"])
    print("-" * 80)

app.add_typer(gem_app, name="gem")

if __name__ == "__main__":
    app()
