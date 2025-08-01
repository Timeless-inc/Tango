from services.vectordb import VectorDBService
from sentence_transformers import SentenceTransformer
import random
import re
import json
import os
from collections import Counter, defaultdict
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Set
import numpy as np
from dataclasses import dataclass, field

@dataclass
class KnowledgeMetrics:
    document_count: int = 0
    topic_coverage: Dict[str, int] = field(default_factory=dict)
    quality_scores: List[float] = field(default_factory=list)
    knowledge_gaps: List[str] = field(default_factory=list)
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class QueryContext:
    intent: str = "general"
    complexity: float = 0.5
    domain: str = "educational"
    required_precision: float = 0.8
    temporal_relevance: bool = False

class AIService:
    def __init__(self):
        self.vector_db = VectorDBService()
        self.sentence_transformer = None
        
        # Configurações avançadas e adaptativas
        self.response_config = {
            'max_sources': 5,
            'similarity_threshold': 0.65,
            'max_response_length': 500,
            'prioritize_recent': True,
            'focus_keywords': True,
            'structured_response': True,
            'adaptive_threshold': True,
            'multi_strategy_search': True,
            'semantic_expansion': True,
            'quality_filtering': True,
            'context_awareness': True,
        }
        
        # Sistema de aprendizado e adaptação
        self.knowledge_metrics = KnowledgeMetrics()
        self.domain_expertise = {
            'educational': 0.9,
            'technical': 0.7,
            'administrative': 0.8,
            'general': 0.6
        }
        
        # Cache inteligente para otimização
        self.query_cache = {}
        self.pattern_cache = {}
        
        # Taxonomia de conhecimento para melhor categorização
        self.knowledge_taxonomy = {
            'institutional': ['campus', 'ifpe', 'instituto', 'história', 'missão'],
            'academic': ['curso', 'técnico', 'superior', 'graduação', 'ensino'],
            'procedural': ['como', 'processo', 'etapas', 'procedimento', 'inscrição'],
            'contact': ['telefone', 'email', 'contato', 'endereço', 'localização'],
            'temporal': ['quando', 'horário', 'data', 'prazo', 'período'],
            'qualitative': ['qualidade', 'avaliação', 'critério', 'requisito']
        }
        
        # Inicializa análise da base de conhecimento existente
        self._analyze_existing_knowledge()
    
    def _analyze_existing_knowledge(self):
        """Analisa a base de conhecimento existente para otimização"""
        try:
            if hasattr(self.vector_db, 'get_collection_info'):
                info = self.vector_db.get_collection_info()
                if info:
                    self.knowledge_metrics.document_count = info.get('count', 0)
                    print(f"Base de conhecimento existente: {self.knowledge_metrics.document_count} documentos")
            
            self._load_knowledge_metrics()
            
        except Exception as e:
            print(f"Aviso: Não foi possível analisar conhecimento existente: {str(e)}")
    
    def _load_knowledge_metrics(self):
        try:
            metrics_file = "data/knowledge_metrics.json"
            if os.path.exists(metrics_file):
                with open(metrics_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.knowledge_metrics.topic_coverage = data.get('topic_coverage', {})
                    self.knowledge_metrics.quality_scores = data.get('quality_scores', [])
                    self.knowledge_metrics.knowledge_gaps = data.get('knowledge_gaps', [])
        except Exception as e:
            print(f"Aviso: Não foi possível carregar métricas: {str(e)}")
    
    def _save_knowledge_metrics(self):
        try:
            os.makedirs("data", exist_ok=True)
            metrics_file = "data/knowledge_metrics.json"
            data = {
                'document_count': self.knowledge_metrics.document_count,
                'topic_coverage': self.knowledge_metrics.topic_coverage,
                'quality_scores': self.knowledge_metrics.quality_scores,
                'knowledge_gaps': self.knowledge_metrics.knowledge_gaps,
                'last_updated': self.knowledge_metrics.last_updated
            }
            with open(metrics_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Aviso: Não foi possível salvar métricas: {str(e)}")
    
    def seed_knowledge_base(self, documents):
        """
        Adiciona documentos à base de conhecimento com análise avançada e adaptação.
        """
        print(f"🧠 Processando {len(documents)} novos documentos para a base de conhecimento...")
        
        if not documents:
            print("⚠️  Nenhum documento fornecido")
            return {"ids": []}
        
        try:
            # Análise avançada dos novos documentos
            analyzed_docs = self._analyze_new_documents(documents)
            
            # Processamento inteligente baseado no tipo de conteúdo
            processed_docs = self._intelligent_document_processing(analyzed_docs)
            
            # Detecção de lacunas de conhecimento
            knowledge_gaps = self._detect_knowledge_gaps(processed_docs)
            
            # Adição dos documentos com metadados enriquecidos
            result = self.vector_db.add_documents(processed_docs)
            
            # Atualização das métricas de conhecimento
            self._update_knowledge_metrics(processed_docs, knowledge_gaps)
            
            # Otimização automática da configuração
            self._optimize_config_for_new_knowledge(processed_docs)
            
            print(f"✅ {len(processed_docs)} documentos adicionados com sucesso!")
            print(f"📊 Cobertura de tópicos atualizada: {len(self.knowledge_metrics.topic_coverage)} categorias")
            print(f"🔍 {len(knowledge_gaps)} lacunas de conhecimento detectadas")
            
            # Salva métricas atualizadas
            self._save_knowledge_metrics()
            
            return {
                **result,
                "analyzed_documents": len(analyzed_docs),
                "knowledge_gaps": knowledge_gaps,
                "topic_coverage": self.knowledge_metrics.topic_coverage
            }
            
        except Exception as e:
            print(f"❌ Erro ao processar documentos: {str(e)}")
            raise e
    
    def _analyze_new_documents(self, documents: List[str]) -> List[Dict[str, Any]]:
        analyzed = []
        
        for i, doc in enumerate(documents):
            analysis = {
                'content': doc,
                'id': f"doc_{i}_{datetime.now().timestamp()}",
                'type': self._classify_document_type(doc),
                'quality_score': self._assess_document_quality_advanced(doc),
                'topics': self._extract_document_topics(doc),
                'complexity': self._calculate_content_complexity(doc),
                'informativeness': self._calculate_informativeness(doc),
                'domain_relevance': self._assess_domain_relevance(doc),
                'structural_analysis': self._analyze_document_structure(doc)
            }
            analyzed.append(analysis)
        
        return analyzed
    
    def _classify_document_type(self, doc: str) -> str:
        doc_lower = doc.lower()
        
        if any(word in doc_lower for word in ['pdf:', 'arquivo:', '.pdf']):
            return 'pdf_document'
        elif any(word in doc_lower for word in ['web:', 'url:', 'http', 'www']):
            return 'web_content'
        elif any(word in doc_lower for word in ['curso', 'disciplina', 'programa', 'currículo']):
            return 'academic_content'
        elif any(word in doc_lower for word in ['contato', 'telefone', 'endereço', 'localização']):
            return 'contact_information'
        elif any(word in doc_lower for word in ['processo', 'procedimento', 'como', 'etapas']):
            return 'procedural_content'
        elif any(word in doc_lower for word in ['história', 'fundação', 'início', 'origem']):
            return 'historical_content'
        else:
            return 'general_information'
    
    def _assess_document_quality_advanced(self, doc: str) -> float:
        score = 0.5  # Base
        
        length = len(doc)
        words = doc.split()
        sentences = len(re.findall(r'[.!?]+', doc))
        
        # Tamanho apropriado
        if 200 <= length <= 2000:
            score += 0.15
        elif 100 <= length < 200:
            score += 0.1
        elif length < 100:
            score -= 0.2
        
        # Estrutura
        if len(words) > 0:
            avg_word_length = sum(len(word) for word in words) / len(words)
            if 4 <= avg_word_length <= 8:
                score += 0.1
            
            sentences_per_100_words = (sentences / len(words)) * 100 if words else 0
            if 3 <= sentences_per_100_words <= 10:
                score += 0.1
        
        # Riqueza de vocabulário
        if len(words) > 10:
            unique_words = len(set(word.lower() for word in words))
            vocabulary_richness = unique_words / len(words)
            if vocabulary_richness > 0.6:
                score += 0.15
        
        # Informações estruturadas
        if re.search(r'\\d+', doc):
            score += 0.05
        if re.search(r'[A-Z][a-z]+ [A-Z][a-z]+', doc):
            score += 0.05
        
        # Qualidade educacional específica
        educational_indicators = [
            'campus', 'ifpe', 'curso', 'técnico', 'superior', 'ensino',
            'educação', 'formação', 'estudante', 'professor'
        ]
        edu_score = sum(1 for indicator in educational_indicators if indicator in doc.lower())
        score += min(edu_score * 0.02, 0.1)
        
        return max(0.1, min(1.0, score))
    
    def answer_query(self, query: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        if conversation_history is None:
            conversation_history = []
        
        try:
            # Busca básica usando o vector_db
            results = self.vector_db.query(query, n_results=8)
            
            if not results or len(results['documents']) == 0:
                return {
                    "response": "Não encontrei informações específicas sobre sua pergunta. Poderia reformular ou ser mais específico?",
                    "sources": [],
                    "confidence": 0.0,
                    "query_type": "sem_resultados"
                }
            
            # Filtra documentos com similaridade mínima
            threshold = 0.3
            relevant_docs = []
            
            for i, distance in enumerate(results['distances']):
                if distance >= threshold:
                    relevant_docs.append({
                        'text': results['documents'][i],
                        'distance': distance,
                        'quality': self._assess_document_quality_advanced(results['documents'][i]),
                        'index': i
                    })
            
            if not relevant_docs:
                return {
                    "response": "Não tenho informações suficientemente precisas para responder com confiança a essa pergunta.",
                    "sources": [],
                    "confidence": 0.0,
                    "query_type": "baixa_relevancia"
                }
            
            # Ordena por pontuação combinada
            for doc in relevant_docs:
                doc['combined_score'] = (doc['distance'] * 0.7) + (doc['quality'] * 0.3)
            
            relevant_docs.sort(key=lambda x: x['combined_score'], reverse=True)
            relevant_docs = relevant_docs[:min(5, len(relevant_docs))]
            
            # Gera resposta usando método existente
            consolidated_content = self._analyze_and_consolidate_content(
                query, [doc['text'] for doc in relevant_docs]
            )
            response_text = self._generate_comprehensive_response(query, consolidated_content)
            
            # Calcula confiança
            confidence = sum(doc['combined_score'] for doc in relevant_docs) / len(relevant_docs)
            confidence = min(0.95, confidence)
            
            return {
                "response": response_text,
                "sources": [f"Documento {i+1}" for i in range(len(relevant_docs))],
                "confidence": round(confidence, 2),
                "query_type": "informativa",
                "document_count": len(relevant_docs)
            }
            
        except Exception as e:
            print(f"Erro em answer_query: {str(e)}")
            return {
                "response": "Desculpe, ocorreu um erro ao processar sua pergunta. Tente novamente.",
                "sources": [],
                "confidence": 0.0,
                "query_type": "erro"
            }
    
    def get_knowledge_status(self) -> Dict[str, Any]:
        """Retorna status completo da base de conhecimento"""
        return {
            "total_documents": self.knowledge_metrics.document_count,
            "topic_coverage": self.knowledge_metrics.topic_coverage,
            "knowledge_gaps": self.knowledge_metrics.knowledge_gaps,
            "domain_expertise": self.domain_expertise,
            "last_updated": self.knowledge_metrics.last_updated,
            "config_status": self.response_config,
            "readiness_score": self._calculate_readiness_score()
        }
    
    def _calculate_readiness_score(self) -> float:
        """Calcula pontuação de prontidão do sistema"""
        score = 0.0
        
        # Pontuação baseada na quantidade de documentos
        doc_score = min(1.0, self.knowledge_metrics.document_count / 50)
        score += doc_score * 0.3
        
        # Pontuação baseada na cobertura de tópicos
        topic_score = min(1.0, len(self.knowledge_metrics.topic_coverage) / 8)
        score += topic_score * 0.4
        
        # Pontuação baseada na ausência de lacunas críticas
        gap_penalty = min(0.3, len(self.knowledge_metrics.knowledge_gaps) * 0.05)
        score += (0.3 - gap_penalty)
        
        return min(1.0, score)
    
    # Métodos auxiliares simplificados para manter compatibilidade
    def _extract_document_topics(self, doc: str) -> List[str]:
        """Extrai tópicos principais do documento"""
        topics = []
        doc_lower = doc.lower()
        
        topic_mapping = {
            'cursos_academicos': ['curso', 'técnico', 'superior', 'graduação'],
            'informacoes_campus': ['campus', 'igarassu', 'localização', 'endereço'],
            'contato_comunicacao': ['telefone', 'email', 'contato'],
            'processos_procedimentos': ['inscrição', 'matrícula', 'processo'],
            'historia_institucional': ['história', 'fundação', 'início'],
        }
        
        for topic, keywords in topic_mapping.items():
            if any(keyword in doc_lower for keyword in keywords):
                topics.append(topic)
        
        return topics if topics else ['informacao_geral']
    
    def _calculate_content_complexity(self, doc: str) -> float:
        """Calcula complexidade do conteúdo"""
        words = doc.split()
        if not words:
            return 0.0
        
        avg_word_length = sum(len(word) for word in words) / len(words)
        long_words_ratio = sum(1 for word in words if len(word) > 7) / len(words)
        
        complexity = (avg_word_length / 10) + long_words_ratio
        return min(1.0, complexity)
    
    def _calculate_informativeness(self, doc: str) -> float:
        """Calcula o nível de informatividade do documento"""
        score = 0.0
        doc_lower = doc.lower()
        
        if any(indicator in doc_lower for indicator in ['é', 'está', 'oferece']):
            score += 0.2
        if re.findall(r'\\d+', doc):
            score += 0.15
        if any(indicator in doc_lower for indicator in ['telefone', 'email']):
            score += 0.25
        if any(indicator in doc_lower for indicator in ['campus igarassu', 'ifpe']):
            score += 0.1
        
        return min(1.0, score)
    
    def _assess_domain_relevance(self, doc: str) -> Dict[str, float]:
        doc_lower = doc.lower()
        
        domain_keywords = {
            'educational': ['educação', 'ensino', 'curso', 'ifpe'],
            'administrative': ['matrícula', 'processo', 'documentos'],
            'institutional': ['campus', 'história', 'estrutura'],
        }
        
        relevance = {}
        for domain, keywords in domain_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in doc_lower)
            relevance[domain] = min(1.0, matches / len(keywords))
        
        return relevance
    
    def _analyze_document_structure(self, doc: str) -> Dict[str, Any]:
        analysis = {
            'has_headings': bool(re.search(r'^#+ ', doc, re.MULTILINE)),
            'has_contact_info': bool(re.search(r'\\(\\d+\\)\\s*\\d+', doc)),
            'paragraph_count': len([p for p in doc.split('\\n\\n') if p.strip()]),
            'structure_score': 0.5
        }
        
        return analysis
    
    # Métodos existentes mantidos para compatibilidade
    def _intelligent_document_processing(self, analyzed_docs: List[Dict]) -> List[str]:
        return [doc['content'] for doc in analyzed_docs]
    
    def _detect_knowledge_gaps(self, processed_docs: List[str]) -> List[str]:
        essential_topics = ['localização', 'contato', 'cursos', 'história']
        all_content = ' '.join(processed_docs).lower()
        
        gaps = []
        for topic in essential_topics:
            if topic not in all_content:
                gaps.append(f"Informações sobre {topic}")
        
        return gaps
    
    def _update_knowledge_metrics(self, processed_docs: List[str], gaps: List[str]):
        self.knowledge_metrics.document_count += len(processed_docs)
        self.knowledge_metrics.knowledge_gaps = gaps
        self.knowledge_metrics.last_updated = datetime.now().isoformat()
        
        for doc in processed_docs:
            doc_lower = doc.lower()
            for category, keywords in self.knowledge_taxonomy.items():
                if any(keyword in doc_lower for keyword in keywords):
                    self.knowledge_metrics.topic_coverage[category] = \
                        self.knowledge_metrics.topic_coverage.get(category, 0) + 1
    
    def _optimize_config_for_new_knowledge(self, processed_docs: List[str]):
        avg_length = sum(len(doc) for doc in processed_docs) / len(processed_docs) if processed_docs else 0
        
        if avg_length > 1000:
            self.response_config['similarity_threshold'] = max(0.6, 
                self.response_config['similarity_threshold'] - 0.05)
        elif avg_length < 300:
            self.response_config['similarity_threshold'] = min(0.8, 
                self.response_config['similarity_threshold'] + 0.05)
    
    # Métodos existentes para manter funcionamento atual
    def _analyze_and_consolidate_content(self, query: str, documents: List[str]) -> Dict[str, Any]:
        if not documents:
            return {"consolidated_text": "", "content_type": "general"}
        
        primary_content = documents[0]
        content_type = self._identify_query_type(query.lower())
        
        return {
            "consolidated_text": primary_content,
            "content_type": content_type
        }
    
    def _identify_query_type(self, query: str) -> str:
        if any(word in query for word in ["onde", "localização", "endereço"]):
            return "localização"
        elif any(word in query for word in ["curso", "graduação", "técnico"]):
            return "cursos"
        elif any(word in query for word in ["contato", "telefone", "email"]):
            return "contato"
        elif any(word in query for word in ["história", "quando"]):
            return "história"
        else:
            return "geral"
    
    def _generate_comprehensive_response(self, query: str, consolidated_content: Dict) -> str:
        content = consolidated_content["consolidated_text"]
        content_type = consolidated_content["content_type"]
        
        structured_info = self._extract_structured_information(content)
        
        if content_type == "cursos":
            return self._format_courses_response(structured_info)
        elif content_type == "localização":
            return self._format_location_response(structured_info)
        elif content_type == "contato":
            return self._format_contact_response(structured_info)
        elif content_type == "história":
            return self._format_history_response(structured_info)
        else:
            return self._format_general_response(structured_info, content)
    
    def _extract_structured_information(self, content: str) -> Dict[str, Any]:
        info = {}
        lines = content.split('\\n')
        
        technical_prefixes = ['fonte:', 'url:', 'tipo:', 'palavras-chave:']
        clean_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            line_lower = line.lower()
            if any(line_lower.startswith(prefix) for prefix in technical_prefixes):
                continue
            if line.startswith('http') and '://' in line:
                continue
            
            clean_lines.append(line)
        
        # Extrai informações específicas
        for line in clean_lines:
            line_lower = line.lower()
            
            if any(word in line_lower for word in ['rodovia', 'rua', 'avenida']):
                info['endereco'] = line
            
            if '(' in line and ')' in line and len([c for c in line if c.isdigit()]) >= 8:
                phone_match = re.search(r'\\(\\d{2}\\)\\s*\\d{4,5}[-\\s]*\\d{4}', line)
                if phone_match:
                    info['telefone'] = phone_match.group()
            
            if 'igarassu' in line_lower and len(line) > 20:
                info.setdefault('campus_info', []).append(line)
            
            if any(word in line_lower for word in ['técnico em', 'bacharelado', 'tecnologia em']):
                info.setdefault('cursos', []).append(line)
        
        # Parágrafos informativos
        clean_content = '\\n'.join(clean_lines)
        paragraphs = [p.strip() for p in clean_content.split('\\n\\n') if len(p.strip()) > 50]
        info['paragraphs'] = paragraphs[:3]
        
        return info
    
    def _format_courses_response(self, info: Dict) -> str:
        response = "🎓 **Cursos Oferecidos no Campus Igarassu**\\n\\n"
        
        response += "**📚 Cursos Técnicos Subsequentes:**\\n"
        response += "• Técnico em Logística\\n"
        response += "• Técnico em Informática para Internet (IPI)\\n"
        response += "• Técnico em Química\\n\\n"
        
        response += "**🎓 Cursos Superiores:**\\n"
        response += "• Tecnologia em Gestão da Qualidade\\n"
        response += "• Tecnologia em Sistemas para Internet (TSI)\\n"
        response += "• Bacharelado em Administração\\n\\n"
        
        response += "**📋 Qualificação Profissional:**\\n"
        response += "• Almoxarife\\n"
        response += "• Operador de Computador\\n\\n"
        
        response += "**🔧 Formação Inicial e Continuada (FIC):**\\n"
        response += "• Cursos pelo Programa Nacional de Acesso ao Ensino Técnico e Emprego (Pronatec)"
        
        return response
    
    def _format_location_response(self, info: Dict) -> str:
        response = "📍 **Localização do Campus Igarassu**\\n\\n"
        
        if 'endereco' in info:
            response += f"O campus está localizado na **{info['endereco']}**.\\n\\n"
        
        if 'campus_info' in info:
            response += "**Sobre o Campus:**\\n"
            for item in info['campus_info'][:2]:
                response += f"• {item}\\n"
        
        return response.strip()
    
    def _format_contact_response(self, info: Dict) -> str:
        response = "📞 **Como Entrar em Contato**\\n\\n"
        
        if 'telefone' in info:
            response += f"**Telefone:** {info['telefone']}\\n\\n"
        
        if 'endereco' in info:
            response += f"**Endereço:** {info['endereco']}\\n\\n"
        
        response += "**Outras Formas de Contato:**\\n"
        response += "• Visite o campus pessoalmente\\n"
        response += "• Acesse o portal oficial do IFPE"
        
        return response.strip()
    
    def _format_history_response(self, info: Dict) -> str:
        response = "📚 **História do Campus Igarassu**\\n\\n"
        
        if 'paragraphs' in info:
            for paragraph in info['paragraphs'][:2]:
                if len(paragraph) > 80:
                    response += f"{paragraph}\\n\\n"
        
        return response.strip()
    
    def _format_general_response(self, info: Dict, full_content: str) -> str:
        if 'paragraphs' in info and info['paragraphs']:
            response = ""
            for paragraph in info['paragraphs'][:2]:
                if len(paragraph) > 50:
                    response += f"{paragraph}\\n\\n"
            return response.strip()
        
        # Fallback para conteúdo limpo
        lines = full_content.split('\\n')
        clean_lines = []
        
        for line in lines:
            line = line.strip()
            if (line and 
                not line.lower().startswith(('fonte:', 'url:', 'tipo:')) and
                not line.startswith('http') and
                len(line) > 20):
                clean_lines.append(line)
        
        if clean_lines:
            return '\\n'.join(clean_lines[:3])
        
        return "Informações disponíveis sobre o Campus Igarassu do IFPE."
