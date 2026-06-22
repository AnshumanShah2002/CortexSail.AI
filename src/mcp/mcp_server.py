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

if __name__ == "__main__":
    mcp.run(transport="sse")
    print("MCP server is up and runnning")