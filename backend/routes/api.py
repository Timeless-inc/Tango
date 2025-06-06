from fastapi import APIRouter, HTTPException, Depends
from models.schemas import (
    QueryRequest, QueryResponse, DocumentBatch, DeleteRequest, ResetRequest, 
    Document, WebScrapingRequest, WebScrapingResponse, DocumentItem, DocumentListResponse
)
from services.aiservice import AIService
from services.webscraper import WebScraperService
from typing import List, Dict, Any, Union
from datetime import datetime

router = APIRouter()
ai_service = AIService()
web_scraper = WebScraperService()

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

# Nova rota para web scraping otimizada
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
    Lista todos os documentos da base de conhecimento.
    """
    try:
        # Obtém os documentos e seus metadados do serviço VectorDB
        documents = ai_service.vector_db.documents
        metadata = ai_service.vector_db.metadata
        
        # Agrupa documentos por URL para melhor visualização
        grouped_docs = {}
        doc_list = []
        
        for i, doc in enumerate(documents):
            # Extrai URL do documento se disponível
            url = "URL não identificada"
            if "URL:" in doc:
                url_line = [line for line in doc.split('\n') if line.startswith('URL:')]
                if url_line:
                    url = url_line[0].replace('URL:', '').strip()
            
            # Extrai título/fonte
            title = "Documento sem título"
            if "Fonte:" in doc:
                title_line = [line for line in doc.split('\n') if line.startswith('Fonte:')]
                if title_line:
                    title = title_line[0].replace('Fonte:', '').strip()
            
            # Prepara prévia do conteúdo (primeiras 200 chars)
            content_preview = doc[:200] + "..." if len(doc) > 200 else doc
            
            doc_item = DocumentItem(
                id=i,
                content=content_preview,
                full_content=doc,
                url=url,
                title=title,
                metadata=metadata[i] if metadata and i < len(metadata) else None
            )
            
            doc_list.append(doc_item)
            
            # Agrupa por URL para estatísticas
            if url not in grouped_docs:
                grouped_docs[url] = []
            grouped_docs[url].append(doc_item)
        
        return DocumentListResponse(
            documents=doc_list,
            grouped_by_url=grouped_docs,
            total_documents=len(doc_list),
            unique_sources=len(grouped_docs)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar documentos: {str(e)}")