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

    def embed_query_function(self, input:str) -> List[float]:
        # Embedding for the user query
            if isinstance(input, str):
                embedding = self.__call__([input])
                result = embedding[0]
                # print(f""Generated embedding for the query: {result}")
                return result
            return self(input)[0]
    
    def embed_document_function(self, input: list[str]) -> List[List[float]]:
        ###embedding generation for documents chunk
        ### Check if the input is a List of str or a single string
        if isinstance(input, List[str]):
            return self([input])
        return self(input)

class VectorDBService:
    """Initializes the VectorDBService with ChromaDB client and collection."""

    def __init__(self, persistent_directory: str = "./chroma_db"):
    
        """Initializes the ChromaDB client and the collection for storing documents and their embeddings."""

        ##Persistent Directory for chromaDB - storing the vector embeddings and the metadata of the documents
        self.persistent_directory = persistent_directory

        self.collection_name = "conf_collection"

        ##Client for ChromaDB - For accessing the Persistent Directory
        self.client = chromadb.PersistentClient(path = persistent_directory)

        ###Creating the embedding

        self.embedding_function = AzureEmbeddingFunction()


        ##Get or Create collection function for chromaDB

        ##Correct the metadata object
        self.collection = self.client.get_or_create_collection(name = self.collection_name, embedding_function = self.embedding_function,
        metadata={"description": "Collection for storing the document chunks and their vector embeddings for Cortexsail application"})

        print(f"Collection name {self.collection_name} initialized successfully.")


    def upload_csv_content(self, csv_file_path: str):
        """Upload CSV to ChromaDB as vector embeddings to be used for retrieval during the user query and response generation."""

        try:
            ##Reading the CSV file using pandas
            df = pd.read_csv(csv_file_path)

            ##Iterating through the rows of the dataframe and creating the documents and their metadata for uploading to ChromaDB

            ##Filter based on the release status - narrowing the scope of document
            if "Release Status" in df.columns:
                df = df[df["Release Status"].isin(["At Risk", "Blocked", "Delayed"])]

            ###Creating documents and metadata for each row in the dataframe to be uploaded to ChromaDB

            documents = []
            metadata = []
            ids = []

            for index,row in df.iterrows():

                ##Appending the filtered documents to the list to be uploaded to ChromaDB

                document_builder_row = []

                if pd.notna(row.get("Issue Key")) :
                    document_builder_row.append(f"Issue Key: {row['Issue Key']}")

                if pd.notna(row.get("Issue Type")):
                    document_builder_row.append(f"Issue Type: {row['Issue Type']}")
                if pd.notna(row.get("Summary")):
                    document_builder_row.append(f"Summary: {row['Summary']}")
                if pd.notna(row.get("Description")):
                    document_builder_row.append(f"Description: {row['Description']}")
                if pd.notna(row.get("Priority")):
                    document_builder_row.append(f"Priority: {row['Priority']}")
                if pd.notna(row.get("Release Status")):
                    document_builder_row.append(f"Release Status: {row['Release Status']}")

                embedding_string_document = "\n".join(document_builder_row)

                if not embedding_string_document.strip():
                    continue
                documents.append(embedding_string_document)

                ###Creating the metadata for each document to be uploaded to ChromaDB

                metadatas = {
                    "Issue Key": str (row.get("Issue Key", "")),
                    "Issue Type": str (row.get("Issue Type", "")),
                    "Summary": str (row.get("Summary", "")),
                    "Description": str (row.get("Description", "")),
                    "Priority": str (row.get("Priority", "")),
                    "Release Status": str (row.get("Release Status", ""))
                }
                metadata.append(metadatas)

                ##Batching and sending every    documents to ChromaDB for uploading

                batch_size = 100
                total_documents_added = 0

                for i in range(0, len(documents), batch_size):
                    batch_document = documents[i:i + batch_size]

                    batch_metadata = metadata[i:i + batch_size]

                    batch_ids = ids[i:i + batch_size]

                    ###Add in Collection - ChromaDB method to add the documents, their metadata and the unique ids to the collection
                    self.collection.add(
                        documents = batch_document,
                        metadatas = batch_metadata,
                        ids = batch_ids
                    )
                    
                    total_documents_added += len(batch_document)
                    print(f"Successfully added {total_documents_added} documents to the collection.")
        except Exception as e:
            print(f"Error uploading CSV content to ChromaDB")
            raise