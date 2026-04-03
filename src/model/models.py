"""pydantic model for the Agentic RAG"""

from typing import Optional
from pydantic import BaseModel

class RAGQueryRequest(BaseModel):
    """Request model for RAG query"""
    query: str
    session_id: Optional[str] = None

class RAGFilters(BaseModel):
    """Filters for RAG query"""
    source: Optional[str] = None
    document_id: Optional[str] = None
    file_name: Optional[str] = None
    category: Optional[str] = None
    topic: Optional[str] = None
    author: Optional[str] = None
    department: Optional[str] = None
    tags: Optional[list[str]] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    top_k: Optional[int] = None

class SourceDocument(BaseModel):
    """Model for source document returned by RAG query"""
    source: Optional[str] = None
    document_id: Optional[str] = None
    content: Optional[str] = None
    score: Optional[float] = None

class RAGResponse(BaseModel):
    """Response model for RAG query"""
    query: str
    answer: str
    source: list[SourceDocument] = []

class DocumentIngestRequest(BaseModel):
    """Request model for document ingestion"""
    document_id: str
    content: str
    source: Optional[str] = None
    file_name: str
    department: Optional[str] = None
    category: Optional[str] = None
    topic: Optional[str] = None
    author: Optional[str] = None

class DocuementIngestResponse(BaseModel):
    """Response model for document ingestion"""
    document_id: str
    status: str
    message: Optional[str] = None