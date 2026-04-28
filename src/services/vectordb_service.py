"""
VectorDB for storing and querying the embedded document chunk.
"""
import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.utils import embedding_functions
from typing import List, Dict, Optional
import pandas as pd
from pathlib import Path
from src.configuration.settings import settings
import json
from openai import AzureOpenAI


class AzureEmbeddingFunction:
    def __init__(self):
        ##Creating embedding function using Azure OpenAI embeddings endpoint
        self.client = AzureOpenAI(
            api_key= settings.azure_api_key,
            api_version= settings.embedding_api_version,
            azure_endpoint= settings.azure_endpoint
        )
        self.deployment = settings.embedding_deployment_name

        print(f'Initialized azure embedding deployment with deployment model: {self.deployment}')
    def name(self):
        "Return a string identifier for this embedding function to ChromaDB."
        return f"azure-openai-{self.deployment}"
    

    """ Function to generate the embeddings for the input text doc using Azure OpenAI embeddings endpoint """

    def __call__(self , input: List[str]) -> List[List[float]]:
        try:

            ##Azure method to generate the embeddings
            response = self.client.embeddings.create(input=input, model=self.deployment)
            embeddings = [item.embedding for item in response.data]

            return embeddings
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            return []
    
    """ Function to create the vector embedding for the user query using Azure OpenAI embeddings endpoint """

    # def embed_query(self, input:str) -> List[float]:
    #     try:
    #         if isinstance(input, str):
    #             embedding = self.__call__([input])
    #             result = embedding[0]
