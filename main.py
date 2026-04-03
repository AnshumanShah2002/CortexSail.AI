"Main entry point"

import uvicorn
from src.configuration.settings import settings

def main():
    """Configuring for FASTAPI"""
    uvicorn.run("src.api.app:app", host=settings.api_host, port=settings.api_port, reload=settings.api_reload)
if __name__ == "__main__":    main()