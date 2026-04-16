from mcp.server.fastmcp import FastMCP
mcp = FastMCP("CortexTools - MCP server tools for tool based agents")

@mcp.tool()
def example_addition(a: int, b: int) -> int:
    """
    Here creating the tools as a function in the mcp server
    This tool adds two integers and returns the result.
    """
    

if __name__ == "__main__":
    mcp.run(transport="sse")
    print("MCP server is up and runnning")