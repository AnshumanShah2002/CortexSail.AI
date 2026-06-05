"""
API / Controller layer for CortexSail Agentic RAG system. This module defines the FastAPI application and includes routers for handling API endpoints related to the agent's operations. It serves as the entry point for the API, configuring the app and providing a health check endpoint.
"""

from fastapi import APIRouter, HTTPException, Response, Request, Cookie
from typing import Optional
from src.model.models import RAGQueryRequest, RAGResponse, DocumentIngestRequest, DocumentIngestResponse, RAGFilters, RequestModelConfluenceAnalyzeDocumentTask, SourceDocument, ConfluenceDocumentFilter, ConfluenceDocumentAnalysisModel,ConfluenceDocumentAnalysisResultModel
RequestModelConfluenceAnalyzeDocumentTask

###Write the service layer first before using it with API layer, this is to ensure separation of concerns and maintain a clean architecture. The service layer will handle the business logic and interactions with external systems, while the API layer will focus on handling HTTP requests and responses.
from src.services.confluence_service_layer import ConfluenceService
from src.services import vectordb_service

#Defining the router instance for the API endpoints related to the agent's operations, this will be included in the main FastAPI app in app.py
router = APIRouter()
#Confluence service instance
confluence_service_instance = ConfluenceService()

#API endpoint takes the endpoint path and the response model which is the expected output format of the API response, this helps in automatic validation and documentation generation for the API. 

#For confluence analyze document task
@router.post("/analyze", response_model = ConfluenceDocumentAnalysisModel)
async def analyze_Confluence_document_task(
    request: RequestModelConfluenceAnalyzeDocumentTask,
    # session_id: Optional[str] = Cookie(None)
):
    """API endpoint for analyzing a confluence document based on the provided query.
    
    request: RequestModelConfluenceAnalyzeDocumentTask - The request body containing the query for analyzing the confluence document.

    Args:
    request: JiraAnalysisRequest with the user's prompt for analyzing the confluence document.

    Returns:
    ConfluenceDocumentAnalysisModel: The response model containing the analysis result of the confluence document.
    """
    try:
        if not request.query.strip():
            raise HTTPException(status_code = 400, detail="Query cannot be empty.")


        result = await confluence_service_instance.user_prompt(request.query)

        confluence_analysis_result = ConfluenceDocumentAnalysisResultModel(
            success = result["success"],
            output = result["output"],
            message = result.get("message")
        )

        return ConfluenceDocumentAnalysisModel(response_answer = confluence_analysis_result)
    except Exception as e:
        raise HTTPException(status_code = 500, detail=f"An error occurred while processing the request: {str(e)}")