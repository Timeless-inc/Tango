import requests
from bs4 import BeautifulSoup
import html2text
import validators
from urllib.parse import urljoin, urlparse
import time
from typing import List, Dict, Optional
import re

class WebScraperService:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = True
        self.html_converter.ignore_images = True
        self.html_converter.ignore_emphasis = False
        
    def scrape_url_chunked(self, url: str, chunk_size: int = 500) -> Dict:
        """
        Extrai conteúdo de uma URL e divide em chunks menores.
        """
        print(f"Iniciando scraping de: {url}")
        try:
            # Valida a URL
            if not validators.url(url):
                raise ValueError("URL inválida")
            
            # Faz a requisição
            print(f"Fazendo requisição para: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            print(f"Resposta recebida. Status: {response.status_code}")
            
            # Parse do HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove scripts, styles e outros elementos não relevantes
            for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
                script.decompose()
            
            # Extrai título
            title = soup.find('title')
            title_text = title.get_text().strip() if title else urlparse(url).netloc
            print(f"Título extraído: {title_text}")
            
            # Extrai conteúdo principal
            text_content = soup.get_text()
            clean_text = self._clean_text(text_content)
            print(f"Texto limpo extraído. Tamanho: {len(clean_text)} caracteres")
            
            if not clean_text or len(clean_text) < 50:
                print("Conteúdo extraído é muito pequeno ou vazio")
                return {
                    "url": url,
                    "title": title_text,
                    "chunks": [],
                    "total_chunks": 0,
                    "success": False,
                    "error": "Conteúdo extraído insuficiente"
                }
            
            # Divide o conteúdo em chunks simples
            chunks = self._create_simple_chunks(clean_text, title_text, url, chunk_size)
            print(f"Criados {len(chunks)} chunks")
            
            return {
                "url": url,
                "title": title_text,
                "chunks": chunks,
                "total_chunks": len(chunks),
                "success": True,
                "error": None
            }
            
        except Exception as e:
            print(f"Erro durante scraping de {url}: {str(e)}")
            return {
                "url": url,
                "title": None,
                "chunks": [],
                "total_chunks": 0,
                "success": False,
                "error": str(e)
            }
    
    def _create_simple_chunks(self, text: str, title: str, url: str, chunk_size: int) -> List[Dict]:
        """
        Divide o texto em chunks simples.
        """
        chunks = []
        words = text.split()
        
        if not words:
            return chunks
        
        current_chunk = []
        
        for word in words:
            current_chunk.append(word)
            
            # Se o chunk atual tem tamanho suficiente, cria um novo chunk
            if len(' '.join(current_chunk)) >= chunk_size:
                chunk_text = ' '.join(current_chunk)
                chunk_data = {
                    "text": chunk_text,
                    "title": title,
                    "url": url,
                    "chunk_index": len(chunks),
                    "keywords": self._extract_simple_keywords(chunk_text),
                    "content_type": "geral",
                    "sentence_count": len(chunk_text.split('.')),
                    "char_count": len(chunk_text)
                }
                chunks.append(chunk_data)
                current_chunk = []
        
        # Adiciona o último chunk se houver conteúdo
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunk_data = {
                "text": chunk_text,
                "title": title,
                "url": url,
                "chunk_index": len(chunks),
                "keywords": self._extract_simple_keywords(chunk_text),
                "content_type": "geral",
                "sentence_count": len(chunk_text.split('.')),
                "char_count": len(chunk_text)
            }
            chunks.append(chunk_data)
        
        return chunks
    
    def _extract_simple_keywords(self, text: str) -> List[str]:
        """
        Extrai palavras-chave simples do texto.
        """
        # Palavras comuns a ignorar
        stop_words = {
            'a', 'o', 'e', 'é', 'da', 'do', 'de', 'para', 'com', 'em', 'no', 'na', 'um', 'uma',
            'por', 'se', 'que', 'como', 'mais', 'ou', 'ao', 'aos', 'as', 'os', 'à', 'às'
        }
        
        # Extrai palavras significativas
        words = re.findall(r'\b[a-záàâãéêíóôõúç]{3,}\b', text.lower())
        keywords = [word for word in words if word not in stop_words]
        
        # Retorna as 5 palavras mais comuns
        word_freq = {}
        for word in keywords:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:5]]
    
    def _clean_text(self, text: str) -> str:
        """
        Limpa e formata o texto extraído.
        """
        if not text:
            return ""
        
        # Remove múltiplas quebras de linha
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # Remove espaços extras
        text = re.sub(r' +', ' ', text)
        
        # Remove linhas muito curtas
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if len(line) > 10:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip()
    
    def scrape_sitemap_chunked(self, base_url: str, max_pages: int = 10) -> List[Dict]:
        """
        Simples fallback para múltiplas páginas - apenas scrape da URL principal.
        """
        print(f"Scraping de sitemap para: {base_url}")
        return [self.scrape_url_chunked(base_url)]