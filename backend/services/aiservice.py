from .vectordb import VectorDBService


class AIService:
    def __init__(self):
        self.vector_db = VectorDBService()
    
    def answer_query(self, query, conversation_history=None):
        """
        Responde à consulta do usuário, considerando o histórico de conversas
        e buscando informações relevantes na base de conhecimento.
        """
        if conversation_history is None:
            conversation_history = []
            
        # Busca informações relevantes na base de conhecimento
        results = self.vector_db.query(query)
        
        # Por enquanto, vamos criar uma resposta simples
        if results and 'documents' in results and results['documents']:
            # Encontrou informações relevantes
            contexts = results['documents'][0]
            response = {
                "response": f"Com base no que sei: {' '.join(contexts[:2])}",
                "sources": results['documents'][0][:2]
            }
        else:
            # Fallback para quando não há informações relevantes
            response = {
                "response": "Não tenho informações suficientes para responder a essa pergunta.",
                "sources": []
            }
            
        return response
    
    def seed_knowledge_base(self, documents, metadatas=None):
        """
        Adiciona documentos à base de conhecimento.
        """
        return self.vector_db.add_documents(documents, metadatas)