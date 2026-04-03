"""FastAPI config to be called from main.py"""

from fastapi import FastAPI

def create_app() -> FastAPI:
    """Create and configure the FastAPI app."""
    app = FastAPI(
        title="FastAPI for CortexSail Agentic RAG",
        version="1.0.0",
        description="This API serves as the backend for the CortexSail Agentic RAG system, providing endpoints for processing and retrieving information related to the agent's operations."
    )

    @app.get("/health-check")
    def health_check():
        return {"status": "API is healthy"}

    return app

app = create_app()