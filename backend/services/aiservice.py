from services.vectordb import VectorDBService
from models.schemas import QueryResponse
import random
import re

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
            
            # Define threshold para considerar documentos relevantes
            high_threshold = 0.7
            
            # Filtra documentos relevantes baseados em palavras-chave e similaridade
            if any(keyword in query.lower() for keyword in ['mango', 'assistente', 'virtual']):
                for i, doc in enumerate(results['documents']):
                    if 'mango' in doc.lower() or 'assistente virtual' in doc.lower():
                        if results['distances'][i] > 0.5:
                            filtered_docs.append(doc)
                            
            elif any(keyword in query.lower() for keyword in ['campus', 'recife', 'ifpe', 'curso']):
                for i, doc in enumerate(results['documents']):
                    if 'campus recife' in doc.lower() or 'ifpe' in doc.lower() or 'curso' in doc.lower():
                        if 'mango' not in doc.lower():
                            filtered_docs.append(doc)
            
            # Se não encontramos documentos específicos, usamos o threshold
            if not filtered_docs:
                for i, doc in enumerate(results['documents']):
                    if results['distances'][i] > high_threshold:
                        filtered_docs.append(doc)
                        
                # Se ainda não temos documentos, usamos os com maior score (até 3)
                if not filtered_docs and results['documents']:
                    sorted_indices = sorted(range(len(results['distances'])), 
                                          key=lambda i: results['distances'][i], 
                                          reverse=True)[:3]
                    filtered_docs = [results['documents'][i] for i in sorted_indices]
            
            # Gera resposta com base nos documentos filtrados
            if filtered_docs:
                # Prepara o contexto para o LLM
                context = "\n".join(filtered_docs)
                
                # Instruções para o modelo formatar a resposta
                prompt = f"""
                Com base nas seguintes informações:
                
                {context}
                
                Responda à seguinte pergunta de forma natural, como um assistente educacional amigável:
                {query}
                
                Forneça uma resposta concisa e informativa, sem mencionar explicitamente que está consultando documentos.
                Não invente informações que não estejam no contexto fornecido.
                """
                
                # Usar modelo de linguagem para gerar resposta elaborada
                try:
                    # Aqui vamos simular a resposta refinada
                    # Em um ambiente real, você chamaria um modelo como GPT ou similar
                    elaborated_response = self._format_response(prompt, filtered_docs, query)
                    
                    response = {
                        "response": elaborated_response,
                        "sources": filtered_docs
                    }
                except Exception as e:
                    print(f"Erro ao gerar resposta elaborada: {e}")
                    # Fallback para o método anterior se houver erro
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
        
    def _format_response(self, prompt, documents, query):
        """
        Método aprimorado para formatar respostas de maneira mais natural e estruturada em parágrafos.
        """
        # Identifica o tema principal da pergunta
        query_lower = query.lower()
        
        # Extrai e organiza informações dos documentos
        key_info = []
        topics = set()
        
        # Identifica termos-chave mais abrangentes para agrupar informações relacionadas
        topic_groups = {
            'institucional': ['ifpe', 'campus', 'igarassu', 'recife', 'instituição'],
            'acadêmico': ['curso', 'disciplina', 'professor', 'aula', 'estudante', 'matrícula', 'ensino'],
            'assistente': ['mango', 'assistente', 'virtual', 'ai', 'inteligência artificial'],
            'calendário': ['data', 'prazo', 'período', 'evento', 'horário'],
            'serviços': ['biblioteca', 'restaurante', 'laboratório', 'bolsa', 'auxílio']
        }
        
        # Dicionário para armazenar informações agrupadas por tópico
        grouped_info = {topic: [] for topic in topic_groups.keys()}
        
        # Processar e categorizar informações dos documentos
        for doc in documents:
            # Remove pontuações excessivas e espaços extras
            clean_doc = ' '.join(doc.split())
            clean_doc = re.sub(r'\.+', '.', clean_doc)  # Remove múltiplos pontos
            clean_doc = re.sub(r'\s+', ' ', clean_doc)  # Remove múltiplos espaços
            
            # Categoriza o documento nos grupos de tópicos
            for topic, keywords in topic_groups.items():
                if any(keyword in clean_doc.lower() for keyword in keywords):
                    grouped_info[topic].append(clean_doc)
                    for keyword in keywords:
                        if keyword in clean_doc.lower():
                            topics.add(keyword)
            
            # Adiciona à lista geral de informações
            key_info.append(clean_doc)
        
        # Introduções diversificadas por tipo de pergunta
        intros = {
            "como": [
                "Sobre o que você perguntou, ",
                "Em relação à sua dúvida, ",
                "Respondendo à sua pergunta, "
            ],
            "qual": [
                "Com base nas informações disponíveis, ",
                "De acordo com os dados institucionais, ",
                "Conforme os registros, "
            ],
            "onde": [
                "Sobre a localização que você perguntou, ",
                "Em relação ao local mencionado, ",
                "Quanto ao lugar que você busca, "
            ],
            "quem": [
                "Sobre a pessoa que você mencionou, ",
                "Em relação ao profissional citado, ",
                "A respeito desse contato, "
            ],
            "quando": [
                "Sobre a data que você perguntou, ",
                "Em relação ao período mencionado, ",
                "Quanto ao cronograma, "
            ],
            "pergunta": [
                "Sobre o que você gostaria de saber, ",
                "Em resposta à sua questão, ",
                "A respeito da sua pergunta, "
            ],
            "default": [
                "Sobre esse assunto, ",
                "A respeito disso, ",
                "Em relação ao tema, "
            ]
        }
        
        # Seleciona introdução apropriada
        if 'como' in query_lower:
            intro = random.choice(intros["como"])
        elif any(word in query_lower for word in ['qual', 'quais']):
            intro = random.choice(intros["qual"])
        elif 'onde' in query_lower:
            intro = random.choice(intros["onde"])
        elif 'quem' in query_lower:
            intro = random.choice(intros["quem"])
        elif 'quando' in query_lower:
            intro = random.choice(intros["quando"])
        elif '?' in query:
            intro = random.choice(intros["pergunta"])
        else:
            intro = random.choice(intros["default"])
        
        # Construção da resposta por parágrafos
        if len(documents) == 1:
            # Com apenas um documento, formata de maneira mais direta
            content = key_info[0]
            # Remove possíveis repetições no início
            for word in ["o", "a", "os", "as", "um", "uma", "uns", "umas"]:
                if content.lower().startswith(word + " ") and intro.lower().endswith(word + " "):
                    content = content[len(word) + 1:]
            
            # Divide em sentenças e reorganiza em parágrafos lógicos (2-3 frases por parágrafo)
            sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', content) if s.strip()]
            
            if len(sentences) <= 3:
                # Se temos poucas frases, mantemos em um único parágrafo
                formatted_response = f"{intro}{' '.join(sentences)}"
            else:
                # Divide em dois parágrafos
                first_para = sentences[:len(sentences)//2]
                second_para = sentences[len(sentences)//2:]
                
                formatted_response = f"{intro}{' '.join(first_para)}\n\n{' '.join(second_para)}"
                
            return formatted_response
            
        else:
            # Para múltiplas fontes, organizamos por tópicos e criamos parágrafos temáticos
            # Remove frases duplicadas ou muito similares
            all_sentences = []
            for doc in key_info:
                sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', doc) if s.strip()]
                all_sentences.extend(sentences)
            
            unique_sentences = []
            for sentence in all_sentences:
                is_duplicate = False
                for existing in unique_sentences:
                    if len(sentence) > 15 and (sentence in existing or existing in sentence):
                        is_duplicate = True
                        break
                if not is_duplicate and sentence:
                    unique_sentences.append(sentence)
            
            # Organiza as sentenças por relevância e tópico
            primary_info = []
            secondary_info = []
            
            # Identifica sentenças principais com base na pergunta
            query_keywords = set(query_lower.split()) - {'o', 'a', 'os', 'as', 'e', 'é', 'são', 'como', 'qual', 'quais', 'quando', 'onde', 'quem', 'por', 'que', 'para'}
            
            for sentence in unique_sentences:
                sentence_lower = sentence.lower()
                
                # Se contém palavras-chave da pergunta, é informação primária
                if any(keyword in sentence_lower for keyword in query_keywords):
                    primary_info.append(sentence)
                else:
                    secondary_info.append(sentence)
            
            # Limita o número total de sentenças para manter a resposta concisa
            if len(primary_info) > 3:
                primary_info = primary_info[:3]
            
            if len(secondary_info) > 3:
                secondary_info = secondary_info[:3]
            
            # Constrói a resposta em formato de parágrafos
            paragraphs = []
            
            # Primeiro parágrafo com informação principal
            if primary_info:
                paragraphs.append(f"{intro}{' '.join(primary_info)}")
            
            # Segundo parágrafo com informação complementar
            if secondary_info:
                paragraphs.append(' '.join(secondary_info))
            
            # Se não temos parágrafos suficientes, usamos a abordagem anterior
            if not paragraphs:
                combined_info = ". ".join(unique_sentences)
                if not combined_info.endswith('.'):
                    combined_info += '.'
                
                return f"{intro}{combined_info}"
            
            # Retorna resposta formatada em parágrafos
            formatted_response = "\n\n".join(paragraphs)
            
            # Verifica se a resposta não está muito longa
            if len(formatted_response) > 800:
                # Tenta cortar no fim de um parágrafo
                cutoff = formatted_response[:797].rfind('\n\n')
                if cutoff > 300:
                    formatted_response = formatted_response[:cutoff]
                else:
                    # Tenta cortar no fim de uma frase
                    cutoff = formatted_response[:797].rfind('.')
                    if cutoff > 300:
                        formatted_response = formatted_response[:cutoff + 1]
                    else:
                        formatted_response = formatted_response[:797] + "..."
            
            return formatted_response
    
    def seed_knowledge_base(self, documents):
        """
        Adiciona novos documentos à base de conhecimento.
        """
        return self.vector_db.add_documents(documents)