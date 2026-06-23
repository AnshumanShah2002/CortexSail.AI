from mcp.server.fastmcp import FastMCP
from src.services.confluence_service_layer import ConfluenceService
from src.services.vectordb_service import VectorDBService
mcp = FastMCP("CortexTools - MCP server tools for tool based agents")


##check if agents require a return value or not, if not then return an empty dict
@mcp.tool()
def health_check_confluence_tool() -> dict:
    """
    Health check for the confluence service layer, this tool will be used by the agent to check if the confluence service is up and running
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
def health_check_vector_db_service_tool() -> dict:
    """
    Health check for the vector db service layer, this tool will be used by the agent to check if the vector db service" is up and running
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
def analyze_user_query_prompt(query: str) -> dict:
    """
    Analyze the user query prompt and return the intent of the query, this tool will be used by the agent to analyze the user query and determine the intent of the query
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
def produce_word_document_from_markdown_tool(markdown_content: str, session_id: str) -> dict:
    """
    Generate a word document from markdown content and return the word file or the path URL, this tool will be used by the agent to generate a word document from markdown content"""

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

if __name__ == "__main__":
    mcp.run(transport="sse")
    print("MCP server is up and runnning")