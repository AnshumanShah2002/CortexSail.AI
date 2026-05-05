"""
API / Controller layer for CortexSail Agentic RAG system. This module defines the FastAPI application and includes routers for handling API endpoints related to the agent's operations. It serves as the entry point for the API, configuring the app and providing a health check endpoint.
"""

from fastapi import APIRouter, HTTPException, Response, Request, Cookie
from typing import Optional
from src.model.models import RAGQueryRequest, RAGResponse, DocumentIngestRequest, DocumentIngestResponse, RAGFilters, SourceDocument, ConfluenceDocumentFilter

###Write the service layer first before using it with API layer, this is to ensure separation of concerns and maintain a clean architecture. The service layer will handle the business logic and interactions with external systems, while the API layer will focus on handling HTTP requests and responses.
from src.services import confluence_service_layer

from src.services import vectordb_service

