import requests
from bs4 import BeautifulSoup
import html2text
import validators
from urllib.parse import urljoin, urlparse
import time
from typing import List, Dict, Optional
import re
from collections import Counter

class WebScraperService:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none'
        })
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = True
        self.html_converter.ignore_emphasis = False
        self.html_converter.body_width = 0  # Sem quebra de linha automática
        
        # Seletores CSS para conteúdo principal (expandidos)
        self.content_selectors = [
            'main', 'article', '[role="main"]', 
            '.content', '.main-content', '.post-content',
            '.entry-content', '.article-content', '.page-content',
            '#content', '#main-content', '.container-content',
            '.text-content', '.body-content', '.page-body',
            '.content-area', '.primary-content', '[data-content]',
            '.post-body', '.article-body', 'section.content'
        ]
        
        # Tags irrelevantes para remoção (expandidas)
        self.noise_tags = [
            'script', 'style', 'nav', 'footer', 'header', 
            'aside', 'advertisement', '.ad', '.ads',
            '.social-share', '.comments', '.cookie-notice',
            '.popup', '.modal', '.sidebar', '.breadcrumb',
            '.navigation', '.menu', '.nav-menu', '.footer-menu',
            '.social-links', '.share-buttons', '.related-posts',
            '.widget', '.banner', '.promo', '.newsletter'
        ]
        
        # Seletores específicos para sites educacionais
        self.educational_selectors = [
            '.campus-info', '.institution-content', '.about-content',
            '.course-info', '.academic-content', '.education-content',
            '.ifpe-content', '.university-content', '.college-content'
        ]
        
    def scrape_url_chunked(self, url: str, chunk_size: int = 800) -> Dict:
        """
        Extrai conteúdo de uma URL com análise inteligente e divisão otimizada em chunks.
        """
        print(f"Iniciando scraping inteligente de: {url}")
        
        # Verifica se é um site do IFPE e usa método especializado
        if 'ifpe.edu.br' in url:
            return self._scrape_ifpe_site_enhanced(url, chunk_size)
        
        try:
            # Valida a URL
            if not validators.url(url):
                raise ValueError("URL inválida")
            
            # Faz a requisição com headers mais robustos
            print(f"Fazendo requisição para: {url}")
            
            # Adiciona delay para não parecer bot
            time.sleep(1)
            
            try:
                response = self.session.get(url, timeout=30, allow_redirects=True, verify=False)
                response.raise_for_status()
            except requests.exceptions.SSLError:
                # Tenta novamente sem verificação SSL se der erro
                print("Erro SSL, tentando sem verificação...")
                response = self.session.get(url, timeout=30, allow_redirects=True, verify=False)
                response.raise_for_status()
            except requests.exceptions.Timeout:
                raise Exception("Timeout na requisição - servidor não responde")
            except requests.exceptions.ConnectionError:
                raise Exception("Erro de conexão - site pode estar fora do ar")
            except requests.exceptions.HTTPError as e:
                if response.status_code == 403:
                    raise Exception("Acesso negado - site bloqueia bots")
                elif response.status_code == 404:
                    raise Exception("Página não encontrada")
                else:
                    raise Exception(f"Erro HTTP {response.status_code}")
            
            response.encoding = response.apparent_encoding  # Detecta encoding correto
            print(f"Resposta recebida. Status: {response.status_code}")
            
            # Parse do HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extrai metadados da página
            metadata = self._extract_metadata(soup, url)
            print(f"Título extraído: {metadata['title']}")
            
            # Remove elementos irrelevantes
            self._remove_noise_elements(soup)
            
            # Extrai conteúdo principal usando seletores inteligentes
            main_content = self._extract_main_content(soup)
            
            # Processa e limpa o texto
            clean_text = self._advanced_text_cleaning(main_content)
            print(f"Texto limpo extraído. Tamanho: {len(clean_text)} caracteres")
            
            if not clean_text or len(clean_text) < 100:
                print("Conteúdo extraído é muito pequeno ou vazio")
                return {
                    "url": url,
                    "title": metadata['title'],
                    "description": metadata['description'],
                    "chunks": [],
                    "total_chunks": 0,
                    "success": False,
                    "error": "Conteúdo extraído insuficiente"
                }
            
            # Cria chunks inteligentes baseados em estrutura semântica
            chunks = self._create_intelligent_chunks(
                clean_text, metadata, url, chunk_size
            )
            print(f"Criados {len(chunks)} chunks inteligentes")
            
            return {
                "url": url,
                "title": metadata['title'],
                "description": metadata['description'],
                "chunks": chunks,
                "total_chunks": len(chunks),
                "success": True,
                "error": None,
                "metadata": metadata
            }
            
        except Exception as e:
            print(f"Erro durante scraping de {url}: {str(e)}")
            return {
                "url": url,
                "title": None,
                "description": None,
                "chunks": [],
                "total_chunks": 0,
                "success": False,
                "error": str(e)
            }
    
    def _scrape_ifpe_site_enhanced(self, url: str, chunk_size: int = 800) -> Dict:
        """Método especializado para sites do IFPE com múltiplas estratégias."""
        print(f"🎯 Usando método especializado para site IFPE: {url}")
        
        # Headers específicos para sites educacionais brasileiros
        ifpe_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Referer': 'https://www.google.com/',
            'DNT': '1'
        }
        
        # Múltiplas tentativas com diferentes estratégias
        strategies = [
            {'delay': 2, 'timeout': 30, 'verify_ssl': True},
            {'delay': 5, 'timeout': 45, 'verify_ssl': True},
            {'delay': 3, 'timeout': 60, 'verify_ssl': False}
        ]
        
        for i, strategy in enumerate(strategies):
            try:
                print(f"Tentativa {i+1}/3 com delay de {strategy['delay']}s...")
                
                # Delay maior para sites institucionais
                time.sleep(strategy['delay'])
                
                # Cria nova sessão com headers específicos
                session = requests.Session()
                session.headers.update(ifpe_headers)
                
                response = session.get(
                    url, 
                    timeout=strategy['timeout'], 
                    allow_redirects=True,
                    verify=strategy['verify_ssl']
                )
                
                print(f"Status HTTP: {response.status_code}")
                
                if response.status_code == 200:
                    response.encoding = response.apparent_encoding
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extrai metadados
                    metadata = self._extract_ifpe_metadata(soup, url)
                    print(f"Título extraído (IFPE): {metadata['title']}")
                    
                    # Extrai conteúdo específico do IFPE
                    content = self._extract_ifpe_content(soup)
                    
                    if content.strip() and len(content) > 100:
                        # Limpa o texto
                        clean_text = self._advanced_text_cleaning(content)
                        print(f"Texto IFPE extraído. Tamanho: {len(clean_text)} caracteres")
                        
                        # Cria chunks
                        chunks = self._create_intelligent_chunks(
                            clean_text, metadata, url, chunk_size
                        )
                        
                        print(f"✅ Site IFPE processado com sucesso! {len(chunks)} chunks criados")
                        
                        return {
                            "url": url,
                            "title": metadata['title'],
                            "description": metadata['description'],
                            "chunks": chunks,
                            "total_chunks": len(chunks),
                            "success": True,
                            "error": None,
                            "metadata": metadata
                        }
                    else:
                        print("⚠️ Conteúdo IFPE extraído vazio ou insuficiente")
                        
                elif response.status_code == 403:
                    print(f"⚠️ Acesso negado (403) - tentativa {i+1}")
                    continue
                else:
                    print(f"⚠️ Status HTTP {response.status_code} - tentativa {i+1}")
                    continue
                    
            except Exception as e:
                print(f"⚠️ Tentativa {i+1} falhou: {str(e)}")
                continue
        
        print("❌ Todas as tentativas falharam para o site IFPE")
        return {
            "url": url,
            "title": None,
            "description": None,
            "chunks": [],
            "total_chunks": 0,
            "success": False,
            "error": "Todas as tentativas de acesso ao site IFPE falharam"
        }
    
    def _extract_ifpe_metadata(self, soup: BeautifulSoup, url: str) -> Dict:
        """Extrai metadados específicos de páginas do IFPE."""
        title = None
        description = None
        
        # Tenta extrair título
        title_selectors = ['title', 'h1', '.page-title', '.content-title']
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text().strip()
                if title:
                    break
        
        if not title:
            title = "Página IFPE"
        
        # Tenta extrair descrição
        desc_selectors = [
            'meta[name="description"]', 
            'meta[property="og:description"]',
            '.description',
            '.summary'
        ]
        for selector in desc_selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    description = element.get('content', '').strip()
                else:
                    description = element.get_text().strip()
                if description:
                    break
        
        if not description:
            description = "Conteúdo do site IFPE"
        
        # Extrai campus da URL
        campus = self._extract_campus_from_url(url)
        
        return {
            'title': title,
            'description': description,
            'campus': campus,
            'institution': 'IFPE',
            'type': 'educational_content'
        }
    
    def _extract_ifpe_content(self, soup: BeautifulSoup) -> str:
        """Extrai conteúdo específico de páginas do IFPE."""
        # Remove elementos indesejados
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            tag.decompose()
        
        # Seletores específicos para sites do IFPE
        ifpe_selectors = [
            '.conteudo',
            '.content',
            '.main-content',
            '#content',
            '.documentContent',
            '.newsImageContainer + *',
            'article',
            '.portalMessage',
            '.documentDescription',
            '.text-content',
            '.page-content'
        ]
        
        content = ""
        
        # Tenta seletores específicos do IFPE
        for selector in ifpe_selectors:
            elements = soup.select(selector)
            if elements:
                content = " ".join([elem.get_text().strip() for elem in elements])
                if len(content) > 200:  # Conteúdo substancial
                    break
        
        # Fallback: procura por divs com texto sobre educação
        if not content.strip() or len(content) < 200:
            educational_keywords = ['pet', 'programa', 'educação', 'tutorial', 'ifpe', 'instituto', 'campus']
            
            for div in soup.find_all(['div', 'section', 'article']):
                div_text = div.get_text().strip()
                if len(div_text) > 100:
                    text_lower = div_text.lower()
                    keyword_count = sum(1 for keyword in educational_keywords if keyword in text_lower)
                    
                    if keyword_count >= 2:
                        if len(div_text) > len(content):
                            content = div_text
        
        # Fallback específico para PET: busca informações estruturadas
        if 'pet' in content.lower() or len(content) < 500:
            pet_content = self._extract_pet_structured_content(soup)
            if pet_content and len(pet_content) > len(content):
                content = pet_content
        
        # Último fallback: todo o texto da página
        if not content.strip():
            content = soup.get_text()
        
        return content
    
    def _extract_pet_structured_content(self, soup: BeautifulSoup) -> str:
        """Extrai conteúdo estruturado específico para páginas do PET."""
        structured_content = []
        
        # Procura por títulos e suas seções
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        for heading in headings:
            heading_text = heading.get_text().strip()
            if not heading_text:
                continue
                
            # Adiciona o título
            structured_content.append(f"\n{heading_text}\n")
            
            # Procura pelo conteúdo que segue este título
            current_element = heading.find_next_sibling()
            section_content = []
            
            while current_element and current_element.name not in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                if current_element.name == 'p':
                    text = current_element.get_text().strip()
                    if text and len(text) > 20:
                        section_content.append(text)
                elif current_element.name in ['ul', 'ol']:
                    # Processa listas - método melhorado
                    list_items = current_element.find_all('li')
                    if list_items:
                        # Adiciona cabeçalho da lista se existir
                        prev_element = current_element.find_previous_sibling()
                        if prev_element and prev_element.name in ['p', 'strong', 'b']:
                            prev_text = prev_element.get_text().strip()
                            if any(keyword in prev_text.lower() for keyword in ['discentes', 'integrantes', 'membros', 'compõem']):
                                section_content.append(prev_text)
                        
                        # Adiciona cada item da lista
                        for li in list_items:
                            li_text = li.get_text().strip()
                            if li_text and len(li_text) > 5:
                                # Mantém formatação original se não começar com bullet
                                if not li_text.startswith('•'):
                                    section_content.append(f"• {li_text}")
                                else:
                                    section_content.append(li_text)
                elif current_element.name == 'div':
                    text = current_element.get_text().strip()
                    if text and len(text) > 20:
                        # Verifica se não é navegação
                        if not self._is_navigation_text(text):
                            # Se contém lista de nomes, processa especialmente
                            if self._contains_names_list(text):
                                formatted_names = self._format_names_list(text)
                                section_content.extend(formatted_names)
                            else:
                                section_content.append(text)
                
                current_element = current_element.find_next_sibling()
            
            # Adiciona o conteúdo da seção se houver
            if section_content:
                structured_content.extend(section_content)
                structured_content.append("")  # Linha em branco para separar seções
        
        # Se não encontrou estrutura de títulos, tenta método alternativo
        if not structured_content:
            # Procura por parágrafos e listas diretamente
            paragraphs = soup.find_all('p')
            lists = soup.find_all(['ul', 'ol'])
            
            for p in paragraphs:
                text = p.get_text().strip()
                if text and len(text) > 20 and not self._is_navigation_text(text):
                    structured_content.append(text)
            
            for ul in lists:
                list_items = ul.find_all('li')
                if list_items:
                    # Procura por texto anterior que possa ser cabeçalho
                    prev_text = ""
                    prev_element = ul.find_previous_sibling(['p', 'div', 'strong'])
                    if prev_element:
                        prev_text = prev_element.get_text().strip()
                        if any(keyword in prev_text.lower() for keyword in ['discentes', 'integrantes', 'membros', 'compõem']):
                            structured_content.append(prev_text)
                    
                    for li in list_items:
                        li_text = li.get_text().strip()
                        if li_text and len(li_text) > 5:
                            structured_content.append(f"• {li_text}")
        
        return "\n".join(structured_content)
    
    def _contains_names_list(self, text: str) -> bool:
        """Verifica se o texto contém uma lista de nomes próprios."""
        # Procura por padrões de nomes (Nome Sobrenome Sobrenome)
        name_pattern = r'[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][a-záàâãéêíóôõúç]+\s+[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][a-záàâãéêíóôõúç]+(?:\s+[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][a-záàâãéêíóôõúç]+)*'
        names_found = re.findall(name_pattern, text)
        
        # Se encontrou 3 ou mais nomes, provavelmente é uma lista de nomes
        return len(names_found) >= 3
    
    def _format_names_list(self, text: str) -> List[str]:
        """Formata uma lista de nomes encontrada no texto."""
        # Procura por padrões de nomes
        name_pattern = r'[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][a-záàâãéêíóôõúç]+(?:\s+[a-záàâãéêíóôõúç]+)*(?:\s+[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][a-záàâãéêíóôõúç]+)+'
        names_found = re.findall(name_pattern, text)
        
        formatted_names = []
        for name in names_found:
            name = name.strip()
            if len(name) > 10:  # Nomes completos são geralmente longos
                formatted_names.append(f"• {name}")
        
        return formatted_names
    
    def _extract_campus_from_url(self, url: str) -> str:
        """Extrai o nome do campus da URL do IFPE."""
        # Padrão: portal.ifpe.edu.br/CAMPUS/...
        parts = url.split('/')
        for i, part in enumerate(parts):
            if 'ifpe.edu.br' in part and i + 1 < len(parts):
                return parts[i + 1]
        return 'desconhecido'
    
    def _extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict:
        """Extrai metadados importantes da página."""
        metadata = {
            'title': '',
            'description': '',
            'keywords': [],
            'author': '',
            'language': 'pt'
        }
        
        # Título da página
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.get_text().strip()
        else:
            # Fallback para h1
            h1_tag = soup.find('h1')
            metadata['title'] = h1_tag.get_text().strip() if h1_tag else urlparse(url).netloc
        
        # Meta description
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        if desc_tag:
            metadata['description'] = desc_tag.get('content', '').strip()
        
        # Meta keywords
        keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
        if keywords_tag:
            keywords = keywords_tag.get('content', '').strip()
            metadata['keywords'] = [k.strip() for k in keywords.split(',') if k.strip()]
        
        # Autor
        author_tag = soup.find('meta', attrs={'name': 'author'})
        if author_tag:
            metadata['author'] = author_tag.get('content', '').strip()
        
        # Idioma
        lang_attr = soup.get('lang') or soup.find('html', attrs={'lang': True})
        if lang_attr:
            metadata['language'] = lang_attr if isinstance(lang_attr, str) else lang_attr.get('lang', 'pt')
        
        return metadata
    
    def _remove_noise_elements(self, soup: BeautifulSoup):
        """Remove elementos irrelevantes da página."""
        # Remove tags de ruído
        for tag_name in self.noise_tags:
            if tag_name.startswith('.'):
                # É uma classe CSS
                elements = soup.find_all(class_=tag_name[1:])
            elif tag_name.startswith('#'):
                # É um ID
                elements = soup.find_all(id=tag_name[1:])
            else:
                # É uma tag HTML
                elements = soup.find_all(tag_name)
            
            for element in elements:
                element.decompose()
        
        # Remove elementos com atributos específicos
        noise_attributes = [
            {'style': re.compile(r'display:\s*none', re.I)},
            {'class': re.compile(r'hidden|invisible|sr-only', re.I)},
            {'aria-hidden': 'true'}
        ]
        
        for attrs in noise_attributes:
            for element in soup.find_all(attrs=attrs):
                element.decompose()
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extrai o conteúdo principal usando seletores inteligentes melhorados."""
        main_content = ""
        
        # Primeiro, tenta seletores específicos para sites educacionais
        for selector in self.educational_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                main_content = content_element.get_text()
                if len(main_content.strip()) > 200:
                    break
        
        # Se não encontrou, tenta seletores gerais
        if not main_content.strip():
            for selector in self.content_selectors:
                content_element = soup.select_one(selector)
                if content_element:
                    main_content = content_element.get_text()
                    if len(main_content.strip()) > 200:
                        break
        
        # Se ainda não encontrou conteúdo principal, usa análise de densidade de texto
        if not main_content.strip():
            main_content = self._extract_by_text_density(soup)
        
        # Fallback final: procura por divs com mais texto
        if not main_content.strip():
            text_blocks = []
            
            # Analisa divs, articles, sections
            for tag_name in ['div', 'article', 'section', 'p']:
                elements = soup.find_all(tag_name)
                for element in elements:
                    text = element.get_text().strip()
                    if len(text) > 200:  # Apenas blocos com conteúdo substancial
                        text_blocks.append((len(text), text))
            
            # Ordena por tamanho e pega o maior
            if text_blocks:
                text_blocks.sort(key=lambda x: x[0], reverse=True)
                main_content = text_blocks[0][1]
            else:
                # Fallback: todo o texto da página
                main_content = soup.get_text()
        
        return main_content
    
    def _extract_by_text_density(self, soup: BeautifulSoup) -> str:
        """Extrai conteúdo baseado na densidade de texto por elemento."""
        best_element = None
        best_score = 0
        
        # Analisa elementos que podem conter conteúdo principal
        for element in soup.find_all(['div', 'article', 'section', 'main']):
            # Calcula densidade de texto vs tags
            text = element.get_text().strip()
            if len(text) < 200:
                continue
                
            # Conta tags filhas
            child_tags = len(element.find_all())
            
            # Calcula score: mais texto, menos tags = melhor
            if child_tags > 0:
                density_score = len(text) / child_tags
            else:
                density_score = len(text)
            
            # Bônus para elementos com palavras-chave relevantes
            text_lower = text.lower()
            keyword_bonus = 0
            educational_keywords = [
                'campus', 'instituto', 'ifpe', 'curso', 'educação', 'ensino',
                'estudante', 'professor', 'aula', 'disciplina', 'história',
                'localização', 'endereço', 'contato'
            ]
            
            for keyword in educational_keywords:
                if keyword in text_lower:
                    keyword_bonus += 100
            
            final_score = density_score + keyword_bonus
            
            if final_score > best_score:
                best_score = final_score
                best_element = element
        
        return best_element.get_text() if best_element else ""
    
    def _advanced_text_cleaning(self, text: str) -> str:
        """Limpeza avançada de texto extraído com foco em conteúdo educacional."""
        if not text:
            return ""
        
        # Remove caracteres de controle e unicode problemáticos
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', text)
        
        # Normaliza espaços em branco mas preserva estrutura
        text = re.sub(r'\t+', ' ', text)  # Tabs para espaços
        text = re.sub(r' +', ' ', text)   # Múltiplos espaços
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Múltiplas quebras
        
        # Remove padrões específicos de ruído
        noise_patterns = [
            r'^\s*cookies?\s*.*?política.*?\n',  # Avisos de cookies
            r'^\s*javascript.*?habilitado.*?\n', # Avisos de JS
            r'^\s*pular\s+para.*?\n',           # Links de acessibilidade
            r'^\s*início\s*>\s*.*?\n',          # Breadcrumbs simples
            r'^\s*home\s*>\s*.*?\n',            # Breadcrumbs em inglês
        ]
        
        for pattern in noise_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)
        
        # Processa linha por linha para melhor limpeza
        lines = text.split('\n')
        cleaned_lines = []
        seen_lines = set()
        
        for line in lines:
            line = line.strip()
            
            # Ignora linhas muito curtas ou vazias
            if len(line) < 15:
                continue
            
            # Ignora linhas repetidas (case insensitive)
            line_lower = line.lower()
            if line_lower in seen_lines:
                continue
            
            # Ignora linhas que são claramente navegação/menu
            if self._is_navigation_text(line):
                continue
            
            # Ignora linhas que são apenas números ou símbolos
            if re.match(r'^[\d\s\-\.\|\/\\]+$', line):
                continue
            
            # Adiciona linha válida
            cleaned_lines.append(line)
            seen_lines.add(line_lower)
        
        # Reconstrói o texto preservando parágrafos
        result = self._reconstruct_paragraphs(cleaned_lines)
        
        # Limpeza final
        result = re.sub(r'\s+$', '', result, flags=re.MULTILINE)
        result = result.strip()
        
        return result
    
    def _reconstruct_paragraphs(self, lines: List[str]) -> str:
        """Reconstrói parágrafos de forma inteligente."""
        if not lines:
            return ""
        
        paragraphs = []
        current_paragraph = []
        
        for line in lines:
            # Detecta início de novo parágrafo
            is_new_paragraph = (
                # Linha começa com maiúscula e tem estrutura de título/cabeçalho
                (re.match(r'^[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ]', line) and len(line) < 100) or
                # Linha anterior terminou com ponto final
                (current_paragraph and current_paragraph[-1].endswith('.')) or
                # Linha muito diferente da anterior (possível mudança de tópico)
                (current_paragraph and self._is_topic_change(current_paragraph[-1], line))
            )
            
            if is_new_paragraph and current_paragraph:
                paragraphs.append(' '.join(current_paragraph))
                current_paragraph = []
            
            current_paragraph.append(line)
        
        # Adiciona último parágrafo
        if current_paragraph:
            paragraphs.append(' '.join(current_paragraph))
        
        return '\n\n'.join(paragraphs)
    
    def _is_topic_change(self, prev_line: str, current_line: str) -> bool:
        """Detecta mudança de tópico entre linhas."""
        # Se a linha atual parece ser um título/cabeçalho
        if (len(current_line) < 80 and 
            (current_line.isupper() or 
             re.match(r'^[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][^a-z]*$', current_line))):
            return True
        
        # Se há uma diferença significativa no estilo de escrita
        prev_words = set(prev_line.lower().split())
        current_words = set(current_line.lower().split())
        
        if len(prev_words) > 3 and len(current_words) > 3:
            intersection = len(prev_words.intersection(current_words))
            if intersection / min(len(prev_words), len(current_words)) < 0.2:
                return True
        
        return False
    
    def _is_navigation_text(self, text: str) -> bool:
        """Identifica se o texto parece ser navegação ou menu com maior precisão."""
        nav_patterns = [
            r'^(home|início|menu|navegação|voltar|próximo|anterior|topo)$',
            r'^(login|entrar|sair|cadastro|registrar|acessar)$',
            r'^(compartilhar|curtir|seguir|inscrever|like|share)$',
            r'^\d+\s*(comentários?|views?|visualizações?|curtidas?)$',
            r'^(clique|acesse|veja|leia)\s+(aqui|mais|também)$',
            r'^(última\s+atualização|publicado|postado)\s+em\s+\d',
            r'^(copyright|©|\(c\))\s+\d{4}',
            r'^página\s+\d+\s+(de\s+\d+)?$',
            r'^(imprimir|print|salvar|save|download)$'
        ]
        
        text_lower = text.lower().strip()
        
        # Verifica padrões específicos
        for pattern in nav_patterns:
            if re.match(pattern, text_lower, re.I):
                return True
        
        # Texto muito curto com apenas palavras de navegação
        if len(text_lower) < 30 and len(text_lower.split()) <= 4:
            nav_words = {
                'home', 'menu', 'sobre', 'contato', 'serviços', 'produtos',
                'notícias', 'eventos', 'galeria', 'links', 'sitemap',
                'início', 'voltar', 'avançar', 'próximo', 'anterior',
                'topo', 'rodapé', 'busca', 'pesquisar', 'encontrar'
            }
            words = set(text_lower.split())
            if len(words.intersection(nav_words)) >= len(words) * 0.7:
                return True
        
        # Texto que parece breadcrumb
        if re.match(r'^.+\s*>\s*.+(\s*>\s*.+)*$', text_lower):
            return True
        
        # Texto com muitos símbolos de navegação
        nav_symbols = ['>', '|', '/', '\\', '»', '«', '›', '‹']
        symbol_count = sum(text.count(symbol) for symbol in nav_symbols)
        if symbol_count >= len(text) * 0.1:  # 10% ou mais são símbolos de navegação
            return True
        
        return False
    def _create_intelligent_chunks(self, text: str, metadata: Dict, url: str, chunk_size: int) -> List[Dict]:
        """
        Cria chunks inteligentes baseados em estrutura semântica e temática.
        """
        chunks = []
        
        # Primeiro, detecta a estrutura do texto
        structured_content = self._analyze_text_structure(text)
        
        # Se conseguiu identificar seções, cria chunks por seção
        if structured_content.get('sections'):
            chunks = self._create_section_based_chunks(
                structured_content, metadata, url, chunk_size
            )
        else:
            # Fallback: chunks por parágrafos como antes
            chunks = self._create_paragraph_based_chunks(
                text, metadata, url, chunk_size
            )
        
        # Pós-processamento para garantir qualidade
        chunks = self._post_process_chunks(chunks)
        
        return chunks
    
    def _analyze_text_structure(self, text: str) -> Dict:
        """Analisa a estrutura do texto para identificar seções e tópicos."""
        lines = text.split('\n')
        
        structure = {
            'title': '',
            'sections': [],
            'paragraphs': []
        }
        
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detecta possíveis títulos/cabeçalhos
            is_header = self._is_likely_header(line)
            
            if is_header:
                # Salva seção anterior se existir
                if current_section and current_content:
                    current_section['content'] = '\n'.join(current_content)
                    structure['sections'].append(current_section)
                
                # Inicia nova seção
                current_section = {
                    'title': line,
                    'content': '',
                    'type': self._classify_section_type(line)
                }
                current_content = []
            else:
                # Adiciona à seção atual
                current_content.append(line)
        
        # Adiciona última seção
        if current_section and current_content:
            current_section['content'] = '\n'.join(current_content)
            structure['sections'].append(current_section)
        
        # Se não encontrou seções, trata como parágrafos
        if not structure['sections']:
            structure['paragraphs'] = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        return structure
    
    def _is_likely_header(self, line: str) -> bool:
        """Determina se uma linha é provavelmente um cabeçalho."""
        # Muito curta para ser cabeçalho
        if len(line) < 10 or len(line) > 150:
            return False
        
        # Padrões de cabeçalho
        header_patterns = [
            r'^[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][^a-z]*$',  # Tudo maiúsculo
            r'^\d+[\.\)]\s+[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ]',  # Numerado
            r'^[IVX]+[\.\)]\s+[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ]',  # Romano
            r'^[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][a-záàâãéêíóôõúç\s]+:$',  # Termina com dois pontos
        ]
        
        for pattern in header_patterns:
            if re.match(pattern, line):
                return True
        
        # Heurísticas adicionais
        words = line.split()
        
        # Começa com palavra importante
        important_starters = [
            'história', 'localização', 'endereço', 'contato', 'sobre',
            'campus', 'instituto', 'cursos', 'ensino', 'educação',
            'fundação', 'criação', 'início', 'origem'
        ]
        
        if any(line.lower().startswith(starter) for starter in important_starters):
            return True
        
        # Linha com poucas palavras mas capitalizadas
        if len(words) <= 6 and all(word[0].isupper() for word in words if word):
            return True
        
        return False
    
    def _classify_section_type(self, title: str) -> str:
        """Classifica o tipo de seção baseado no título."""
        title_lower = title.lower()
        
        type_keywords = {
            'pet_programa': ['pet', 'programa de educação tutorial', 'programa educação tutorial'],
            'pet_integrantes': ['integrantes', 'membros', 'discentes', 'participantes', 'bolsistas', 'equipe'],
            'pet_tutores': ['tutor', 'tutora', 'professor', 'coordenador', 'orientador'],
            'pet_objetivos': ['objetivos', 'metas', 'finalidade', 'propósito'],
            'pet_atividades': ['atividades', 'projetos', 'ações', 'trabalhos'],
            'história': ['história', 'origem', 'fundação', 'criação', 'início'],
            'localização': ['localização', 'endereço', 'onde', 'local', 'situado', 'fica'],
            'contato': ['contato', 'telefone', 'email', 'falar', 'comunicação'],
            'cursos': ['curso', 'disciplina', 'formação', 'graduação', 'técnico'],
            'serviços': ['serviço', 'atendimento', 'biblioteca', 'laboratório'],
            'eventos': ['evento', 'atividade', 'programação', 'agenda'],
            'administrativo': ['direção', 'coordenação', 'administração', 'gestão']
        }
        
        for section_type, keywords in type_keywords.items():
            if any(keyword in title_lower for keyword in keywords):
                return section_type
        
        return 'geral'
    
    def _create_section_based_chunks(self, structure: Dict, metadata: Dict, url: str, chunk_size: int) -> List[Dict]:
        """Cria chunks baseados nas seções identificadas."""
        chunks = []
        
        for section in structure['sections']:
            section_text = f"{section['title']}\n\n{section['content']}"
            
            # Para conteúdo do PET, aumenta tolerância para manter contexto
            tolerance_multiplier = 2.0 if 'pet' in section_text.lower() else 1.5
            
            # Se a seção é pequena o suficiente, vira um chunk
            if len(section_text) <= chunk_size * tolerance_multiplier:
                chunk_data = self._create_enhanced_chunk_data(
                    section_text, metadata, url, len(chunks), section['type'], section['title']
                )
                chunks.append(chunk_data)
            else:
                # Divide a seção em sub-chunks maiores para PET
                adjusted_chunk_size = int(chunk_size * 1.5) if 'pet' in section_text.lower() else chunk_size
                sub_chunks = self._split_large_section(
                    section, metadata, url, adjusted_chunk_size, len(chunks)
                )
                chunks.extend(sub_chunks)
        
        return chunks
    
    def _split_large_section(self, section: Dict, metadata: Dict, url: str, chunk_size: int, start_index: int) -> List[Dict]:
        """Divide uma seção grande em sub-chunks mantendo coesão."""
        chunks = []
        content = section['content']
        title = section['title']
        section_type = section['type']
        
        # Divide por parágrafos primeiro
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        current_chunk = [title]  # Sempre inclui o título
        current_size = len(title)
        
        for paragraph in paragraphs:
            para_size = len(paragraph)
            
            # Se adicionar este parágrafo ultrapassaria o limite
            if current_size + para_size > chunk_size and len(current_chunk) > 1:
                # Finaliza chunk atual
                chunk_text = '\n\n'.join(current_chunk)
                chunk_data = self._create_enhanced_chunk_data(
                    chunk_text, metadata, url, start_index + len(chunks), 
                    section_type, title
                )
                chunks.append(chunk_data)
                
                # Inicia novo chunk com título e parágrafo atual
                current_chunk = [title, paragraph]
                current_size = len(title) + para_size
            else:
                # Adiciona ao chunk atual
                current_chunk.append(paragraph)
                current_size += para_size
        
        # Adiciona último chunk se houver conteúdo
        if len(current_chunk) > 1:  # Mais que só o título
            chunk_text = '\n\n'.join(current_chunk)
            chunk_data = self._create_enhanced_chunk_data(
                chunk_text, metadata, url, start_index + len(chunks),
                section_type, title
            )
            chunks.append(chunk_data)
        
        return chunks
    
    def _create_paragraph_based_chunks(self, text: str, metadata: Dict, url: str, chunk_size: int) -> List[Dict]:
        """Fallback: cria chunks baseados em parágrafos."""
        chunks = []
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        if not paragraphs:
            return chunks
        
        current_chunk = []
        current_size = 0
        
        for paragraph in paragraphs:
            para_size = len(paragraph)
            
            if current_size + para_size > chunk_size and current_chunk:
                chunk_text = '\n\n'.join(current_chunk)
                chunk_data = self._create_enhanced_chunk_data(
                    chunk_text, metadata, url, len(chunks), 'geral', ''
                )
                chunks.append(chunk_data)
                current_chunk = []
                current_size = 0
            
            current_chunk.append(paragraph)
            current_size += para_size
        
        if current_chunk:
            chunk_text = '\n\n'.join(current_chunk)
            chunk_data = self._create_enhanced_chunk_data(
                chunk_text, metadata, url, len(chunks), 'geral', ''
            )
            chunks.append(chunk_data)
        
        return chunks
    
    def _create_enhanced_chunk_data(self, text: str, metadata: Dict, url: str, chunk_index: int, content_type: str, section_title: str) -> Dict:
        """Cria objeto de dados do chunk com metadados enriquecidos e melhorados."""
        # Extrai palavras-chave específicas do chunk
        chunk_keywords = self._extract_intelligent_keywords(text)
        
        # Calcula métricas do texto
        sentences = self._split_into_sentences(text)
        words = text.split()
        
        # Extrai informações específicas baseadas no tipo de conteúdo
        specific_info = self._extract_specific_information(text, content_type)
        
        # Cria resumo do chunk
        chunk_summary = self._create_chunk_summary(text, section_title)
        
        return {
            "text": text,
            "title": metadata['title'],
            "url": url,
            "chunk_index": chunk_index,
            "keywords": chunk_keywords,
            "content_type": content_type,
            "section_title": section_title,
            "sentence_count": len(sentences),
            "word_count": len(words),
            "char_count": len(text),
            "language": metadata.get('language', 'pt'),
            "source": f"Web: {metadata['title']}",
            "summary": chunk_summary,
            "specific_info": specific_info,
            "metadata": {
                "url": url,
                "title": metadata['title'],
                "description": metadata.get('description', ''),
                "author": metadata.get('author', ''),
                "chunk_index": chunk_index,
                "content_type": content_type,
                "section_title": section_title,
                "quality_score": self._calculate_chunk_quality(text)
            }
        }
    
    def _extract_specific_information(self, text: str, content_type: str) -> Dict:
        """Extrai informações específicas baseadas no tipo de conteúdo."""
        info = {}
        text_lower = text.lower()
        
        if content_type == 'localização':
            # Extrai endereços e informações de localização
            address_patterns = [
                r'endereço[:\s]+([^\n\.]+)',
                r'localiza[ds]o?\s+(?:em|na|no)\s+([^\n\.]+)',
                r'situado\s+(?:em|na|no)\s+([^\n\.]+)',
                r'fica\s+(?:em|na|no)\s+([^\n\.]+)'
            ]
            
            for pattern in address_patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                if matches:
                    info['endereço'] = matches[0].strip()
                    break
        
        elif content_type == 'contato':
            # Extrai informações de contato
            phone_pattern = r'(?:telefone|fone|tel)[:\s]*(\(?[\d\s\-\(\)]+)'
            email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
            
            phones = re.findall(phone_pattern, text, re.IGNORECASE)
            emails = re.findall(email_pattern, text)
            
            if phones:
                info['telefone'] = phones[0].strip()
            if emails:
                info['email'] = emails[0]
        
        elif content_type == 'história':
            # Extrai datas importantes
            date_patterns = [
                r'(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})',
                r'(\d{4})',
                r'(início\s+das?\s+atividades?\s+[^\n\.]+)'
            ]
            
            for pattern in date_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    info['data_importante'] = matches[0]
                    break
        
        elif content_type == 'acadêmico':
            # Extrai cursos mencionados
            course_patterns = [
                r'cursos?\s+(?:técnicos?\s+)?(?:subsequentes?\s+)?(?:em\s+)?([^\n\.,]+)',
                r'formação\s+em\s+([^\n\.,]+)',
                r'graduação\s+em\s+([^\n\.,]+)'
            ]
            
            courses = []
            for pattern in course_patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                courses.extend(matches)
            
            if courses:
                info['cursos'] = list(set(courses))  # Remove duplicatas
        
        return info
    
    def _create_chunk_summary(self, text: str, section_title: str) -> str:
        """Cria um resumo conciso do chunk."""
        if section_title:
            return f"{section_title}: {text[:100]}..."
        
        # Pega as primeiras sentenças mais informativas
        sentences = self._split_into_sentences(text)
        if not sentences:
            return text[:100] + "..." if len(text) > 100 else text
        
        # Prioriza sentenças com informações importantes
        important_sentence = None
        for sentence in sentences[:3]:  # Analisa só as primeiras 3
            if any(word in sentence.lower() for word in [
                'localizado', 'situado', 'endereço', 'campus', 'instituto',
                'oferece', 'curso', 'fundado', 'criado', 'início'
            ]):
                important_sentence = sentence
                break
        
        if important_sentence:
            return important_sentence[:150] + "..." if len(important_sentence) > 150 else important_sentence
        
        # Fallback: primeira sentença
        return sentences[0][:150] + "..." if len(sentences[0]) > 150 else sentences[0]
    
    def _calculate_chunk_quality(self, text: str) -> float:
        """Calcula um score de qualidade para o chunk."""
        score = 0.5  # Base
        
        # Bônus por tamanho adequado
        length = len(text)
        if 200 <= length <= 1000:
            score += 0.3
        elif length < 100:
            score -= 0.2
        
        # Bônus por estrutura (pontuação adequada)
        sentences = text.count('.') + text.count('!') + text.count('?')
        words = len(text.split())
        if words > 0:
            sentence_ratio = sentences / words * 100
            if 2 <= sentence_ratio <= 8:
                score += 0.2
        
        # Bônus por palavras-chave educacionais relevantes
        educational_keywords = [
            'campus', 'instituto', 'ifpe', 'curso', 'educação', 'ensino',
            'estudante', 'professor', 'localização', 'endereço', 'história'
        ]
        
        text_lower = text.lower()
        keyword_count = sum(1 for keyword in educational_keywords if keyword in text_lower)
        if keyword_count >= 2:
            score += 0.2
        
        return round(min(1.0, max(0.1, score)), 2)
    
    def _post_process_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """Pós-processa chunks para garantir qualidade e consistência."""
        if not chunks:
            return chunks
        
        processed_chunks = []
        
        for chunk in chunks:
            # Remove chunks muito pequenos ou de baixa qualidade (threshold reduzido)
            if (len(chunk['text']) < 50 or 
                chunk['metadata']['quality_score'] < 0.1):
                continue
            
            # Melhora o texto do chunk
            chunk['text'] = self._improve_chunk_text(chunk['text'])
            
            processed_chunks.append(chunk)
        
        return processed_chunks
    
    def _improve_chunk_text(self, text: str) -> str:
        """Melhora o texto do chunk para maior clareza."""
        # Remove espaços extras no início/fim
        text = text.strip()
        
        # Garante que parágrafos sejam bem separados
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Remove linhas que são só pontuação
        lines = text.split('\n')
        clean_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not re.match(r'^[^\w]*$', line):
                clean_lines.append(line)
        
        return '\n'.join(clean_lines)
    
    def _identify_content_type(self, text: str) -> str:
        """Identifica o tipo de conteúdo do chunk."""
        text_lower = text.lower()
        
        # Padrões para diferentes tipos de conteúdo
        if any(word in text_lower for word in ['curso', 'disciplina', 'matrícula', 'professor', 'aula']):
            return 'acadêmico'
        elif any(word in text_lower for word in ['campus', 'endereço', 'localização', 'como chegar']):
            return 'localização'
        elif any(word in text_lower for word in ['contato', 'telefone', 'email', 'falar']):
            return 'contato'
        elif any(word in text_lower for word in ['evento', 'data', 'prazo', 'cronograma']):
            return 'eventos'
        elif any(word in text_lower for word in ['biblioteca', 'laboratório', 'restaurante', 'serviço']):
            return 'serviços'
        else:
            return 'geral'
    
    def _extract_intelligent_keywords(self, text: str) -> List[str]:
        """
        Extrai palavras-chave de forma inteligente usando análise de frequência e relevância.
        """
        if not text:
            return []
        
        # Stop words expandida
        stop_words = {
            'a', 'o', 'e', 'é', 'da', 'do', 'de', 'para', 'com', 'em', 'no', 'na', 'um', 'uma',
            'por', 'se', 'que', 'como', 'mais', 'ou', 'ao', 'aos', 'as', 'os', 'à', 'às',
            'ele', 'ela', 'eles', 'elas', 'seu', 'sua', 'seus', 'suas', 'este', 'esta',
            'isso', 'aqui', 'assim', 'então', 'quando', 'onde', 'porque', 'mas', 'também',
            'já', 'ainda', 'só', 'até', 'sobre', 'entre', 'sem', 'pelo', 'pela', 'pode',
            'ter', 'tem', 'foi', 'ser', 'está', 'são', 'muito', 'bem', 'fazer', 'todo',
            'toda', 'todos', 'todas', 'cada', 'outro', 'outra', 'outros', 'outras'
        }
        
        # Limpa e normaliza o texto
        clean_text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = clean_text.split()
        
        # Filtra palavras significativas
        significant_words = []
        for word in words:
            if (len(word) >= 3 and 
                word not in stop_words and 
                not word.isdigit() and
                not re.match(r'^[a-z]{1,2}$', word)):  # Remove siglas de 1-2 letras
                significant_words.append(word)
        
        # Conta frequências
        word_freq = Counter(significant_words)
        
        # Pontuação baseada em frequência e características
        scored_words = []
        for word, freq in word_freq.items():
            score = freq
            
            # Aumenta pontuação para palavras técnicas/institucionais
            if any(term in word for term in ['ifpe', 'campus', 'curso', 'professor', 'estudante']):
                score *= 2
            
            # Aumenta pontuação para palavras maiores (mais específicas)
            if len(word) > 6:
                score *= 1.3
            
            # Diminui pontuação para palavras muito comuns
            if freq > len(significant_words) * 0.1:  # Aparece em mais de 10% do texto
                score *= 0.7
            
            scored_words.append((word, score))
        
        # Ordena e retorna as melhores palavras-chave
        scored_words.sort(key=lambda x: x[1], reverse=True)
        return [word for word, score in scored_words[:8]]  # Top 8 palavras-chave
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Divide texto em sentenças de forma inteligente."""
        # Padrão para identificar final de sentença
        sentence_endings = r'[.!?]+\s+'
        sentences = re.split(sentence_endings, text)
        
        # Limpa e filtra sentenças
        clean_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20:  # Apenas sentenças com conteúdo substancial
                clean_sentences.append(sentence)
        
        return clean_sentences
    
    def _identify_content_type(self, text: str) -> str:
        """Identifica o tipo de conteúdo do chunk."""
        text_lower = text.lower()
        
        # Padrões para diferentes tipos de conteúdo
        if any(word in text_lower for word in ['curso', 'disciplina', 'matrícula', 'professor', 'aula']):
            return 'acadêmico'
        elif any(word in text_lower for word in ['campus', 'endereço', 'localização', 'como chegar']):
            return 'localização'
        elif any(word in text_lower for word in ['contato', 'telefone', 'email', 'falar']):
            return 'contato'
        elif any(word in text_lower for word in ['evento', 'data', 'prazo', 'cronograma']):
            return 'eventos'
        elif any(word in text_lower for word in ['biblioteca', 'laboratório', 'restaurante', 'serviço']):
            return 'serviços'
        else:
            return 'geral'
    
    def _clean_text(self, text: str) -> str:
        """
        Método legado mantido para compatibilidade - usa o novo método de limpeza.
        """
        return self._advanced_text_cleaning(text)
    
    def scrape_sitemap_chunked(self, base_url: str, max_pages: int = 10) -> List[Dict]:
        """
        Simples fallback para múltiplas páginas - apenas scrape da URL principal.
        """
        print(f"Scraping de sitemap para: {base_url}")
        return [self.scrape_url_chunked(base_url)]