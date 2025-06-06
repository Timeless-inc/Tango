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

# Novos schemas para web scraping
class WebScrapingRequest(BaseModel):
    url: str
    max_length: Optional[int] = 5000
    scrape_multiple: Optional[bool] = False
    max_pages: Optional[int] = 10

class WebScrapingResponse(BaseModel):
    success: bool
    message: str
    documents_added: int
    failed_urls: List[str] = []
    scraped_urls: List[str] = []

# Schema para documento individual na listagem
class DocumentItem(BaseModel):
    id: int
    content: str
    full_content: str
    url: str
    title: str
    metadata: Optional[Dict[str, Any]] = None

# Schema para resposta da listagem de documentos
class DocumentListResponse(BaseModel):
    documents: List[DocumentItem]
    grouped_by_url: Dict[str, List[DocumentItem]]
    total_documents: int
    unique_sources: int