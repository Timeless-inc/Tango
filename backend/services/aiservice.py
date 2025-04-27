from services.vectordb import VectorDBService
from models.schemas import QueryResponse

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
        results = self.vector_db.query(query, n_results=5)
        
        if results and 'documents' in results and results['documents'] and 'distances' in results:
            # Analisa os resultados por relevância e conteúdo
            filtered_docs = []
            
            # Primeiro, vamos extrair palavras-chave da consulta
            query_words = set(query.lower().split())
            important_words = {'o', 'a', 'os', 'as', 'e', 'é', 'são', 'tem', 'que'}
            query_keywords = query_words - important_words
            
            # Para cada documento, vamos verificar a relevância baseada em keywords e score
            high_threshold = 0.7
            
            # Se a consulta contém palavras-chave específicas, filtramos documentos relacionados
            if any(keyword in query.lower() for keyword in ['mango', 'assistente', 'virtual']):
                for i, doc in enumerate(results['documents']):
                    if 'mango' in doc.lower() or 'assistente virtual' in doc.lower():
                        if results['distances'][i] > 0.5:  # Um threshold mais baixo para matches diretos
                            filtered_docs.append(doc)
                            
            elif any(keyword in query.lower() for keyword in ['campus', 'recife', 'ifpe', 'curso']):
                for i, doc in enumerate(results['documents']):
                    if 'campus recife' in doc.lower() or 'ifpe' in doc.lower() or 'curso' in doc.lower():
                        if 'mango' not in doc.lower():  # Evita documentos sobre o Mango
                            filtered_docs.append(doc)
            
            # Se não encontramos documentos específicos, usamos o threshold
            if not filtered_docs:
                # Primeiro documento com alta similaridade
                for i, doc in enumerate(results['documents']):
                    if results['distances'][i] > high_threshold:
                        filtered_docs = [doc]
                        break
                        
                # Se ainda não temos documentos, usamos o com maior score
                if not filtered_docs and results['documents']:
                    best_idx = results['distances'].index(max(results['distances']))
                    filtered_docs = [results['documents'][best_idx]]
            
            # Formata a resposta com os documentos filtrados
            if filtered_docs:
                if len(filtered_docs) == 1:
                    response = {
                        "response": filtered_docs[0],
                        "sources": filtered_docs
                    }
                else:
                    # Junta múltiplos documentos relevantes com marcadores
                    combined_response = "\n".join([f"• {doc}" for doc in filtered_docs])
                    response = {
                        "response": combined_response,
                        "sources": filtered_docs
                    }
            else:
                response = {
                    "response": "Não tenho informações suficientes para responder a essa pergunta com precisão.",
                    "sources": []
                }
        else:
            # Fallback para quando não há informações relevantes
            response = {
                "response": "Não tenho informações suficientes para responder a essa pergunta.",
                "sources": []
            }
            
        return response
    
    def seed_knowledge_base(self, documents):
        """
        Adiciona novos documentos à base de conhecimento.
        """
        return self.vector_db.add_documents(documents)