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
			"../servers/DATAROBOT/mcp_datarobot",
			"run",
			"mcp-datarobot"
		]
	},{
		"server_name": "NOTION",
		"command":"uv",
		"args": [
			"--directory",
			"../servers/NOTION/mcp-notion",
			"run",
			"mcp-notion"
		]
	},
{
		"server_name": "QUICKBOOKS",
		"command":"uv",
		"args": [
			"--directory",
			"../servers/QUICKBOOKS/mcp_quickbooks",
			"run",
			"mcp-quickbooks"
		]
	},
	{
		"server_name": "DART",
		"command":"uv",
		"args": [
			"--directory",
			"../servers/DART/mcp_dart",
			"run",
			"mcp-dart"
		]
	}
]