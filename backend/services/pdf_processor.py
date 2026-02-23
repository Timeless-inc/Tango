import os
import io
from typing import List, Dict
from PyPDF2 import PdfReader
import re
from collections import Counter

class PDFProcessorService:
    def __init__(self):
        self.chunk_size = 1200  # Tamanho otimizado para chunks mais informativos
        
    def process_pdf(self, file_content: bytes, filename: str, chunk_size: int = None) -> List[Dict]:
        """
        Processa um arquivo PDF com análise estrutural avançada e chunking inteligente melhorado.
        """
        try:
            # Define o tamanho do chunk
            if chunk_size is None:
                chunk_size = self.chunk_size
                
            print(f"Processando PDF: {filename}")
            
            # Lê o PDF
            pdf_reader = PdfReader(io.BytesIO(file_content))
            
            # Extrai metadados do PDF
            metadata = self._extract_pdf_metadata(pdf_reader, filename)
            print(f"Metadados extraídos: {metadata['title']}")
            
            # Extrai texto estruturado de todas as páginas com melhor análise
            structured_content = self._extract_enhanced_structured_content(pdf_reader)
            print(f"Texto estruturado extraído de {len(structured_content)} páginas")
            
            if not structured_content:
                return []
            
            # Processa e limpa o conteúdo com técnicas avançadas
            processed_content = self._advanced_content_processing(structured_content)
            
            # Cria chunks inteligentes baseados na estrutura do documento
            chunks = self._create_enhanced_structured_chunks(
                processed_content, metadata, filename, chunk_size
            )
            
            print(f"Criados {len(chunks)} chunks estruturados de alta qualidade")
            return chunks
            
        except Exception as e:
            print(f"Erro ao processar PDF {filename}: {str(e)}")
            raise Exception(f"Erro ao processar PDF: {str(e)}")
    
    def _extract_pdf_metadata(self, pdf_reader: PdfReader, filename: str) -> Dict:
        """Extrai metadados avançados do PDF."""
        metadata = {
            'title': '',
            'author': '',
            'subject': '',
            'creator': '',
            'total_pages': len(pdf_reader.pages),
            'filename': filename
        }
        
        # Tenta extrair metadados do PDF
        if pdf_reader.metadata:
            pdf_meta = pdf_reader.metadata
            metadata['title'] = pdf_meta.get('/Title', '').strip()
            metadata['author'] = pdf_meta.get('/Author', '').strip()
            metadata['subject'] = pdf_meta.get('/Subject', '').strip()
            metadata['creator'] = pdf_meta.get('/Creator', '').strip()
        
        # Se não tem título, tenta extrair da primeira página ou usar filename
        if not metadata['title']:
            try:
                first_page_text = pdf_reader.pages[0].extract_text()
                metadata['title'] = self._extract_title_from_text(first_page_text, filename)
            except:
                metadata['title'] = filename.replace('.pdf', '').replace('_', ' ').replace('-', ' ').title()
        
        return metadata
    
    def _extract_enhanced_structured_content(self, pdf_reader: PdfReader) -> List[Dict]:
        """Extrai conteúdo estruturado melhorado por página com análise avançada de layout."""
        pages_content = []
        
        for page_num, page in enumerate(pdf_reader.pages):
            try:
                # Extrai texto da página
                page_text = page.extract_text()
                
                if not page_text or len(page_text.strip()) < 50:
                    continue
                
                # Analisa a estrutura da página de forma mais inteligente
                page_structure = self._enhanced_page_analysis(page_text, page_num + 1)
                
                # Só adiciona se tem conteúdo significativo
                if page_structure and page_structure.get('meaningful_content'):
                    pages_content.append(page_structure)
                
            except Exception as e:
                print(f"Erro ao extrair texto da página {page_num + 1}: {str(e)}")
                continue
        
        return pages_content
    
    def _enhanced_page_analysis(self, page_text: str, page_num: int) -> Dict:
        """Análise avançada da estrutura de uma página específica."""
        # Remove caracteres problemáticos
        page_text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', page_text)
        
        lines = page_text.split('\n')
        
        # Classifica linhas por tipo com maior precisão
        headers = []
        paragraphs = []
        lists = []
        tables = []
        
        current_paragraph = []
        meaningful_content = False
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_paragraph:
                    paragraph_text = ' '.join(current_paragraph)
                    if len(paragraph_text) > 30:  # Só parágrafos com conteúdo substancial
                        paragraphs.append(paragraph_text)
                        meaningful_content = True
                    current_paragraph = []
                continue
            
            # Ignora cabeçalhos/rodapés de página
            if self._is_page_header_footer(line, page_num):
                continue
            
            # Detecta tabelas (múltiplas colunas separadas por espaços)
            if self._is_table_row(line):
                if current_paragraph:
                    paragraph_text = ' '.join(current_paragraph)
                    if len(paragraph_text) > 30:
                        paragraphs.append(paragraph_text)
                        meaningful_content = True
                    current_paragraph = []
                tables.append(line)
                meaningful_content = True
                continue
            
            # Detecta cabeçalhos com maior precisão
            if self._is_enhanced_header(line):
                if current_paragraph:
                    paragraph_text = ' '.join(current_paragraph)
                    if len(paragraph_text) > 30:
                        paragraphs.append(paragraph_text)
                        meaningful_content = True
                    current_paragraph = []
                headers.append(line)
                meaningful_content = True
                continue
            
            # Detecta itens de lista
            if re.match(r'^[\-\*\•]\s+|^\d+[\.\)]\s+|^[a-z][\.\)]\s+', line):
                if current_paragraph:
                    paragraph_text = ' '.join(current_paragraph)
                    if len(paragraph_text) > 30:
                        paragraphs.append(paragraph_text)
                        meaningful_content = True
                    current_paragraph = []
                lists.append(line)
                meaningful_content = True
                continue
            
            # Texto normal - adiciona ao parágrafo atual
            current_paragraph.append(line)
        
        # Adiciona último parágrafo se houver
        if current_paragraph:
            paragraph_text = ' '.join(current_paragraph)
            if len(paragraph_text) > 30:
                paragraphs.append(paragraph_text)
                meaningful_content = True
        
        return {
            'page_number': page_num,
            'headers': headers,
            'paragraphs': paragraphs,
            'lists': lists,
            'tables': tables,
            'raw_text': page_text,
            'meaningful_content': meaningful_content
        }
    
    def _is_page_header_footer(self, line: str, page_num: int) -> bool:
        """Identifica cabeçalhos e rodapés de página."""
        line_lower = line.lower()
        
        # Padrões comuns de cabeçalho/rodapé
        footer_patterns = [
            rf'página\s+{page_num}',
            rf'{page_num}\s*/\s*\d+',
            r'^\d+$',  # Só número da página
            r'^copyright|©|\(c\)',
            r'^\s*\d{1,2}\s*$'  # Só números pequenos
        ]
        
        for pattern in footer_patterns:
            if re.match(pattern, line_lower):
                return True
        
        # Linha muito curta que pode ser cabeçalho
        if len(line) < 20 and not any(char.isalpha() for char in line):
            return True
        
        return False
    
    def _is_table_row(self, line: str) -> bool:
        """Detecta se uma linha faz parte de uma tabela."""
        # Múltiplos espaços ou tabs podem indicar colunas
        if re.search(r'\s{3,}', line) and len(line.split()) >= 3:
            return True
        
        # Separadores de tabela comuns
        if re.search(r'[\|\t]', line) and len(line.split()) >= 2:
            return True
        
        return False
    
    def _is_enhanced_header(self, line: str) -> bool:
        """Detecta cabeçalhos com maior precisão."""
        # Muito longo para ser cabeçalho
        if len(line) > 200:
            return False
        
        # Muito curto e sem significado
        if len(line) < 8:
            return False
        
        # Padrões de cabeçalho melhorados
        header_patterns = [
            r'^[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][^a-z]*$',  # Tudo maiúsculo
            r'^\d+[\.\)]\s+[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ]',  # Numerado
            r'^[IVX]+[\.\)]\s+[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ]',  # Romano
            r'^[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][a-záàâãéêíóôõúç\s]+:$',  # Termina com dois pontos
            r'^CAPÍTULO|^SEÇÃO|^PARTE|^ANEXO',  # Palavras-chave
        ]
        
        for pattern in header_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                return True
        
        # Heurísticas adicionais
        words = line.split()
        
        # Linha com poucas palavras mas todas capitalizadas
        if (2 <= len(words) <= 8 and 
            all(word[0].isupper() for word in words if word and word[0].isalpha())):
            return True
        
        # Palavras-chave que indicam início de seção
        section_keywords = [
            'introdução', 'objetivo', 'metodologia', 'conclusão', 
            'resumo', 'abstract', 'referências', 'bibliografia',
            'histórico', 'localização', 'estrutura', 'organização'
        ]
        
        if any(keyword in line.lower() for keyword in section_keywords):
            return True
        
        return False
    
    def _extract_title_from_text(self, text: str, filename: str) -> str:
        """Extrai título do texto da primeira página."""
        lines = text.split('\n')[:15]  # Primeiras 15 linhas
        
        for line in lines:
            line = line.strip()
            # Busca linha que parece ser título (tamanho adequado, não só números)
            if (20 <= len(line) <= 120 and 
                not re.match(r'^[\d\s\-\.]+$', line) and
                not line.lower().startswith(('página', 'page', 'capítulo', 'chapter'))):
                
                # Remove caracteres especiais no início/fim
                title = re.sub(r'^[^\w]+|[^\w]+$', '', line)
                if title and len(title) > 10:
                    return title
        
        # Fallback: usa o nome do arquivo
        return filename.replace('.pdf', '').replace('_', ' ').replace('-', ' ').title()
    
    def _analyze_page_structure(self, page_text: str, page_num: int) -> Dict:
        """Analisa a estrutura de uma página específica."""
        # Identifica diferentes elementos estruturais
        lines = page_text.split('\n')
        
        # Classifica linhas por tipo
        headers = []
        paragraphs = []
        lists = []
        
        current_paragraph = []
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_paragraph:
                    paragraphs.append(' '.join(current_paragraph))
                    current_paragraph = []
                continue
            
            # Detecta cabeçalhos (linhas curtas, possivelmente em maiúscula ou com formatação especial)
            if (len(line) < 80 and 
                (line.isupper() or 
                 re.match(r'^\d+\.?\s+[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ]', line) or
                 re.match(r'^[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][^a-z]*$', line))):
                if current_paragraph:
                    paragraphs.append(' '.join(current_paragraph))
                    current_paragraph = []
                headers.append(line)
            
            # Detecta itens de lista
            elif re.match(r'^[\-\*\•]\s+|^\d+[\.\)]\s+|^[a-z][\.\)]\s+', line):
                if current_paragraph:
                    paragraphs.append(' '.join(current_paragraph))
                    current_paragraph = []
                lists.append(line)
            
            # Texto normal - adiciona ao parágrafo atual
            else:
                current_paragraph.append(line)
        
        # Adiciona último parágrafo se houver
        if current_paragraph:
            paragraphs.append(' '.join(current_paragraph))
        
        return {
            'page_number': page_num,
            'headers': headers,
            'paragraphs': paragraphs,
            'lists': lists,
            'raw_text': page_text
        }
    
    def _advanced_content_processing(self, pages_content: List[Dict]) -> Dict:
        """Processamento avançado e organização do conteúdo estruturado."""
        processed = {
            'title': '',
            'sections': [],
            'all_text': '',
            'total_pages': len(pages_content),
            'document_type': 'geral'
        }
        
        current_section = None
        all_headers = []
        
        # Primeiro, identifica o tipo de documento e extrai cabeçalhos globais
        for page in pages_content:
            all_headers.extend(page['headers'])
        
        # Classifica o tipo de documento
        processed['document_type'] = self._classify_document_type(all_headers, pages_content)
        
        # Processa cada página
        for page in pages_content:
            # Processa cabeçalhos como início de novas seções
            for header in page['headers']:
                # Finaliza seção anterior se existir
                if current_section and current_section.get('content'):
                    processed['sections'].append(current_section)
                
                # Inicia nova seção
                current_section = {
                    'title': header,
                    'content': [],
                    'page_start': page['page_number'],
                    'type': self._classify_section_type(header)
                }
            
            # Adiciona todo o conteúdo da página à seção atual
            content_parts = []
            
            # Adiciona parágrafos
            for para in page['paragraphs']:
                if len(para.strip()) > 20:  # Só conteúdo substancial
                    content_parts.append(para)
            
            # Adiciona listas
            for list_item in page['lists']:
                content_parts.append(list_item)
            
            # Adiciona tabelas
            for table_row in page.get('tables', []):
                content_parts.append(table_row)
            
            # Adiciona à seção atual ou cria seção genérica
            if current_section:
                current_section['content'].extend(content_parts)
            elif content_parts:  # Tem conteúdo mas não tem seção
                current_section = {
                    'title': f"Conteúdo - Página {page['page_number']}",
                    'content': content_parts,
                    'page_start': page['page_number'],
                    'type': 'geral'
                }
            
            # Adiciona ao texto completo com marcação de página
            if page.get('meaningful_content'):
                processed['all_text'] += f"\n\n[Página {page['page_number']}]\n{page['raw_text']}"
        
        # Adiciona última seção
        if current_section and current_section.get('content'):
            processed['sections'].append(current_section)
        
        # Pós-processa as seções para melhor qualidade
        processed['sections'] = self._post_process_sections(processed['sections'])
        
        return processed
    
    def _classify_document_type(self, headers: List[str], pages_content: List[Dict]) -> str:
        """Classifica o tipo de documento baseado nos cabeçalhos e conteúdo."""
        all_text = ' '.join([' '.join(page.get('paragraphs', [])) for page in pages_content]).lower()
        
        # Padrões para diferentes tipos de documento
        if any(keyword in all_text for keyword in ['regulamento', 'regimento', 'norma', 'resolução']):
            return 'regulamento'
        elif any(keyword in all_text for keyword in ['projeto pedagógico', 'ppc', 'matriz curricular']):
            return 'pedagogico'
        elif any(keyword in all_text for keyword in ['manual', 'guia', 'instruções']):
            return 'manual'
        elif any(keyword in all_text for keyword in ['relatório', 'atividades', 'gestão']):
            return 'relatorio'
        elif any(keyword in all_text for keyword in ['edital', 'processo seletivo', 'concurso']):
            return 'edital'
        else:
            return 'geral'
    
    def _classify_section_type(self, title: str) -> str:
        """Classifica o tipo de seção baseado no título."""
        title_lower = title.lower()
        
        type_keywords = {
            'introducao': ['introdução', 'apresentação', 'preâmbulo'],
            'objetivos': ['objetivo', 'finalidade', 'meta'],
            'estrutura': ['estrutura', 'organização', 'composição'],
            'funcionamento': ['funcionamento', 'operação', 'procedimento'],
            'requisitos': ['requisito', 'exigência', 'critério'],
            'avaliacao': ['avaliação', 'nota', 'conceito'],
            'referencias': ['referência', 'bibliografia', 'fonte'],
            'anexos': ['anexo', 'apêndice', 'complemento']
        }
        
        for section_type, keywords in type_keywords.items():
            if any(keyword in title_lower for keyword in keywords):
                return section_type
        
        return 'geral'
    
    def _post_process_sections(self, sections: List[Dict]) -> List[Dict]:
        """Pós-processa as seções para melhorar qualidade e remover redundâncias."""
        processed_sections = []
        
        for section in sections:
            # Remove seções muito pequenas ou vazias
            if not section.get('content') or len(' '.join(section['content'])) < 50:
                continue
            
            # Limpa e melhora o conteúdo da seção
            cleaned_content = []
            seen_content = set()
            
            for content in section['content']:
                content = content.strip()
                if len(content) < 20:  # Muito pequeno
                    continue
                
                # Remove duplicatas
                content_lower = content.lower()
                if content_lower in seen_content:
                    continue
                
                cleaned_content.append(content)
                seen_content.add(content_lower)
            
            if cleaned_content:
                section['content'] = cleaned_content
                processed_sections.append(section)
        
        return processed_sections
    
    def _create_enhanced_structured_chunks(self, content: Dict, metadata: Dict, filename: str, chunk_size: int) -> List[Dict]:
        """Cria chunks melhorados baseados na estrutura do documento."""
        chunks = []
        
        # Se tem seções estruturadas, processa cada uma
        if content['sections']:
            for section in content['sections']:
                section_chunks = self._process_section_into_chunks(
                    section, metadata, filename, chunk_size, len(chunks)
                )
                chunks.extend(section_chunks)
        
        # Fallback: se não há estrutura de seções, usa chunking inteligente
        else:
            text = content['all_text']
            if text.strip():
                simple_chunks = self._create_intelligent_text_chunks(text, chunk_size)
                
                for i, chunk_text in enumerate(simple_chunks):
                    chunk_data = self._create_enhanced_pdf_chunk_data(
                        chunk_text,
                        metadata['title'],
                        metadata,
                        filename,
                        i,
                        1,  # Página padrão
                        'geral',
                        content.get('document_type', 'geral')
                    )
                    chunks.append(chunk_data)
        
        # Filtra e melhora a qualidade dos chunks
        chunks = self._filter_and_improve_chunks(chunks)
        
        return chunks
    
    def _process_section_into_chunks(self, section: Dict, metadata: Dict, filename: str, chunk_size: int, start_index: int) -> List[Dict]:
        """Processa uma seção em chunks mantendo coerência temática."""
        chunks = []
        section_title = section['title']
        section_content = section['content']
        section_type = section.get('type', 'geral')
        page_start = section.get('page_start', 1)
        
        # Junta todo o conteúdo da seção
        full_section_text = '\n\n'.join(section_content)
        
        # Se a seção é pequena o suficiente, vira um chunk único
        if len(full_section_text) <= chunk_size * 1.2:  # 20% de tolerância
            chunk_data = self._create_enhanced_pdf_chunk_data(
                full_section_text,
                section_title,
                metadata,
                filename,
                start_index,
                page_start,
                section_type,
                metadata.get('document_type', 'geral')
            )
            chunks.append(chunk_data)
        
        # Se a seção é grande, divide mantendo contexto
        else:
            sub_chunks = self._intelligent_section_splitting(
                full_section_text, section_title, chunk_size
            )
            
            for i, sub_chunk in enumerate(sub_chunks):
                # Cria título informativo para sub-chunk
                if len(sub_chunks) > 1:
                    chunk_title = f"{section_title} (Parte {i+1}/{len(sub_chunks)})"
                else:
                    chunk_title = section_title
                
                chunk_data = self._create_enhanced_pdf_chunk_data(
                    sub_chunk,
                    chunk_title,
                    metadata,
                    filename,
                    start_index + len(chunks),
                    page_start,
                    section_type,
                    metadata.get('document_type', 'geral')
                )
                chunks.append(chunk_data)
        
        return chunks
    
    def _intelligent_section_splitting(self, text: str, section_title: str, chunk_size: int) -> List[str]:
        """Divide uma seção de forma inteligente mantendo coerência."""
        chunks = []
        
        # Primeiro, tenta dividir por sub-seções (parágrafos naturais)
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        current_chunk = []
        current_size = 0
        
        for paragraph in paragraphs:
            para_size = len(paragraph)
            
            # Se adicionar este parágrafo ultrapassaria muito o limite
            if current_size + para_size > chunk_size * 1.1 and current_chunk:
                # Finaliza chunk atual
                chunk_text = '\n\n'.join(current_chunk)
                chunks.append(chunk_text)
                current_chunk = []
                current_size = 0
            
            # Se o parágrafo individual é muito grande, divide por sentenças
            if para_size > chunk_size:
                # Primeiro adiciona o que já temos
                if current_chunk:
                    chunk_text = '\n\n'.join(current_chunk)
                    chunks.append(chunk_text)
                    current_chunk = []
                    current_size = 0
                
                # Divide o parágrafo grande
                large_para_chunks = self._split_large_paragraph(paragraph, chunk_size)
                chunks.extend(large_para_chunks)
            else:
                current_chunk.append(paragraph)
                current_size += para_size
        
        # Adiciona último chunk se houver conteúdo
        if current_chunk:
            chunk_text = '\n\n'.join(current_chunk)
            chunks.append(chunk_text)
        
        return chunks
    
    def _split_large_paragraph(self, paragraph: str, chunk_size: int) -> List[str]:
        """Divide um parágrafo muito grande por sentenças."""
        # Divide por sentenças
        sentences = re.split(r'[.!?]+\s+', paragraph)
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            sent_size = len(sentence)
            
            if current_size + sent_size > chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_size = 0
            
            current_chunk.append(sentence)
            current_size += sent_size
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def _create_intelligent_text_chunks(self, text: str, chunk_size: int) -> List[str]:
        """Cria chunks inteligentes de texto sem estrutura definida."""
        # Remove marcações de página para análise
        clean_text = re.sub(r'\[Página \d+\]\n', '', text)
        
        # Divide por parágrafos naturais
        paragraphs = [p.strip() for p in clean_text.split('\n\n') if p.strip() and len(p) > 30]
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        for paragraph in paragraphs:
            para_size = len(paragraph)
            
            if current_size + para_size > chunk_size and current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = []
                current_size = 0
            
            current_chunk.append(paragraph)
            current_size += para_size
        
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        return chunks
    
    def _split_large_section(self, text: str, chunk_size: int) -> List[str]:
        """Divide uma seção grande em chunks menores mantendo coerência."""
        chunks = []
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        current_chunk = []
        current_size = 0
        
        for paragraph in paragraphs:
            para_size = len(paragraph)
            
            # Se adicionar este parágrafo exceder o limite
            if current_size + para_size > chunk_size and current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = []
                current_size = 0
            
            current_chunk.append(paragraph)
            current_size += para_size
            
            # Se o parágrafo individual é muito grande, força quebra
            if para_size > chunk_size * 1.5:
                if len(current_chunk) > 1:
                    current_chunk.pop()
                    chunks.append('\n\n'.join(current_chunk))
                    current_chunk = []
                
                # Divide o parágrafo grande em sentenças
                sentences = self._split_into_sentences(paragraph)
                sentence_chunk = []
                sentence_size = 0
                
                for sentence in sentences:
                    sent_size = len(sentence)
                    if sentence_size + sent_size > chunk_size and sentence_chunk:
                        chunks.append(' '.join(sentence_chunk))
                        sentence_chunk = []
                        sentence_size = 0
                    
                    sentence_chunk.append(sentence)
                    sentence_size += sent_size
                
                if sentence_chunk:
                    current_chunk = [' '.join(sentence_chunk)]
                    current_size = sentence_size
                else:
                    current_chunk = []
                    current_size = 0
        
        # Adiciona último chunk
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Divide texto em sentenças."""
        sentences = re.split(r'[.!?]+\s+', text)
        return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
    
    def _create_simple_text_chunks(self, text: str, chunk_size: int) -> List[str]:
        """Cria chunks simples quando não há estrutura clara."""
        words = text.split()
        chunks = []
        current_chunk = []
        
        for word in words:
            current_chunk.append(word)
            if len(' '.join(current_chunk)) >= chunk_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def _create_pdf_chunk_data(self, text: str, title: str, metadata: Dict, filename: str, 
                              chunk_index: int, page_ref: int) -> Dict:
        """Cria dados estruturados do chunk de PDF."""
        # Limpa o texto
        clean_text = self._advanced_clean_text(text)
        
        # Extrai palavras-chave inteligentes
        keywords = self._extract_pdf_keywords(clean_text)
        
        # Identifica tipo de conteúdo
        content_type = self._identify_pdf_content_type(clean_text)
        
        return {
            "text": clean_text,
            "title": title,
            "filename": filename,
            "source": f"PDF: {metadata['title']}",
            "chunk_index": chunk_index,
            "page_reference": page_ref,
            "total_pages": metadata['total_pages'],
            "keywords": keywords,
            "content_type": content_type,
            "char_count": len(clean_text),
            "word_count": len(clean_text.split()),
            "url": f"file:///{filename}",
            "metadata": {
                "type": "pdf",
                "filename": filename,
                "title": metadata['title'],
                "author": metadata.get('author', ''),
                "page": page_ref,
                "total_pages": metadata['total_pages'],
                "chunk_index": chunk_index,
                "section_title": title,
                "content_type": content_type
            }
        }
    def _advanced_clean_text(self, text: str) -> str:
        """Limpeza avançada de texto extraído de PDF."""
        if not text:
            return ""
        
        # Remove caracteres de controle e problemas de encoding
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', text)
        
        # Corrige problemas comuns de extração de PDF
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # Palavras grudadas
        text = re.sub(r'(\d)([A-Za-z])', r'\1 \2', text)  # Números grudados com texto
        text = re.sub(r'([A-Za-z])(\d)', r'\1 \2', text)  # Texto grudado com números
        
        # Normaliza espaços e quebras de linha
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # Remove linhas muito curtas ou repetitivas
        lines = text.split('\n')
        cleaned_lines = []
        seen_lines = set()
        
        for line in lines:
            line = line.strip()
            
            # Ignora linhas muito curtas
            if len(line) < 10:
                continue
            
            # Ignora linhas repetidas
            line_lower = line.lower()
            if line_lower in seen_lines:
                continue
            
            # Ignora rodapés e cabeçalhos comuns
            if self._is_header_footer_line(line):
                continue
            
            cleaned_lines.append(line)
            seen_lines.add(line_lower)
        
        result = '\n'.join(cleaned_lines)
        return result.strip()
    
    def _is_header_footer_line(self, line: str) -> bool:
        """Identifica linhas que são cabeçalhos ou rodapés."""
        line_lower = line.lower().strip()
        
        # Padrões comuns de rodapé/cabeçalho
        patterns = [
            r'^página\s+\d+',
            r'^\d+\s*$',
            r'^page\s+\d+',
            r'^\d+\s+de\s+\d+',
            r'^www\.',
            r'@\w+\.\w+',  # emails
            r'^\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}',  # datas
        ]
        
        for pattern in patterns:
            if re.match(pattern, line_lower):
                return True
        
        # Linhas muito curtas com apenas datas, números, etc.
        if len(line) < 25 and re.match(r'^[\d\s\-\/.,:]+$', line):
            return True
        
        return False
    
    def _extract_pdf_keywords(self, text: str) -> List[str]:
        """Extrai palavras-chave específicas para conteúdo PDF."""
        if not text:
            return []
        
        # Stop words expandidas para contexto acadêmico/institucional
        stop_words = {
            'a', 'o', 'e', 'é', 'da', 'do', 'de', 'para', 'com', 'em', 'no', 'na', 'um', 'uma',
            'por', 'se', 'que', 'como', 'mais', 'ou', 'ao', 'aos', 'as', 'os', 'à', 'às',
            'ele', 'ela', 'eles', 'elas', 'seu', 'sua', 'seus', 'suas', 'este', 'esta',
            'isso', 'aqui', 'assim', 'então', 'quando', 'onde', 'porque', 'mas', 'também',
            'já', 'ainda', 'só', 'até', 'sobre', 'entre', 'sem', 'pelo', 'pela', 'pode',
            'ter', 'tem', 'foi', 'ser', 'está', 'são', 'muito', 'bem', 'fazer', 'todo',
            'toda', 'todos', 'todas', 'cada', 'outro', 'outra', 'outros', 'outras', 'será',
            'página', 'capítulo', 'item', 'deve', 'podem', 'deverá', 'conforme', 'segundo'
        }
        
        # Extrai e limpa palavras
        words = re.findall(r'\b[a-záàâãéêíóôõúç]{3,}\b', text.lower())
        
        # Filtra palavras significativas
        significant_words = []
        for word in words:
            if (word not in stop_words and 
                len(word) >= 3 and 
                not word.isdigit()):
                significant_words.append(word)
        
        # Conta frequências e aplica pontuação
        word_freq = Counter(significant_words)
        scored_words = []
        
        for word, freq in word_freq.items():
            score = freq
            
            # Pontuação especial para termos técnicos/institucionais
            if any(term in word for term in ['ifpe', 'campus', 'curso', 'professor', 'estudante', 
                                           'ensino', 'técnico', 'superior', 'graduação', 'tecnologia']):
                score *= 3
            
            # Pontuação para palavras maiores (mais específicas)
            if len(word) > 7:
                score *= 1.5
            elif len(word) > 5:
                score *= 1.2
            
            # Reduz pontuação para palavras muito frequentes
            if freq > len(significant_words) * 0.08:
                score *= 0.6
            
            scored_words.append((word, score))
        
        # Retorna top 10 palavras-chave
        scored_words.sort(key=lambda x: x[1], reverse=True)
        return [word for word, score in scored_words[:10]]
    
    def _identify_pdf_content_type(self, text: str) -> str:
        """Identifica o tipo de conteúdo do chunk de PDF."""
        text_lower = text.lower()
        
        # Padrões para diferentes tipos de conteúdo
        content_patterns = {
            'acadêmico': ['curso', 'disciplina', 'matrícula', 'professor', 'aula', 'ensino', 'estudante'],
            'institucional': ['ifpe', 'instituto', 'federal', 'campus', 'missão', 'visão', 'objetivos'],
            'regulamento': ['artigo', 'parágrafo', 'inciso', 'resolução', 'portaria', 'norma'],
            'procedimento': ['procedimento', 'passo', 'etapa', 'requisito', 'documentação'],
            'contato': ['contato', 'telefone', 'email', 'endereço', 'atendimento'],
            'eventos': ['evento', 'data', 'prazo', 'cronograma', 'calendário', 'período'],
            'serviços': ['biblioteca', 'laboratório', 'restaurante', 'serviço', 'bolsa', 'auxílio']
        }
        
        # Calcula pontuação para cada tipo
        type_scores = {}
        for content_type, keywords in content_patterns.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                type_scores[content_type] = score
        
        # Retorna o tipo com maior pontuação
        if type_scores:
            return max(type_scores.keys(), key=lambda k: type_scores[k])
        else:
            return 'geral'
    
    def _create_enhanced_pdf_chunk_data(self, text: str, title: str, metadata: Dict, filename: str, 
                                       chunk_index: int, page_start: int, section_type: str, 
                                       document_type: str) -> Dict:
        """Cria dados de chunk PDF com metadados enriquecidos."""
        # Extrai palavras-chave específicas do chunk
        keywords = self._extract_pdf_keywords(text, section_type)
        
        # Calcula métricas do texto
        sentences = self._count_sentences(text)
        words = text.split()
        
        # Extrai informações específicas baseadas no tipo
        specific_info = self._extract_pdf_specific_info(text, section_type, document_type)
        
        # Cria resumo do chunk
        summary = self._create_pdf_chunk_summary(text, title)
        
        # Calcula score de qualidade
        quality_score = self._calculate_pdf_chunk_quality(text, section_type)
        
        return {
            "text": text,
            "title": title,
            "filename": filename,
            "chunk_index": chunk_index,
            "keywords": keywords,
            "section_type": section_type,
            "document_type": document_type,
            "page_start": page_start,
            "sentence_count": sentences,
            "word_count": len(words),
            "char_count": len(text),
            "language": "pt",
            "source": f"PDF: {metadata['title']}",
            "summary": summary,
            "specific_info": specific_info,
            "metadata": {
                "filename": filename,
                "title": metadata['title'],
                "author": metadata.get('author', ''),
                "total_pages": metadata['total_pages'],
                "chunk_index": chunk_index,
                "section_type": section_type,
                "document_type": document_type,
                "page_start": page_start,
                "quality_score": quality_score
            }
        }
    
    def _extract_pdf_keywords(self, text: str, section_type: str) -> List[str]:
        """Extrai palavras-chave específicas para PDFs educacionais."""
        if not text:
            return []
        
        # Stop words específicas para PDFs educacionais
        stop_words = {
            'a', 'o', 'e', 'é', 'da', 'do', 'de', 'para', 'com', 'em', 'no', 'na', 'um', 'uma',
            'por', 'se', 'que', 'como', 'mais', 'ou', 'ao', 'aos', 'as', 'os', 'à', 'às',
            'ele', 'ela', 'eles', 'elas', 'seu', 'sua', 'seus', 'suas', 'este', 'esta',
            'isso', 'aqui', 'assim', 'então', 'quando', 'onde', 'porque', 'mas', 'também',
            'já', 'ainda', 'só', 'até', 'sobre', 'entre', 'sem', 'pelo', 'pela', 'pode',
            'ter', 'tem', 'foi', 'ser', 'está', 'são', 'muito', 'bem', 'fazer', 'todo',
            'toda', 'todos', 'todas', 'cada', 'outro', 'outra', 'outros', 'outras',
            'art', 'artigo', 'parágrafo', 'inciso', 'alínea'  # Específicas de documentos
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
                word.isalnum()):
                significant_words.append(word)
        
        # Conta frequências
        word_freq = Counter(significant_words)
        
        # Palavras-chave prioritárias baseadas no tipo de seção
        priority_keywords = {
            'introducao': ['introdução', 'objetivo', 'finalidade', 'apresentação'],
            'estrutura': ['estrutura', 'organização', 'composição', 'hierarquia'],
            'funcionamento': ['funcionamento', 'procedimento', 'processo', 'tramitação'],
            'requisitos': ['requisito', 'critério', 'exigência', 'condição'],
            'avaliacao': ['avaliação', 'nota', 'conceito', 'aprovação'],
            'geral': ['ifpe', 'instituto', 'federal', 'educação', 'ensino', 'curso']
        }
        
        keywords = []
        
        # Adiciona palavras prioritárias para o tipo de seção
        section_priorities = priority_keywords.get(section_type, priority_keywords['geral'])
        for word in section_priorities:
            if word in significant_words:
                keywords.append(word)
        
        # Adiciona palavras mais frequentes
        for word, freq in word_freq.most_common(10):
            if word not in keywords and freq >= 2:
                keywords.append(word)
        
        return keywords[:8]
    
    def _extract_pdf_specific_info(self, text: str, section_type: str, document_type: str) -> Dict:
        """Extrai informações específicas baseadas no tipo de seção e documento."""
        info = {}
        text_lower = text.lower()
        
        # Informações específicas por tipo de seção
        if section_type == 'objetivos':
            # Extrai objetivos específicos
            obj_patterns = [
                r'objetivo[s]?\s*[:\-]\s*([^\n\.]+)',
                r'finalidade[s]?\s*[:\-]\s*([^\n\.]+)',
                r'visa\s+([^\n\.]+)'
            ]
            
            for pattern in obj_patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                if matches:
                    info['objetivos'] = [match.strip() for match in matches]
                    break
        
        elif section_type == 'requisitos':
            # Extrai requisitos e critérios
            req_patterns = [
                r'requisito[s]?\s*[:\-]\s*([^\n\.]+)',
                r'critério[s]?\s*[:\-]\s*([^\n\.]+)',
                r'exigência[s]?\s*[:\-]\s*([^\n\.]+)'
            ]
            
            requirements = []
            for pattern in req_patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                requirements.extend([match.strip() for match in matches])
            
            if requirements:
                info['requisitos'] = requirements
        
        # Extrai datas importantes
        date_patterns = [
            r'(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})',
            r'(\d{1,2}/\d{1,2}/\d{4})',
            r'(\d{4})'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            if matches:
                info['datas'] = matches[:3]  # Máximo 3 datas
                break
        
        # Extrai números importantes (artigos, parágrafos, etc.)
        if document_type in ['regulamento', 'edital']:
            number_patterns = [
                r'art(?:igo)?\.?\s*(\d+)',
                r'§\s*(\d+)',
                r'inciso\s+([IVX]+)',
                r'capítulo\s+([IVX]+|\d+)'
            ]
            
            numbers = []
            for pattern in number_patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                numbers.extend(matches)
            
            if numbers:
                info['referencias_legais'] = numbers[:5]
        
        return info
    
    def _create_pdf_chunk_summary(self, text: str, title: str) -> str:
        """Cria um resumo conciso do chunk PDF."""
        # Pega as primeiras sentenças mais informativas
        sentences = re.split(r'[.!?]+\s+', text)
        
        if not sentences:
            return text[:100] + "..." if len(text) > 100 else text
        
        # Procura por sentenças que definem ou explicam algo
        for sentence in sentences[:3]:
            sentence = sentence.strip()
            if (len(sentence) > 30 and 
                any(word in sentence.lower() for word in [
                    'é', 'são', 'define-se', 'entende-se', 'considera-se',
                    'objetiva', 'visa', 'tem por finalidade'
                ])):
                return sentence[:150] + "..." if len(sentence) > 150 else sentence
        
        # Fallback: primeira sentença substancial
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 30:
                return sentence[:150] + "..." if len(sentence) > 150 else sentence
        
        return text[:100] + "..." if len(text) > 100 else text
    
    def _calculate_pdf_chunk_quality(self, text: str, section_type: str) -> float:
        """Calcula score de qualidade específico para chunks de PDF."""
        score = 0.5  # Base
        
        # Bônus por tamanho adequado
        length = len(text)
        if 300 <= length <= 1500:
            score += 0.3
        elif length < 100:
            score -= 0.3
        
        # Bônus por estrutura adequada
        sentences = self._count_sentences(text)
        words = len(text.split())
        
        if words > 0:
            sentence_ratio = sentences / words * 100
            if 2 <= sentence_ratio <= 8:
                score += 0.2
        
        # Bônus por palavras-chave relevantes do domínio educacional
        educational_keywords = [
            'instituto', 'curso', 'ensino', 'educação', 'formação',
            'estudante', 'professor', 'avaliação', 'aprovação', 'requisito'
        ]
        
        text_lower = text.lower()
        keyword_count = sum(1 for keyword in educational_keywords if keyword in text_lower)
        if keyword_count >= 2:
            score += 0.2
        
        # Bônus específico por tipo de seção
        section_bonus = {
            'objetivos': 0.1,
            'requisitos': 0.1,
            'avaliacao': 0.1
        }
        score += section_bonus.get(section_type, 0)
        
        return round(min(1.0, max(0.1, score)), 2)
    
    def _count_sentences(self, text: str) -> int:
        """Conta o número de sentenças no texto."""
        return len(re.findall(r'[.!?]+', text))
    
    def _filter_and_improve_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """Filtra e melhora a qualidade dos chunks."""
        improved_chunks = []
        
        for chunk in chunks:
            # Remove chunks muito pequenos ou de baixa qualidade
            if (len(chunk['text']) < 80 or 
                chunk['metadata']['quality_score'] < 0.3):
                continue
            
            # Melhora o texto do chunk
            chunk['text'] = self._improve_pdf_chunk_text(chunk['text'])
            
            improved_chunks.append(chunk)
        
        return improved_chunks
    
    def _improve_pdf_chunk_text(self, text: str) -> str:
        """Melhora o texto do chunk PDF para maior clareza."""
        # Remove espaços extras e normaliza
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Remove linhas que são só numeração ou referência
        lines = text.split('\n')
        clean_lines = []
        
        for line in lines:
            line = line.strip()
            # Remove linhas muito curtas ou que são só números/referências
            if (len(line) > 10 and 
                not re.match(r'^[\d\s\-\.\|\(\)]+$', line) and
                not re.match(r'^Art\.?\s*\d+\s*$', line.strip())):
                clean_lines.append(line)
        
        return ' '.join(clean_lines) if clean_lines else text