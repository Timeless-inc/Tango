from fastapi import APIRouter, HTTPException, Depends
from models.schemas import QueryRequest, QueryResponse, DocumentBatch, DeleteRequest, ResetRequest, Document
from services.aiservice import AIService
from typing import List, Dict, Any, Union

router = APIRouter()
ai_service = AIService()

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

# Adicione esta nova rota após as outras rotas de documentos existentes

@router.get("/documents/list", response_model=Dict[str, List[Union[str, Dict[str, Any]]]])
async def list_documents():
    """
    Lista todos os documentos da base de conhecimento.
    """
    try:
        # Obtém os documentos e seus metadados do serviço VectorDB
        documents = ai_service.vector_db.documents
        metadata = ai_service.vector_db.metadata
        
        # Prepara a resposta com documentos e IDs
        doc_list = []
        for i, doc in enumerate(documents):
            doc_list.append({
                "id": i,
                "content": doc,
                "metadata": metadata[i] if metadata and i < len(metadata) else None
            })
            
        return {"documents": doc_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar documentos: {str(e)}")