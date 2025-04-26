from fastapi import APIRouter, HTTPException
from models.schemas import QueryRequest, QueryResponse
from services.aiservice import AIService

router = APIRouter()
ai_service = AIService()

@router.post("/query", response_model=QueryResponse)
async def query_assistant(request: QueryRequest):
    """
    Endpoint para fazer perguntas à assistente.
    """
    try:
        response = ai_service.answer_query(request.query, request.conversation_history)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar consulta: {str(e)}")


@router.post("/train")
async def train_assistant(documents: list[str]):
    """
    Endpoint para adicionar novos documentos à base de conhecimento.
    """
    try:
        count = ai_service.seed_knowledge_base(documents)
        return {"status": "success", "documents_added": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao treinar assistente: {str(e)}")