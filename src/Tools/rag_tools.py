"""Cortex RAG tools. This module defines CrewAI tools for the RAG agents.
These tools can be called by agents to perform RAG-related tasks such as
Confluence fetching and semantic document search.
"""

from attr import fields
from crewai import tools
from crewai.tools import tool
from cortex import CORTEX #implement on clear picture
from src.model.models import ConfluenceDocumentFilter, RAGQueryRequest,RAGFilters,SourceDocument,RAGResponse,DocumentIngestRequest,DocumentIngestResponse
from typing import Any, Dict, List

from atlassian import Confluence

from src.services.vectordb_service import VectorDBService

def confluence_connection(url: str, username: str, password: str) -> Confluence:
    try:
        confluence = Confluence(url = url, username = username, password = password)
        return confluence
    except Exception as e:
        print(f"Error connecting to Confluence: {e}")
        raise e

##for empty string if the user does not provide any value for the filter, we will consider it as None and ignore that filter while building the CQL query
def _is_set(value: Any) -> bool:
    return value not in (None, "", "None")

### for quotes in the filter values, we need to escape them in the CQL query to avoid syntax errors. The _escape_cql_value function replaces double quotes with escaped double quotes.
def _escape_cql_value(value: str) -> str:
    return str(value).replace('"', r'\"')


def build_cql(filters: Dict[str, Any], default_space: str | None = None) -> str:
    """Build a Confluence CQL query dynamically from extracted filters.

    Supported keys:
      - space, type, title, text, label, labels
      - creator, contributor
      - id, parent
      - created_after, created_before
      - lastmodified_after, lastmodified_before
      - order_by
    """
    cql_parts = []

    # Optional default scope to avoid broad scans.
    if default_space and not _is_set(filters.get("space")):
        cql_parts.append(f'space = "{_escape_cql_value(default_space)}"')

    if _is_set(filters.get("space")):
        cql_parts.append(f'space = "{_escape_cql_value(filters["space"])}"')

    if _is_set(filters.get("type")):
        cql_parts.append(f'type = "{_escape_cql_value(filters["type"])}"')

    if _is_set(filters.get("title")):
        cql_parts.append(f'title ~ "{_escape_cql_value(filters["title"])}"')

    if _is_set(filters.get("text")):
        cql_parts.append(f'text ~ "{_escape_cql_value(filters["text"])}"')

    if _is_set(filters.get("label")):
        cql_parts.append(f'label = "{_escape_cql_value(filters["label"])}"')

    if _is_set(filters.get("labels")):
        labels = filters.get("labels")
        if isinstance(labels, list):
            escaped = ",".join(f'"{_escape_cql_value(label)}"' for label in labels if _is_set(label))
            if escaped:
                cql_parts.append(f"label in ({escaped})")
        else:
            cql_parts.append(f'label = "{_escape_cql_value(labels)}"')

    if _is_set(filters.get("creator")):
        cql_parts.append(f'creator = "{_escape_cql_value(filters["creator"])}"')

    if _is_set(filters.get("contributor")):
        cql_parts.append(f'contributor = "{_escape_cql_value(filters["contributor"])}"')

    if _is_set(filters.get("id")):
        cql_parts.append(f'id = "{_escape_cql_value(filters["id"])}"')

    if _is_set(filters.get("parent")):
        cql_parts.append(f'parent = "{_escape_cql_value(filters["parent"])}"')

    if _is_set(filters.get("created_after")):
        cql_parts.append(f'created >= "{_escape_cql_value(filters["created_after"])}"')

    if _is_set(filters.get("created_before")):
        cql_parts.append(f'created <= "{_escape_cql_value(filters["created_before"])}"')

    if _is_set(filters.get("lastmodified_after")):
        cql_parts.append(f'lastmodified >= "{_escape_cql_value(filters["lastmodified_after"])}"')

    if _is_set(filters.get("lastmodified_before")):
        cql_parts.append(f'lastmodified <= "{_escape_cql_value(filters["lastmodified_before"])}"')

    cql_final = " AND ".join(cql_parts) if cql_parts else 'type = "page"'

    order_by = filters.get("order_by")
    if _is_set(order_by):
        cql_final = f"{cql_final} ORDER BY {order_by}"

    return cql_final

@tool("Confluence Fetcher")
def confluence_document_fetcher(filters: ConfluenceDocumentFilter, url: str = None, username: str = None, password: str = None) -> List[Dict]:
    """Example tool to fetch documents from Confluence based on filters created"""
    "We are taking the user input -> validate against pydantic model -> then to typed model -> then convert back to dictionary -> this removes values without any values ie: None or empty then we pass to build_cql"
    if isinstance(filters, ConfluenceDocumentFilter):
        filters = ConfluenceDocumentFilter(**filters)
        ## using model_dump to convert the pydantic model to a dictionary and then filtering out the None values to pass only the set filters to the build_cql function
        filters_dictionary = filters.model_dump(exclude_none=True)

        if not filters_dictionary:
            ##insert logger at last after implementation
            print(f'No valid filters provided.skipping call')
            return []
        if not url or not username or not password:
            ## insert logger at last after implementation
            print(f'Missing Confluence credentials. Please provide url, username and password.')
            return []
        ###inset logger for the confirmation of connection to confluence at last after implementation
        print(f'Connecting to Confluence at {url} with user {username}')

        try:
            confluence = confluence_connection(url,username,password)
            cql_query = build_cql(filters_dictionary); 
            print(f"cql build successful: {cql_query}")

            ##Instead of this function we can use the meta_data to fetch the document and then use the document_id to fetch the content of the document and then return the content as part of the response. This way we can avoid fetching the content of all the documents in the search result and only fetch the content of the relevant documents based on the top_k value provided by the user.


            # add fields here one by one as per the requirement and the response from the confluence.cql function
            results = confluence.cql(cql=cql_query, start=0, limit=10, expand="content.space,content.version")
            # Adjust limit as needed

            ##meta-data + the CQL ,for fetching from the vector database
            
            confluence_metadata = [
                {
                    "source": "confluence",
                    "document_id": (result.get("content", {}) or {}).get("id") or result.get("id"),
                    "title": (result.get("content", {}) or {}).get("title") or result.get("title", ""),
                    "content_type": (result.get("content", {}) or {}).get("type") or result.get("type", "page"),
                    "space_key": ((result.get("content", {}) or {}).get("space", {}) or {}).get("key"),
                    "space_name": ((result.get("content", {}) or {}).get("space", {}) or {}).get("name"),
                    "status": result.get("status") or (result.get("content", {}) or {}).get("status"),
                    "updated_at": ((result.get("content", {}) or {}).get("version", {}) or {}).get("when"),
                    "version": ((result.get("content", {}) or {}).get("version", {}) or {}).get("number"),
                    "created_by": (((result.get("content", {}) or {}).get("version", {}) or {}).get("by", {}) or {}).get("displayName"),
                    "url": ((result.get("content", {}) or {}).get("_links", {}) or {}).get("webui") or result.get("url"),
                }
                for result in results
            ]
            return confluence_metadata 

        except Exception as e:
            print(f'Failed to connect to Confluence: {e}')
            return []
        
##Two step narrowing for fetching the appropriate document from confluence based on the user's query
@tool("Similar Documents Fetcher")
def similar_documents_fetcher(query:str, no_of_documents: int = 5,space_key: str = None) -> str :
    """
    Example tool to fetch similar documents from Confluence based on the user's query and the space key provided and on historical data
    """
    try:
        print(f'Fetching similar documents for query: {query} from space: {space_key}')

        
        ###Initialzing the VectorDB service
        ###ChromaDB - Post initialize Chroma config in vectorDB layer
        vector_db_instance = VectorDBService(persistent_directory="./chroma_db") 
        
        filter = {}
        if space_key:
            filter["space_key"] = space_key
        
        ##Searching for similar documents in the vector database based on the query and the filter provided
        
        similar_documents = vector_db_instance.search_similar_onboarding_documents(
            query=query,
            filters=filter if filter else None,
            n_results=no_of_documents
        )

        if not similar_documents:
            return "No similar documents found for the query."
        top_relevant_document = similar_documents[0]
        metadata = top_relevant_document["metadata"]

        ##Normal formatting of the response for the agent to consume and use as context for the conversation
        response_part = ["\n" + "="*60]
        response_part.append("Similar Document Found")
        response_part.append("="*60+"\n")

        ##Displaying the metadata of the document in the response
        response_part.append(f"Document ID: {metadata.get('Document ID','N/A')}")
        response_part.append(f"Title: {metadata.get('Title','N/A')}")
        response_part.append(f"Role Description: {metadata.get('Role Description','N/A')}")
        response_part.append(f"Department: {metadata.get('Department','N/A')}")
        response_part.append(f"Location: {metadata.get('Location','N/A')}")
        response_part.append(f"Role: {metadata.get('Role','N/A')}")
        response_part.append(f"Team: {metadata.get('Team','N/A')}")

        ##Assuming the document content is also stored in the vector database along with the metadata, we can fetch the content and include it in the response as well.
        document = top_relevant_document.get("Document","")
        ##Check issue in Document
        if "Role Description" in document:
            role_description = document.split("Role Description:")[1].strip()
            response_part.append(f"\nRole Description: {role_description}")

        response_part.append("\n"+"="*60)
        print(f"Returning the most similar document for the query: {query} with metadata: {metadata}")
        return "\n".join(response_part)
    except Exception as e:
        print(f'Failed to fetch similar documents: {e}')
        return "An error occurred while fetching similar documents."