from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union

class QueryRequest(BaseModel):
    query: str
    conversation_history: Optional[List[dict]] = []

class QueryResponse(BaseModel):
    response: str
    sources: List[str] = []

class Document(BaseModel):
    text: str
    metadata: Optional[Dict[str, Any]] = None

class DocumentBatch(BaseModel):
    documents: List[Union[str, Document]]
    metadata: Optional[List[Dict[str, Any]]] = None

class DeleteRequest(BaseModel):
    ids: List[int]

class ResetRequest(BaseModel):
    confirm: bool = False