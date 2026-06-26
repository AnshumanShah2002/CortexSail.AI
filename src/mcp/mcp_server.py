from mcp.server.fastmcp import FastMCP
from src.services.confluence_service_layer import ConfluenceService
from src.services.vectordb_service import VectorDBService
from typing import List, Dict, Optional
mcp = FastMCP("CortexTools - MCP server tools for tool based agents")

##Tools for Confluence service layer
##check if agents require a return value or not, if not then return an empty Dict
@mcp.tool()
def health_check_confluence_tool() -> Dict:
    """
    Agent Method - Health check for the confluence service layer, this tool will be used by the agent to check if the confluence service is up and running
    """
    try:
        status = ConfluenceService().health_check()
        return {
            "success": True,
            "service": "confluence",
            "status": status
        }
    except Exception as e:
        return {
            "success": False,
            "service": "confluence",
            "error": str(e)
        }

@mcp.tool()
def health_check_vector_db_service_tool() -> Dict:
    """
    Agent Method - Health check for the vector db service layer, this tool will be used by the agent to check if the vector db service" is up and running
    """
    try:
        vectorstatus = VectorDBService().get_collection_details()
        return {
          "success": True,
          "service": "vector_db",
          "status": vectorstatus
        }
    except Exception as e:
        return {
            "success": False,
            "service": "vector_db",
            "error": str(e)
        }

## user_prompt function: Extract session credentials, Initialize/check crew manager, Initialize conversation memory, Fetch conversation context, Get crew instance, Build LLM inputs, Execute crew kickoff, Extract output, Validate output, Parse task outputs, Store in memory, Return response, Handle errors
@mcp.tool()
def analyze_user_query_prompt(query: str) -> Dict:
    """
    Agent Method - Analyze the user query prompt and return the intent of the query, this tool will be used by the agent to analyze the user query and determine the intent of the query
    """
    if not query or not query.strip():
            return {
                "success": False,
                "service": "confluence",
                "output": "",
                "message": "Query is empty or invalid"
            }    
    try:
        #Keeping the success param as bool if the success comes as True, else default is False
        result = ConfluenceService().user_prompt(query.strip())
        ##This response is only for the agent that is calling the agent not for all the services like rest / UI binding
        return {
            "success": bool(result.get("success", False)),
            "service": "confluence",
            "output": result.get("output", ""),
            "message": result.get("message", "")
        }
    except Exception as e:
        return {
            "success": False,
            "service": "confluence",
            "output": "",
            "message": "Tool execution failed with error: " + str(e)
        }

@mcp.tool()
def produce_word_document_from_markdown_tool(markdown_content: str, session_id: str) -> Dict:
    """
    Agent Method - Generate a word document from markdown content and return the word file or the path URL, this tool will be used by the agent to generate a word document from markdown content"""

    if not markdown_content or not markdown_content.strip():
        return {
            "success": False,
            "service" : "confluence",
            "output": "",
            "message": "Markdown content is empty or invalid"
        }
    #change session id upon implementing the auth and session_id management for the agent, for now it is a default session id
    if not session_id or not session_id.strip():
        session_id = "default_session"
    try:
        result = ConfluenceService().produce_word_document_from_markdown(markdown_content.strip(), session_id.strip())
        return {
            "success": bool(result.get("success", False)),
            "service": "confluence",
            "filepath": result.get("output", ""),
            "filename": result.get("filename", ""),
            "message": result.get("message", "")
        }
    except Exception as e:
        return {
            "success": False,
            "service": "confluence",
            "filepath": "",
            "filename": "",
            "message": "Tool execution failed with error: " + str(e)
        }

###Tools for VectorDB service 
@mcp.tool()
def search_similar_onboarding_documents_tool(query: str, top_k: int = 5, filters: Optional[Dict] = None) -> List[Dict]:
    """
    Agent Method - Search for similar onboarding documents based on the user query, this tool will be used by the agent to search for similar onboarding documents based on the user query
    """

    if not query or not query.strip():
        return {
            "success": False,
            "service": "vector_db",
            "results": [],
            "count": 0,
            "output": [],
            "message": "Query is empty or invalid"
        }
    ##Its appropriate for the agent to recieve a list of Dicts as the output for the search results, so that it can process the results and use them for further processing
    try:
        results = VectorDBService().search_similar_onboarding_documents(query.strip(), top_k, filters)
        return {
            "success": True,
            "service": "vector_db",
            "results": results,
            "count": len(results),
            "message": f"Found {len(results)} similar onboarding documents."
        }
    except Exception as e:
        return {
            "success": False,
            "service": "vector_db",
            "results": [],
            "count": 0,
            "message": "Tool execution failed with error: " + str(e)
        }
@mcp.tool()
def get_collection_details_tool() -> Dict:
    """
    Agent Method - Get the details of the collection in the vector db service, this tool will be used by the agent to get the details of the collection in the vector db service
    """
    try:
        collection_details = VectorDBService().get_collection_details()
        return {
            "success": True,
            "service": "vector_db",
            "collection_details": collection_details,
            "message": "Collection details fetched successfully."
        }
    except Exception as e:
        return {
            "success": False,
            "service": "vector_db",
            "collection_details": {},
            "message": "Tool execution failed with error: " + str(e)
        }
    
##Adding a protection flag of False so that the db is not cleared by accident, the agent has to explicitly set the confirm flag to True to clear the db - Fix this as no parameter if the clear db is not working
@mcp.tool()
def clear_complete_collection_tool(confirm: bool = False) -> Dict:
    """
    Agent Method - Clear the complete collection in the vector db service, this tool will be used by the agent to clear the complete collection in the vector db service
    """

    if not confirm:
        return {
            "success": False,
            "service": "vector_db",
            "message": "Confirmation flag not set. Set confirm=True to clear the collection."
        }

    try:
        ##Nothing to capture in the return value, just a success message is enough for the agent to know that the collection has been cleared
        VectorDBService().clear_complete_collection()
        return {
            "success": True,
            "service": "vector_db",
            "message": "VectorDB collection cleared successfully."
        }
    except Exception as e:
        return {
            "success": False,
            "service": "vector_db",
            "message": "Tool execution failed with error: " + str(e)
        }

@mcp.tool()
def upload_csv_content_tool(csv_file_path: str) -> Dict:
    """
    Agent Method - Upload CSV content to the vector db service, this tool will be used by the agent to upload CSV content to the vector db service
    """
    if not csv_file_path or not csv_file_path.strip():
        return {
            "success": False,
            "service": "vector_db",
            "message": "CSV file path is empty or invalid"
        }
    try:
        VectorDBService().upload_csv_content(csv_file_path.strip())
        return {
            "success": True,
            "service": "vector_db",
            "filepath": csv_file_path.strip(),
            "message": "CSV content uploaded successfully."
        }   
    except Exception as e:
        return {
            "success": False,
            "service": "vector_db",
            "filepath": csv_file_path.strip(),
            "message": "Tool execution failed with error: " + str(e)
        }

if __name__ == "__main__":
    mcp.run(transport="sse")
    print("MCP server is up and runnning")