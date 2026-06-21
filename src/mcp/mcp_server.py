from mcp.server.fastmcp import FastMCP
from src.services.confluence_service_layer import ConfluenceService
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

if __name__ == "__main__":
    mcp.run(transport="sse")
    print("MCP server is up and runnning")