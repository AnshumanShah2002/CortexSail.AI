"""Base settings configuration for Cortexsail"""

from pydantic import Field
import os
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pydantic import BaseSettings, Field
from configuration.settings import Settings



class Settings(BaseSettings):

    ## Environ variables for usage azure model
    azure_api_key: str = "####"
    azure_api_endpoint = "####"
    azure_api_version = "###"
    azure_model_version = "####"

    ###Embedding model config###
    embedding_model_name: str = "###"
    embedding_deployment_name: str = "####"
    embedding_api_version: str = "####"
    embedding_model_dimension: int = 1024 #change as per requirement
    azure_endpoint: str = "####"

    ### Basic configuration ###
    base_model_name: str = "####"
    base_model_llm_temperature: float = 0.5
    model_max_tokens = 1000


    ### memory flag ###
    short_term_memory_flag:bool = False
    long_term_memory_flag:bool = False

    ###MCP config
    mcp_endpoint: str = Field(
        default="https://localhost:8081/sse",
        description="Endpoint URL for the MCP server"
    )

    mcp_transport: str = Field(
        default="sse",
        description="Transport method for MCP communication (e.g., 'sse', 'websocket')"
    )

    mcp_connection_timeout: int = Field(
        default=60,
        description="Connection timeout in seconds for MCP communication"
    )   


    #Redis config
    # redis_host: str = Field(default="localhost")

    ### Vector DB config - ChromaDB config
    vector_db_persist_dir: str = Field(
        default="./chroma_db",
        description="Directory path for persisting ChromaDB data"
    )

    vector_db_collection_name: str = Field(
        default="Cortexsail_documents",
        description="ChromaDB collection name for storing the documents and their embeddings"
    )
    vector_db_similarity_metric: float = Field(
        default=0.6,
        description="Similarity metric for ChromaDB vector comparisons and its baseline value for filtering the relevant documents based on the user's query"
    )

    class Config:
        env_file = ".env"
        case_sensitivity = False
        
    def boot_settings(self) -> Settings:
        try:
            load_dotenv()
            settings = Settings()
            os.environ["AZURE_API_KEY"] = settings.azure_api_key
            os.environ["AZURE_API_ENDPOINT"] = settings.azure_api_endpoint
            os.environ["AZURE_MODEL_VERSION"] = settings.azure_model_version
            os.environ["AZURE_API_VERSION"] = settings.azure_api_version

            #To be toggled when declaring the memory config file for both types
            return settings
        except Exception as e:
            print(f"Failed to load the config with issue as: {e}")
            raise ValueError(f"Config issue occured")
        
settings = Settings() 

