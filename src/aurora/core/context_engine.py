# src/aurora/core/context_engine.py
from typing import Dict, Any, Optional # CORREÇÃO CRÍTICA A SER APLICADA
import yaml
from aurora.config import settings

class ContextEngine:
    """
    Motor de contexto responsável por carregar e fornecer conhecimento
    de domínio para outros módulos da aplicação.
    """
    def __init__(self):
        self.knowledge_file = settings.get("KNOWLEDGE_FILE_PATH", "knowledge.yaml")
        self.knowledge: Dict[str, Any] = self._load_knowledge()

    def _load_knowledge(self) -> Dict[str, Any]:
        """
        Carrega o arquivo de conhecimento (YAML) do disco.
        Retorna um dicionário vazio se o arquivo não for encontrado ou ocorrer um erro.
        """
        try:
            with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data if isinstance(data, dict) else {}
        except FileNotFoundError:
            print(f"AVISO: Arquivo de conhecimento '{self.knowledge_file}' não encontrado.")
            return {}
        except yaml.YAMLError as e:
            print(f"ERRO: Falha ao parsear o arquivo de conhecimento YAML: {e}")
            return {}

    def get_context(self, domain: str, key: str) -> Optional[Any]:
        """
        Obtém uma informação de contexto específica de um domínio.

        Args:
            domain (str): O domínio do conhecimento (ex: 'crm', 'pln').
            key (str): A chave da informação desejada.

        Returns:
            Optional[Any]: O valor da informação ou None se não for encontrado.
        """
        return self.knowledge.get(domain, {}).get(key)