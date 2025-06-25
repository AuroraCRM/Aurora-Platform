import chromadb
from chromadb.utils import embedding_functions

class KnowledgeBaseService:
    """
    Gerencia a base de conhecimento vetorial da Aurora usando o ChromaDB.
    """
    def __init__(self, path: str = "aurora_knowledge_base"):
        print(f"Inicializando a Base de Conhecimento em: {path}")
        self.client = chromadb.PersistentClient(path=path)
        
        # Define a função que transforma texto em vetores (embeddings)
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        self.collection = self.client.get_or_create_collection(
            name="aurora_documents",
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"}
        )
        print("Serviço da Base de Conhecimento pronto.")

    def add_document(self, doc_text: str, doc_id: str, metadata: dict):
        """Adiciona um novo documento à base de conhecimento."""
        self.collection.add(
            documents=[doc_text],
            metadatas=[metadata],
            ids=[doc_id]
        )
        print(f"Documento '{doc_id}' adicionado/atualizado.")

    def search(self, query_text: str, n_results: int = 3) -> list:
        """Busca os documentos mais relevantes para uma consulta."""
        print(f"Buscando por: '{query_text}'...")
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results.get('documents', [])[0]