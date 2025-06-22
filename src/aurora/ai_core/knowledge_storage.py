# src/aurora/ai_core/knowledge_storage.py
import faiss
import numpy as np
from typing import List, Optional
from pydantic import BaseModel, Field

# Dimensão dos vetores de embedding (ex: para modelos da OpenAI, geralmente é 1536)
EMBEDDING_DIM = 1536

class KnowledgeEntry(BaseModel):
    """
    Representa uma entrada única na base de conhecimento vetorial.
    """
    content: str
    embedding: List[float]
    source_id: str = Field(..., description="Identificador único da fonte do conhecimento")
    metadata: Optional[dict] = None

class VectorKnowledgeBase:
    """
    Gerencia uma base de conhecimento vetorial em memória usando FAISS.
    """
    def __init__(self):
        # Inicializa um índice FAISS para busca de similaridade rápida
        self.index = faiss.IndexFlatL2(EMBEDDING_DIM)
        self.entries: List[KnowledgeEntry] = []

    def add_entry(self, entry: KnowledgeEntry):
        """
        Adiciona uma nova entrada de conhecimento à base.
        """
        if len(entry.embedding) != EMBEDDING_DIM:
            raise ValueError(f"Dimensão do embedding inválida. Esperado {EMBEDDING_DIM}, recebido {len(entry.embedding)}")

        # Adiciona o embedding ao índice FAISS
        embedding_np = np.array([entry.embedding]).astype('float32')
        self.index.add(embedding_np)
        
        # Armazena a entrada completa para recuperação de metadados
        self.entries.append(entry)

    def search(self, query_embedding: List[float], k: int = 5) -> List[KnowledgeEntry]:
        """
        Busca as 'k' entradas mais similares a um embedding de consulta.
        """
        if not self.entries:
            return []

        query_np = np.array([query_embedding]).astype('float32')
        distances, indices = self.index.search(query_np, k)

        # Retorna as entradas completas correspondentes aos índices encontrados
        results = [self.entries[i] for i in indices[0] if i < len(self.entries)]
        return results

    def _create_mock_entry(self) -> KnowledgeEntry:
        """
        Função auxiliar para criar uma entrada de teste.
        """
        content = "Este é um documento de teste sobre a Aurora."
        embedding = list(np.random.rand(EMBEDDING_DIM))
        
        # CORREÇÃO: O argumento 'source_id' estava faltando na criação do objeto.
        return KnowledgeEntry(
            content=content,
            embedding=embedding,
            source_id="mock_doc_001" 
        )

# Exemplo de uso (pode ser movido para testes)
if __name__ == "__main__":
    kb = VectorKnowledgeBase()
    mock_entry = kb._create_mock_entry()
    kb.add_entry(mock_entry)
    
    # Simula uma busca
    search_result = kb.search(mock_entry.embedding, k=1)
    print("Busca retornou:", search_result[0].content)