from typing import Dict, Any, Callable, Optional

from src.server_connection import MCPServers
from src.client_and_server_config import ServersConfig, ClientsConfig


async def client_and_server_validation(payload: Dict[str, Any], streaming_callback: Optional[Callable] = None):
    try:
        selected_server_credentials = payload.get("selected_server_credentials")
        client_details = payload.get("client_details", {})
        selected_client = payload.get("selected_client", "")
        selected_servers = payload.get("selected_servers", [])

        # Debug prints
        print(f"DEBUG: VALIDATION - selected_server_credentials: {selected_server_credentials}")
        print(f"DEBUG: VALIDATION - selected_server_credentials type: {type(selected_server_credentials)}")
        print(f"DEBUG: VALIDATION - selected_servers: {selected_servers}")
        print(f"DEBUG: VALIDATION - selected_client: {selected_client}")

        if not selected_client or not selected_servers or not selected_server_credentials or not client_details:
            print("Invalid Request Payload")
            return {
                "payload": None,
                "error": "Invalid Request Payload",
                "status": False
            }

        for server in selected_servers:
            if server not in MCPServers:
                print("Invalid Server")
                return {
                    "payload": None,
                    "error": "Invalid Server",
                    "status": False
                }

        if selected_client not in ClientsConfig:
            print("Invalid Client")
            return {
                "payload": None,
                "error": "Invalid Client",
                "status": False
            }

        tools_arr = []
        for server in selected_servers:
   
            resource = await MCPServers[server].list_tools()
            if resource:
                for tool in resource.tools:
                    # Debug the tool object to understand its structure
                    print(f"DEBUG: Tool {tool.name} attributes: {dir(tool)}")
                    print(f"DEBUG: Tool {tool.name} inputSchema: {getattr(tool, 'inputSchema', 'NOT_FOUND')}")
                    print(f"DEBUG: Tool {tool.name} parameters: {getattr(tool, 'parameters', 'NOT_FOUND')}")
                    print(f"DEBUG: Tool {tool.name} __dict__: {getattr(tool, '__dict__', 'NO_DICT')}")
                    
                    # Try different ways to access the schema
                    schema = None
                    if hasattr(tool, 'inputSchema') and tool.inputSchema:
                        schema = tool.inputSchema
                    elif hasattr(tool, 'parameters') and tool.parameters:
                        schema = tool.parameters
                    elif hasattr(tool, '__dict__') and tool.__dict__:
                        # Look for schema in the tool's dictionary
                        for key, value in tool.__dict__.items():
                            if 'schema' in key.lower() or 'param' in key.lower():
                                print(f"DEBUG: Found potential schema in {key}: {value}")
                                if isinstance(value, dict) and 'properties' in value:
                                    schema = value
                                    break
                    else:
                        # Fallback to empty schema
                        schema = {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    
                    # Ensure server_credentials parameter is included in the schema
                    if schema and isinstance(schema, dict):
                        if 'properties' not in schema:
                            schema['properties'] = {}
                        if 'server_credentials' not in schema['properties']:
                            schema['properties']['server_credentials'] = {
                                "type": "object",
                                "description": "Server credentials (automatically provided)"
                            }
                        if 'required' not in schema:
                            schema['required'] = []
                        if 'server_credentials' not in schema['required']:
                            schema['required'].append('server_credentials')
                    
                    tool_dict = {
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": getattr(tool, "description", f"Tool for {tool.name}"),
                            "parameters": schema
                        }
                    }
                    tools_arr.append(tool_dict)

        client_details["tools"] = tools_arr

        final_payload = {
            "selected_client": selected_client,
            "selected_servers": selected_servers,
            "selected_server_credentials": selected_server_credentials,
            "client_details": client_details
        }
        
        print(f"DEBUG: VALIDATION - Final payload keys: {list(final_payload.keys())}")
        print(f"DEBUG: VALIDATION - Final selected_server_credentials: {final_payload['selected_server_credentials']}")

        return {
            "payload": final_payload,
            "error": None,
            "status": True
        }

    except Exception as err:
        print("Error initializing MCP ==========>>>>", err)
        return {
            "payload": None,
            "error": str(err),
            "status": False
        }
