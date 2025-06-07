import os
import io
from typing import List, Dict
from PyPDF2 import PdfReader
import re

class PDFProcessorService:
    def __init__(self):
        self.chunk_size = 1000  # Tamanho padrão do chunk em caracteres
        
    def process_pdf(self, file_content: bytes, filename: str, chunk_size: int = None) -> List[Dict]:
        """
        Processa um arquivo PDF e retorna chunks de texto organizados.
        """
        try:
            # Define o tamanho do chunk
            if chunk_size is None:
                chunk_size = self.chunk_size
                
            # Lê o PDF
            pdf_reader = PdfReader(io.BytesIO(file_content))
            
            # Extrai texto de todas as páginas
            full_text = ""
            total_pages = len(pdf_reader.pages)
            
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        full_text += f"\n\n[Página {page_num + 1}]\n{page_text}"
                except Exception as e:
                    print(f"Erro ao extrair texto da página {page_num + 1}: {str(e)}")
                    continue
            
            if not full_text.strip():
                return []
            
            # Limpa o texto
            cleaned_text = self._clean_text(full_text)
            
            # Cria chunks organizados
            chunks = self._create_organized_chunks(cleaned_text, filename, chunk_size, total_pages)
            
            return chunks
            
        except Exception as e:
            print(f"Erro ao processar PDF {filename}: {str(e)}")
            raise Exception(f"Erro ao processar PDF: {str(e)}")
    
    def _clean_text(self, text: str) -> str:
        """
        Limpa e formata o texto extraído do PDF.
        """
        if not text:
            return ""
        
        # Remove caracteres de controle e espaços extras
        text = re.sub(r'\x00-\x1f\x7f-\x9f', '', text)  # Remove caracteres de controle
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Remove múltiplas quebras de linha
        text = re.sub(r' +', ' ', text)  # Remove espaços extras
        text = re.sub(r'\t+', ' ', text)  # Substitui tabs por espaços
        
        # Remove linhas muito curtas (provavelmente lixo)
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if len(line) > 3:  # Mantém apenas linhas com mais de 3 caracteres
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip()
    
    def _create_organized_chunks(self, text: str, filename: str, chunk_size: int, total_pages: int) -> List[Dict]:
        """
        Divide o texto em chunks organizados com metadados consistentes.
        """
        chunks = []
        words = text.split()
        
        if not words:
            return chunks
        
        current_chunk = []
        current_page = 1
        
        # Extrai título do documento (primeiras palavras significativas)
        document_title = self._extract_document_title(text, filename)
        
        for word in words:
            # Detecta mudança de página
            if word.startswith('[Página') and word.endswith(']'):
                try:
                    page_num = int(word.replace('[Página', '').replace(']', '').strip())
                    current_page = page_num
                    continue
                except:
                    pass
            
            current_chunk.append(word)
            
            # Se o chunk atual atingiu o tamanho desejado
            if len(' '.join(current_chunk)) >= chunk_size:
                chunk_text = ' '.join(current_chunk)
                
                chunk_data = {
                    "text": chunk_text,
                    "title": document_title,
                    "filename": filename,
                    "source": f"PDF: {filename}",
                    "chunk_index": len(chunks),
                    "page_reference": current_page,
                    "total_pages": total_pages,
                    "keywords": self._extract_keywords(chunk_text),
                    "content_type": "pdf",
                    "char_count": len(chunk_text),
                    "word_count": len(current_chunk),
                    "url": f"file:///{filename}",  # URL fictícia para agrupamento
                    "metadata": {
                        "type": "pdf",
                        "filename": filename,
                        "page": current_page,
                        "total_pages": total_pages,
                        "chunk_index": len(chunks)
                    }
                }
                
                chunks.append(chunk_data)
                current_chunk = []
        
        # Adiciona o último chunk se houver conteúdo
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunk_data = {
                "text": chunk_text,
                "title": document_title,
                "filename": filename,
                "source": f"PDF: {filename}",
                "chunk_index": len(chunks),
                "page_reference": current_page,
                "total_pages": total_pages,
                "keywords": self._extract_keywords(chunk_text),
                "content_type": "pdf",
                "char_count": len(chunk_text),
                "word_count": len(current_chunk),
                "url": f"file:///{filename}",  # URL fictícia para agrupamento
                "metadata": {
                    "type": "pdf",
                    "filename": filename,
                    "page": current_page,
                    "total_pages": total_pages,
                    "chunk_index": len(chunks)
                }
            }
            chunks.append(chunk_data)
        
        return chunks
    
    def _extract_document_title(self, text: str, filename: str) -> str:
        """
        Extrai ou gera um título para o documento.
        """
        # Tenta extrair título das primeiras linhas
        lines = text.split('\n')[:10]  # Primeiras 10 linhas
        
        for line in lines:
            line = line.strip()
            # Se a linha tem tamanho razoável e não parece ser apenas números/códigos
            if 10 <= len(line) <= 100 and not re.match(r'^[\d\s\-\.]+$', line):
                # Remove caracteres especiais no início/fim
                title = re.sub(r'^[^\w]+|[^\w]+$', '', line)
                if title:
                    return title
        
        # Fallback: usa o nome do arquivo sem extensão
        return filename.replace('.pdf', '').replace('_', ' ').replace('-', ' ').title()
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extrai palavras-chave simples do texto.
        """
        # Remove pontuação e converte para minúsculas
        clean_text = re.sub(r'[^\w\s]', '', text.lower())
        words = clean_text.split()
        
        # Remove palavras muito comuns (stop words básicas)
        stop_words = {
            'o', 'a', 'os', 'as', 'um', 'uma', 'uns', 'umas', 'de', 'da', 'do', 'das', 'dos',
            'e', 'ou', 'mas', 'que', 'para', 'por', 'com', 'sem', 'em', 'na', 'no', 'nas', 'nos',
            'é', 'são', 'foi', 'será', 'ter', 'tem', 'tinha', 'pode', 'podem', 'muito', 'mais',
            'como', 'quando', 'onde', 'porque', 'se', 'já', 'também', 'só', 'ainda', 'isso',
            'este', 'esta', 'estes', 'estas', 'esse', 'essa', 'esses', 'essas', 'aquele', 'aquela'
        }
        
        # Filtra palavras relevantes (mais de 3 caracteres e não são stop words)
        keywords = [word for word in words if len(word) > 3 and word not in stop_words]
        
        # Conta frequência e retorna as mais comuns
        from collections import Counter
        word_freq = Counter(keywords)
        
        # Retorna até 10 palavras mais frequentes
        return [word for word, count in word_freq.most_common(10)]