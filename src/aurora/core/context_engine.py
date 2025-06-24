# src/aurora/core/context_engine.py

import yaml

class ContextEngine:
    """
    Motor responsável por carregar e fornecer o contexto relevante 
    para a execução de tarefas de IA.
    """
    def __init__(self, knowledge_file='knowledge.yaml'):
        self.knowledge_file = knowledge_file
        self.knowledge_base = self._load_knowledge()

    def _load_knowledge(self):
        """Carrega a base de conhecimento de um arquivo YAML."""
        try:
            with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"AVISO: Arquivo de conhecimento '{self.knowledge_file}' não encontrado.")
            return {}
        except Exception as e:
            print(f"ERRO: Falha ao carregar a base de conhecimento: {e}")
            return {}

    def __call__(self, task_description: str) -> dict:
        """
        Torna a instância da classe 'callable'. Este método substitui 
        o 'get_context_for_task' e é a forma idiomática de executar
        a ação principal do objeto.
        
        Args:
            task_description: A descrição da tarefa fornecida.

        Returns:
            Um dicionário contendo o contexto para a tarefa.
        """
        # Lógica para determinar o contexto com base na descrição da tarefa.
        # Por enquanto, retorna um contexto genérico.
        # No futuro, pode analisar a task_description para buscar no self.knowledge_base.
        
        context = {
            "task": task_description,
            "system_prompt": "Você é um assistente de IA prestativo.",
            "knowledge_context": self.knowledge_base.get("general_info", "Nenhum contexto adicional disponível.")
        }
        return context