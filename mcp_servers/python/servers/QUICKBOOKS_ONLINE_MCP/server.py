# server.py

import os
from mcp.server.fastmcp import FastMCP
import tools  # Import the module to access the `tools` list

# Ensure .env is loaded for server environment
from dotenv import load_dotenv
load_dotenv()

# Create FastMCP instance
mcp = FastMCP("QuickBooks-MCP")

# Register each tool explicitly
mcp.tool()(tools.get_quickbooks_customers)
mcp.tool()(tools.get_quickbooks_invoices)
mcp.tool()(tools.create_quickbooks_customer)
mcp.tool()(tools.get_quickbooks_customer_by_id)
mcp.tool()(tools.create_quickbooks_invoice)
mcp.tool()(tools.update_quickbooks_invoice)
mcp.tool()(tools.delete_quickbooks_invoice)

print("Registered tools:")
for tool in mcp._tool_manager.list_tools():
    print("-", tool.name)

# Run the server
if __name__ == "__main__":
    mcp.run()
