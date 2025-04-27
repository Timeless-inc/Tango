import os
import json
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

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
        
        # Inicializa os atributos
        self._vectors = None
        self._documents = None
        self._metadata = None
        
    @property
    def vectors(self):
        if self._vectors is None:
            self._load_data()
        return self._vectors
    
    @vectors.setter
    def vectors(self, value):
        self._vectors = value
    
    @property
    def documents(self):
        if self._documents is None:
            self._load_data()
        return self._documents
    
    @documents.setter
    def documents(self, value):
        self._documents = value
    
    @property
    def metadata(self):
        if self._metadata is None:
            self._load_data()
        return self._metadata
    
    @metadata.setter
    def metadata(self, value):
        self._metadata = value
    
    def _load_data(self):
        """Carrega os dados do disco apenas quando necessário."""
        if os.path.exists(self.vectors_path) and os.path.exists(self.documents_path):
            self._vectors = np.load(self.vectors_path)
            with open(self.documents_path, 'rb') as f:
                self._documents = pickle.load(f)
                
            if os.path.exists(self.metadata_path):
                with open(self.metadata_path, 'r', encoding='utf-8') as f:
                    self._metadata = json.load(f)
            else:
                self._metadata = [None] * len(self._documents)
                
            print(f"Coleção '{self.collection_name}' carregada com sucesso. Documentos: {len(self._documents)}")
        else:
            # Cria nova base vazia
            self._vectors = np.array([]).reshape(0, self.model.get_sentence_embedding_dimension())
            self._documents = []
            self._metadata = []
            print(f"Coleção '{self.collection_name}' criada com sucesso.")
    
    def add_documents(self, documents, metadatas=None):
        """Adiciona documentos à coleção."""
        if not documents:
            return {"ids": []}
        
        # Verifica se metadatas foi fornecido, se não, cria lista de None
        if metadatas is None:
            metadatas = [None] * len(documents)
        
        # Gera embeddings para os novos documentos
        new_embeddings = self.model.encode(documents)
        
        # Normaliza os embeddings para distância coseno
        norms = np.linalg.norm(new_embeddings, axis=1, keepdims=True)
        normalized_embeddings = np.divide(new_embeddings, norms, where=norms!=0)
        
        # Adiciona os novos documentos e embeddings à coleção
        new_ids = list(range(len(self.documents), len(self.documents) + len(documents)))
        
        if len(self.vectors) == 0:
            self.vectors = normalized_embeddings
        else:
            self.vectors = np.vstack([self.vectors, normalized_embeddings])
        
        self.documents.extend(documents)
        self.metadata.extend(metadatas)
        
        # Salva a coleção atualizada
        self._save()
        
        return {"ids": new_ids}
    
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
            
            # Obtém os índices dos documentos mais similares
            top_indices = np.argsort(similarities)[::-1][:n_results]
            
            return {
                "documents": [self.documents[i] for i in top_indices],
                "ids": top_indices.tolist(),
                "metadatas": [self.metadata[i] for i in top_indices],
                "distances": [float(similarities[i]) for i in top_indices]
            }
        
        return {"documents": [], "ids": [], "metadatas": [], "distances": []}
    
    def delete(self, ids):
        """Remove documentos da coleção pelos IDs."""
        if not ids or not self.documents:
            return {"success": False}
        
        # Converte para conjunto para operações mais rápidas
        ids_set = set(ids)
        
        # Cria máscaras para remover os itens
        mask = np.ones(len(self.documents), dtype=bool)
        for idx in ids_set:
            if 0 <= idx < len(self.documents):
                mask[idx] = False
        
        # Aplica as máscaras
        self.vectors = self.vectors[mask]
        self.documents = [doc for i, doc in enumerate(self.documents) if mask[i]]
        self.metadata = [meta for i, meta in enumerate(self.metadata) if mask[i]]
        
        # Salva a coleção atualizada
        self._save()
        
        return {"success": True}
    
    def _save(self):
        """Salva a coleção no disco."""
        np.save(self.vectors_path, self.vectors)
        
        with open(self.documents_path, 'wb') as f:
            pickle.dump(self.documents, f)
            
        with open(self.metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)
            
        print(f"Coleção '{self.collection_name}' salva com sucesso. Documentos: {len(self.documents)}")
        
    def reset(self):
        """Reinicia a coleção, removendo todos os documentos."""
        self.vectors = np.array([]).reshape(0, self.model.get_sentence_embedding_dimension())
        self.documents = []
        self.metadata = []
        
        # Salva a coleção vazia
        self._save()
        
        return {"success": True}