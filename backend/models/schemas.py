from pydantic import BaseModel
from typing import List, Optional


class Message(BaseModel):
    role: str  # "user" ou "assistant"
    content: str


class Conversation(BaseModel):
    messages: List[Message]


class QueryRequest(BaseModel):
    query: str
    conversation_history: Optional[List[Message]] = []


class QueryResponse(BaseModel):
    response: str
    sources: Optional[List[str]] = None