"""Pydantic models for the Agentic RAG API"""

from typing import Optional
from pydantic import BaseModel

#Generic models for RAG system, these can be extended or modified as needed for specific tools or integrations



class RAGQueryRequest(BaseModel):
	query: str
	#integrate with redis then check
	session_id: Optional[str] = None


class RAGFilters(BaseModel):
	"""Filters for RAG document retrieval"""

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
	source: Optional[str] = None
	document_id: Optional[str] = None
	content: Optional[str] = None
	score: Optional[float] = None


class RAGResponse(BaseModel):
	query: str
	answer: str
	sources: list[SourceDocument] = []


class DocumentIngestRequest(BaseModel):
	document_id: str
	content: str
	source: Optional[str] = None
	file_name: Optional[str] = None
	category: Optional[str] = None
	topic: Optional[str] = None
	author: Optional[str] = None
	department: Optional[str] = None


class DocumentIngestResponse(BaseModel):
	document_id: str
	status: str
	message: Optional[str] = None

    
###Confluence specific models for the confluence document fetcher tool
class ConfluenceDocumentFilter(BaseModel):
	space: Optional[str] = None
	type: Optional[str] = "page"
	title: Optional[str] = None
	text: Optional[str] = None
	label: Optional[str] = None
	labels: Optional[list[str]] = None
	creator: Optional[str] = None
	contributor: Optional[str] = None
	id: Optional[str] = None
	parent: Optional[str] = None
	created_after: Optional[str] = None
	created_before: Optional[str] = None
	lastmodified_after: Optional[str] = None
	lastmodified_before: Optional[str] = None
	order_by: Optional[str] = None

class ConfluenceUserLoginResponse(BaseModel):
    """Response model for Confluence login"""
    success: bool
    session_id: Optional[str] = None
    message: Optional[str] = None