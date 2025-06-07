from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from models.schemas import (
    QueryRequest, QueryResponse, DocumentBatch, DeleteRequest, ResetRequest, 
    Document, WebScrapingRequest, WebScrapingResponse, DocumentItem, DocumentListResponse
)
from services.aiservice import AIService
from services.webscraper import WebScraperService
from services.pdf_processor import PDFProcessorService
from typing import List, Dict, Any, Union
from datetime import datetime

router = APIRouter()
ai_service = AIService()
web_scraper = WebScraperService()
pdf_processor = PDFProcessorService()

@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Endpoint para consultar o assistente Tango.
    """
    try:
        result = ai_service.answer_query(
            query=request.query,
            conversation_history=request.conversation_history
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar consulta: {str(e)}")

@router.post("/documents", response_model=Dict[str, List[int]])
async def add_documents(request: DocumentBatch):
    """
    Adiciona documentos à base de conhecimento.
    """
    try:
        # Processa documentos passados como strings ou objetos Document
        documents = []
        metadata_list = []
        
        # Verifica o tipo dos documentos fornecidos
        for doc in request.documents:
            if isinstance(doc, str):
                documents.append(doc)
                metadata_list.append(None)
            elif isinstance(doc, dict) and "text" in doc:
                documents.append(doc["text"])
                metadata_list.append(doc.get("metadata", None))
            elif hasattr(doc, "text"):  # Se for um objeto Pydantic Document
                documents.append(doc.text)
                metadata_list.append(doc.metadata if hasattr(doc, "metadata") else None)
        
        # Se metadata foi fornecido diretamente no request, sobrescreve o metadata dos documentos
        if request.metadata:
            metadata_list = request.metadata
        
        result = ai_service.seed_knowledge_base(documents)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao adicionar documentos: {str(e)}")

@router.post("/scrape-website", response_model=WebScrapingResponse)
async def scrape_website(request: WebScrapingRequest):
    """
    Extrai conteúdo de um site em chunks e adiciona à base de conhecimento.
    """
    try:
        print(f"Iniciando web scraping para: {request.url}")
        
        documents_to_add = []
        failed_urls = []
        scraped_urls = []
        total_chunks = 0
        
        if request.scrape_multiple:
            # Scraping de múltiplas páginas
            print("Modo: múltiplas páginas")
            results = web_scraper.scrape_sitemap_chunked(request.url, request.max_pages)
        else:
            # Scraping de uma única URL
            print("Modo: URL única")
            results = [web_scraper.scrape_url_chunked(request.url)]
        
        print(f"Resultados do scraping: {len(results)} URLs processadas")
        
        # Processa os resultados
        for result in results:
            print(f"Processando resultado para {result['url']}")
            print(f"Sucesso: {result['success']}, Chunks: {len(result.get('chunks', []))}")
            
            if result['success'] and result.get('chunks'):
                scraped_urls.append(result['url'])
                
                # Processa cada chunk individualmente
                for chunk in result['chunks']:
                    # Cria documento otimizado para busca
                    document_text = f"""Fonte: {chunk['title']}
URL: {chunk['url']}
Tipo: {chunk['content_type']}
Palavras-chave: {', '.join(chunk['keywords'])}

{chunk['text']}"""
                    
                    documents_to_add.append(document_text)
                    total_chunks += 1
                    print(f"Chunk {total_chunks} adicionado: {len(chunk['text'])} caracteres")
            else:
                print(f"URL falhou: {result['url']}, Erro: {result.get('error', 'Desconhecido')}")
                failed_urls.append(result['url'])
        
        print(f"Total de documentos para adicionar: {len(documents_to_add)}")
        
        # Adiciona os documentos à base de conhecimento
        documents_added = 0
        if documents_to_add:
            print("Adicionando documentos à base de conhecimento...")
            add_result = ai_service.seed_knowledge_base(documents_to_add)
            documents_added = len(add_result.get('ids', []))
            print(f"Documentos adicionados com sucesso: {documents_added}")
        else:
            print("Nenhum documento para adicionar")
        
        return WebScrapingResponse(
            success=True,
            message=f"Web scraping concluído. {documents_added} chunks de {len(scraped_urls)} páginas adicionados.",
            documents_added=documents_added,
            failed_urls=failed_urls,
            scraped_urls=scraped_urls
        )
        
    except Exception as e:
        print(f"Erro durante web scraping: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro durante web scraping: {str(e)}")

@router.delete("/documents", response_model=Dict[str, bool])
async def delete_documents(request: DeleteRequest):
    """
    Remove documentos da base de conhecimento pelos IDs.
    """
    try:
        result = ai_service.vector_db.delete(request.ids)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao remover documentos: {str(e)}")

@router.post("/reset", response_model=Dict[str, bool])
async def reset_knowledge_base(request: ResetRequest):
    """
    Reinicia a base de conhecimento, removendo todos os documentos.
    """
    if not request.confirm:
        raise HTTPException(status_code=400, detail="Confirmação necessária para reiniciar a base de conhecimento")
    
    try:
        result = ai_service.vector_db.reset()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao reiniciar a base de conhecimento: {str(e)}")

@router.get("/documents/list", response_model=DocumentListResponse)
async def list_documents():
    """
    Lista todos os documentos da base de conhecimento com agrupamento melhorado.
    """
    try:
        # Obtém os documentos e seus metadados do serviço VectorDB
        documents = ai_service.vector_db.documents
        metadata = ai_service.vector_db.metadata
        
        # Agrupa documentos por fonte para melhor visualização
        grouped_docs = {}
        doc_list = []
        
        for i, doc in enumerate(documents):
            # Extrai informações da fonte (URL, PDF, ou documento manual)
            source_info = _extract_source_info(doc)
            
            # Prepara prévia do conteúdo (primeiras 200 chars)
            content_preview = doc[:200] + "..." if len(doc) > 200 else doc
            
            doc_item = DocumentItem(
                id=i,
                content=content_preview,
                full_content=doc,
                url=source_info['url'],
                title=source_info['title'],
                metadata=metadata[i] if metadata and i < len(metadata) else None
            )
            
            doc_list.append(doc_item)
            
            # Agrupa por fonte (URL para websites, nome do arquivo para PDFs)
            group_key = source_info['group_key']
            if group_key not in grouped_docs:
                grouped_docs[group_key] = []
            grouped_docs[group_key].append(doc_item)
        
        return DocumentListResponse(
            documents=doc_list,
            grouped_by_url=grouped_docs,
            total_documents=len(doc_list),
            unique_sources=len(grouped_docs)
        )
        
    except Exception as e:
        print(f"Erro ao listar documentos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao listar documentos: {str(e)}")

@router.post("/upload-pdf", response_model=Dict[str, Any])
async def upload_pdf(file: UploadFile = File(...), chunk_size: int = 1000):
    """
    Upload e processamento de arquivo PDF com organização similar ao web scraping.
    """
    try:
        # Verifica se é um arquivo PDF
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Apenas arquivos PDF são aceitos")
        
        # Lê o conteúdo do arquivo
        file_content = await file.read()
        
        if len(file_content) == 0:
            raise HTTPException(status_code=400, detail="Arquivo PDF está vazio")
        
        print(f"Processando PDF: {file.filename} ({len(file_content)} bytes)")
        
        # Processa o PDF
        chunks = pdf_processor.process_pdf(file_content, file.filename, chunk_size)
        
        if not chunks:
            raise HTTPException(status_code=400, detail="Não foi possível extrair texto do PDF")
        
        print(f"PDF processado: {len(chunks)} chunks extraídos")
        
        # Prepara documentos para adicionar à base de conhecimento (formato similar ao web scraping)
        documents_to_add = []
        
        for chunk in chunks:
            # Formato consistente com web scraping para melhor agrupamento
            document_text = f"""Fonte: {chunk['title']}
Arquivo: {chunk['filename']}
Tipo: PDF
Página: {chunk['page_reference']} de {chunk['total_pages']}
Palavras-chave: {', '.join(chunk['keywords'])}

{chunk['text']}"""
            
            documents_to_add.append(document_text)
        
        # Adiciona à base de conhecimento
        if documents_to_add:
            result = ai_service.seed_knowledge_base(documents_to_add)
            documents_added = len(result.get('ids', []))
        else:
            documents_added = 0
        
        return {
            "success": True,
            "message": f"PDF processado com sucesso! {documents_added} chunks adicionados.",
            "filename": file.filename,
            "chunks_extracted": len(chunks),
            "documents_added": documents_added,
            "total_pages": chunks[0]['total_pages'] if chunks else 0,
            "title": chunks[0]['title'] if chunks else file.filename
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro ao processar PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao processar PDF: {str(e)}")

# Função auxiliar para extrair informações da fonte
def _extract_source_info(doc: str) -> Dict[str, str]:
    """
    Extrai informações da fonte do documento para agrupamento.
    """
    lines = doc.split('\n')
    
    # Valores padrão
    source_info = {
        'url': 'Documento manual',
        'title': 'Documento sem título',
        'group_key': 'Documentos manuais',
        'type': 'manual'
    }
    
    # Processa cada linha para extrair metadados
    for line in lines:
        line = line.strip()
        
        if line.startswith('Fonte:'):
            title = line.replace('Fonte:', '').strip()
            source_info['title'] = title
            
        elif line.startswith('URL:'):
            url = line.replace('URL:', '').strip()
            source_info['url'] = url
            source_info['group_key'] = url
            source_info['type'] = 'website'
            
        elif line.startswith('Arquivo:'):
            filename = line.replace('Arquivo:', '').strip()
            source_info['url'] = f"📄 {filename}"
            source_info['group_key'] = f"PDF: {filename}"
            source_info['type'] = 'pdf'
            
        elif line.startswith('Tipo: PDF'):
            source_info['type'] = 'pdf'
            # Se não temos título ainda, usa o nome do arquivo
            if source_info['title'] == 'Documento sem título':
                # Tenta extrair do grupo ou da próxima linha
                if 'Arquivo:' in doc:
                    filename_line = [l for l in lines if l.startswith('Arquivo:')]
                    if filename_line:
                        filename = filename_line[0].replace('Arquivo:', '').strip()
                        source_info['title'] = filename.replace('.pdf', '')
    
    return source_info