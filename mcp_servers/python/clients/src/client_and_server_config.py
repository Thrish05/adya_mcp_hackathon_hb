ClientsConfig =[
    "MCP_CLIENT_AZURE_AI",
    "MCP_CLIENT_OPENAI",
	"MCP_CLIENT_GEMINI"
]
ServersConfig = [
	{
		"server_name": "MCP-GSUITE",
		"command":"uv",
		"args": [
			"--directory",
			"../servers/MCP-GSUITE/mcp-gsuite",
			"run",
			"mcp-gsuite"
		]
	},
	{
		"server_name": "DOCKERHUB",
		"command":"uv",
		"args": [
			"--directory",
			"../servers/DOCKERHUB/mcp-dockerhub",
			"run",
			"mcp-dockerhub"
		]
	},{
		"server_name": "DATAROBOT",
		"command":"uv",
		"args": [
			"--directory",
			"../servers/DATAROBOT/mcp-datarobot",
			"run",
			"mcp-datarobot"
		]
	},{
		"server_name": "CUSTOM",
		"command":"uv",
		"args": [
			"--directory",
			"../servers/CUSTOM/mcp-custom",
			"run",
			"mcp-custom"
		]
	},
  {
    "server_name": "QUICKBOOKS_ONLINE_MCP",
    "command": "../servers/QUICKBOOKS_ONLINE_MCP/venv/Scripts/python.exe",
    "args": [
        "../servers/QUICKBOOKS_ONLINE_MCP/server.py"
    ]
}
]