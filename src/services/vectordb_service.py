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

        ###To be used everywhere
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

    ####Function for uploading onboarding documents to ChromaDB
    def upload_csv_content(self, csv_file_path: str):
        """Upload onboarding CSV to ChromaDB as vector embeddings to be used for retrieval during the user query and response generation."""

        try:
            ##Reading the CSV file using pandas
            df = pd.read_csv(csv_file_path)

            ##Iterating through the rows of the dataframe and creating the documents and their metadata for uploading to ChromaDB

            ###Creating documents and metadata for each row in the dataframe to be uploaded to ChromaDB

            documents = []
            metadata = []
            ids = []

            for index,row in df.iterrows():

                ##Appending the filtered documents to the list to be uploaded to ChromaDB

                document_builder_row = []

                if pd.notna(row.get("Title")) :
                    document_builder_row.append(f"Title: {row['Title']}")

                if pd.notna(row.get("Role Description")):
                    document_builder_row.append(f"Role Description: {row['Role Description']}")
                if pd.notna(row.get("Department")):
                    document_builder_row.append(f"Department: {row['Department']}")
                if pd.notna(row.get("Team")):
                    document_builder_row.append(f"Team: {row['Team']}")
                if pd.notna(row.get("Role")):
                    document_builder_row.append(f"Role: {row['Role']}")
                if pd.notna(row.get("Location")):
                    document_builder_row.append(f"Location: {row['Location']}")
                if pd.notna(row.get("Prerequisite Documents")):
                    document_builder_row.append(f"Prerequisite Documents: {row['Prerequisite Documents']}")

                embedding_string_document = "\n".join(document_builder_row)

                if not embedding_string_document.strip():
                    continue
                documents.append(embedding_string_document)

                ###Creating the metadata for each document to be uploaded to ChromaDB

                metadatas = {
                    "Document ID": str (row.get("Document ID", "")),
                    "Title": str (row.get("Title", "")),
                    "Role Description": str (row.get("Role Description", "")),
                    "Department": str (row.get("Department", "")),
                    "Team": str (row.get("Team", "")),
                    "Role": str (row.get("Role", "")),
                    "Location": str (row.get("Location", "")),
                    "Prerequisite Documents": str (row.get("Prerequisite Documents", ""))
                }
                metadata.append(metadatas)
                ids.append(str(row.get("Document ID", index)))

            ##Batching and sending documents to ChromaDB for uploading

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
            print(f"Error uploading CSV content to ChromaDB: {e}")
            raise
    
    ##Function for Search Similar Onboarding Documents - ChromaDB Embedding

    def search_similar_onboarding_documents(self, query: str, n_results: int = 5, filters: Optional[Dict] = None) -> List[Dict]:
        """Search Similar Onboarding Document based on user query"""

        try:
            ###Narrowing the search result using the filters provided by the user - for example, filtering based on the release status of the document - Using where clause in chromaDB search method

            ##No narrowing entire collection will be searched for the similar documents based on the user query

            where_clause = None
            if filters:
                where_clause = filters

            ##Generating query embedding using the Azure OpenAI embeddings endpoint for the user query 

            query_embedding = self.embedding_function.embed_query_function(query)
            print(f"Generated query embedding for the user query: {query_embedding}")

            results = self.collection.query(
             query_embedding = [query_embedding],
             n_results = n_results,
             where = where_clause
            )

            similar_documents = []

            ##Checking if the results contain ids list and inside that another list is present and has more than 0 elements to ensure that there are similar documents found for the user query - after chroma query for similar documents

            if results['ids'] and len(results['ids'][0]) > 0:
                for i in range(len(results["ids"][0])):
                    document_result = {
                        "id": results["ids"][0][i],
                        "document": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "similarity_score": 1 - results["distances"][0][i] if "distances" in results else None
                    }
                    similar_documents.append(document_result)
            print(f"Found similar documents: {similar_documents}")
            return similar_documents

        except Exception as e:
            print(f"Error searching similar onboarding documents: {e}")
            return []
    
    def get_collection_details(self) -> Dict:
        """Extract the details of collection"""

        try:
            collection_count = self.collection.count()

            return {
                "collection_name": self.collection_name,
                "number_of_documents": collection_count,
                "persistent_directory": self.persistent_directory
            }
        except Exception as e:
            print(f"Error getting collection details: {e}")
            return {}

    def clear_complete_collection(self):
        """Clear the complete collection in ChromaDB - for testing purposes"""

        try:
            self.client.delete_collection(name = self.collection_name)

            ### Creating a new collection after deleting so that the collection is ready to be used for uploading the documents and their embeddings again
            self.collection = self.client.create_collection(name = self.collection_name, metadata={
                "description": "Collection for storing the document chunks and their vector embeddings for Cortexsail application"
            })
            print(f"Collection {self.collection_name} cleared successfully and new collection created.")
        except Exception as e:
            print(f"Error clearing the collection: {e}")
            raise