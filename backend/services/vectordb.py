import numpy as np
import os
import pickle
from sentence_transformers import SentenceTransformer
import json


class VectorDBService:
    def __init__(self, collection_name="tango_knowledge"):
        self.collection_name = collection_name
        self.data_dir = "./data/vectors"
        
        # Cria o diretório de dados se não existir
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Caminhos para os arquivos de armazenamento
        self.vectors_path = os.path.join(self.data_dir, f"{collection_name}_vectors.npy")
        self.documents_path = os.path.join(self.data_dir, f"{collection_name}_documents.pkl")
        self.metadata_path = os.path.join(self.data_dir, f"{collection_name}_metadata.json")
        
        # Inicializa o modelo de embeddings
        self.model = SentenceTransformer('intfloat/multilingual-e5-large')
        
        # Carrega ou cria a base de vetores
        if os.path.exists(self.vectors_path) and os.path.exists(self.documents_path):
            self.vectors = np.load(self.vectors_path)
            with open(self.documents_path, 'rb') as f:
                self.documents = pickle.load(f)
            
            # Carrega os metadados se existirem
            if os.path.exists(self.metadata_path):
                with open(self.metadata_path, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
            else:
                self.metadata = [None] * len(self.documents)
                
            print(f"Coleção '{collection_name}' carregada com sucesso. Documentos: {len(self.documents)}")
        else:
            # Cria nova base vazia
            self.vectors = np.array([]).reshape(0, self.model.get_sentence_embedding_dimension())
            self.documents = []
            self.metadata = []
            print(f"Coleção '{collection_name}' criada com sucesso.")
    
    def add_documents(self, texts, metadatas=None, ids=None):
        """Adiciona documentos à base de conhecimento."""
        if not texts:
            return 0
            
        # Prepara metadados
        if metadatas is None:
            metadatas = [None] * len(texts)
        
        # Gera embeddings para os textos
        embeddings = self.model.encode(texts)
        
        # Adiciona os vetores à base
        self.vectors = np.vstack([self.vectors, embeddings]) if self.vectors.size else embeddings
        
        # Armazena os documentos e metadados
        for i, (text, metadata) in enumerate(zip(texts, metadatas)):
            self.documents.append(text)
            self.metadata.append(metadata)
        
        # Salva os dados
        self._save_data()
        
        return len(texts)
    
    def query(self, query_text, n_results=3):
        """Realiza consulta de similaridade semântica."""
        if not self.documents:
            return {"documents": [], "ids": [], "metadatas": [], "distances": []}
            
        # Gera embedding para a consulta
        query_embedding = self.model.encode(query_text)
        
        # Calcula similaridade coseno
        if len(self.vectors) > 0:
            # Normaliza vetores para cálculo de similaridade coseno
            query_norm = np.linalg.norm(query_embedding)
            if query_norm > 0:
                query_embedding = query_embedding / query_norm
            
            # Normaliza vetores da base (se ainda não estiverem normalizados)
            vector_norms = np.linalg.norm(self.vectors, axis=1, keepdims=True)
            normalized_vectors = np.divide(self.vectors, vector_norms, 
                                          where=vector_norms!=0)
            
            # Calcula similaridade coseno
            similarities = np.dot(normalized_vectors, query_embedding)
            
            # Encontra os N documentos mais similares
            n_results = min(n_results, len(self.documents))
            indices = np.argsort(-similarities)[:n_results]
            distances = 1 - similarities[indices]  # Converte similaridade para distância
            
            # Prepara os resultados
            results = {
                "documents": [[self.documents[idx] for idx in indices]],
                "ids": [[str(idx) for idx in indices]],
                "metadatas": [[self.metadata[idx] for idx in indices] if self.metadata else None],
                "distances": [distances.tolist()]
            }
            
            return results
        
        return {"documents": [], "ids": [], "metadatas": [], "distances": []}
    
    def _save_data(self):
        """Salva os vetores, documentos e metadados no disco."""
        np.save(self.vectors_path, self.vectors)
        
        with open(self.documents_path, 'wb') as f:
            pickle.dump(self.documents, f)
            
        with open(self.metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)