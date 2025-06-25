from fastmcp import FastMCP
import os
import requests
from typing import List, Dict, Any, Optional, Union
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP(
    name="Dart API MCP Server",
    instructions="MCP server for Dart task, doc, and project management API"
)

# Helper function to get API key
def get_api_key(server_credentials: dict) -> str:
    """Get API key from server_credentials or environment"""
    # Priority 1: Credentials from request
    if server_credentials and "api_key" in server_credentials:
        return server_credentials["api_key"]
    
    # Priority 2: Environment variable
    env_key = os.getenv("DART_API_KEY")
    if env_key:
        return env_key
        
    raise ValueError("No Dart API key provided")

# Generic request function
def dart_request(server_credentials: dict, method: str, endpoint: str, **kwargs):
    """Make authenticated request to Dart API"""
    api_key = get_api_key(server_credentials)
    url = f"https://app.itsdart.com/api/v0/public/{endpoint}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    response = requests.request(method, url, headers=headers, **kwargs)
    response.raise_for_status()
    return response

# Comments Endpoints
@mcp.tool()
def create_comment(server_credentials: dict, item: Dict[str, Any]) -> Dict:
    """
    Create a new comment
    Args:
        item: CommentCreate object with taskId and text
    """
    return dart_request(server_credentials, "POST", "comments", json={"item": item}).json()

@mcp.tool()
def list_comments(server_credentials: dict, task_id: str, author: Optional[str] = None, 
                 limit: Optional[int] = None, offset: Optional[int] = None) -> Dict:
    """
    List comments with filters
    Args:
        task_id: Filter by task ID (required)
        author: Filter by author name
        limit: Number of results per page
        offset: Initial index for pagination
    """
    params = {"task_id": task_id}
    if author: params["author"] = author
    if limit: params["limit"] = limit
    if offset: params["offset"] = offset
    return dart_request(server_credentials, "GET", "comments/list", params=params).json()

# Config Endpoints
@mcp.tool() 
def get_config(server_credentials: dict) -> Dict:
    """Get user space configuration"""
    return dart_request(server_credentials, "GET", "config").json()

# Dartboards Endpoints
@mcp.tool()
def get_dartboard(server_credentials: dict, dartboard_id: str) -> Dict:
    """Retrieve a dartboard by ID"""
    return dart_request(server_credentials, "GET", f"dartboards/{dartboard_id}").json()

# Docs Endpoints
@mcp.tool()
def create_doc(server_credentials: dict, item: Dict[str, Any]) -> Dict:
    """
    Create a new doc
    Args:
        item: DocCreate object with title and text
    """
    return dart_request(server_credentials, "POST", "docs", json={"item": item}).json()

@mcp.tool()
def get_doc(server_credentials: dict, doc_id: str) -> Dict:
    """Retrieve a doc by ID"""
    return dart_request(server_credentials, "GET", f"docs/{doc_id}").json()

@mcp.tool()
def update_doc(server_credentials: dict, doc_id: str, item: Dict[str, Any]) -> Dict:
    """
    Update a doc
    Args:
        doc_id: ID of doc to update
        item: DocUpdate object with properties to update
    """
    return dart_request(server_credentials, "PUT", f"docs/{doc_id}", json={"item": item}).json()

@mcp.tool()
def delete_doc(server_credentials: dict, doc_id: str) -> Dict:
    """Delete a doc by ID"""
    return dart_request(server_credentials, "DELETE", f"docs/{doc_id}").json()

@mcp.tool()
def list_docs(server_credentials: dict, folder: Optional[str] = None, title: Optional[str] = None, 
             limit: Optional[int] = None, offset: Optional[int] = None) -> Dict:
    """
    List docs with filters
    Args:
        folder: Filter by folder name
        title: Search by title
        limit: Number of results per page
        offset: Initial index for pagination
    """
    params = {}
    if folder: params["folder"] = folder
    if title: params["title"] = title
    if limit: params["limit"] = limit
    if offset: params["offset"] = offset
    return dart_request(server_credentials, "GET", "docs/list", params=params).json()

# Folders Endpoints
@mcp.tool() 
def get_folder(server_credentials: dict, folder_id: str) -> Dict:
    """Retrieve a folder by ID"""
    return dart_request(server_credentials, "GET", f"folders/{folder_id}").json()

# Tasks Endpoints
@mcp.tool()
def create_task(server_credentials: dict, item: Dict[str, Any]) -> Dict:
    """
    Create a new task
    Args:
        item: TaskCreate object with title and description
    """
    return dart_request(server_credentials, "POST", "tasks", json={"item": item}).json()

@mcp.tool()
def get_task(server_credentials: dict, task_id: str) -> Dict:
    """Retrieve a task by ID"""
    return dart_request(server_credentials, "GET", f"tasks/{task_id}").json()

@mcp.tool()
def update_task(server_credentials: dict, task_id: str, item: Dict[str, Any]) -> Dict:
    """
    Update a task
    Args:
        task_id: ID of task to update
        item: TaskUpdate object with properties to update
    """
    return dart_request(server_credentials, "PUT", f"tasks/{task_id}", json={"item": item}).json()

@mcp.tool()
def delete_task(server_credentials: dict, task_id: str) -> Dict:
    """Delete a task by ID"""
    return dart_request(server_credentials, "DELETE", f"tasks/{task_id}").json()

@mcp.tool()
def list_tasks(server_credentials: dict, assignee: Optional[str] = None, status: Optional[str] = None, 
              limit: Optional[int] = None, offset: Optional[int] = None) -> Dict:
    """
    List tasks with filters
    Args:
        assignee: Filter by assignee name
        status: Filter by status
        limit: Number of results per page
        offset: Initial index for pagination
    """
    params = {}
    if assignee: params["assignee"] = assignee
    if status: params["status"] = status
    if limit: params["limit"] = limit
    if offset: params["offset"] = offset
    return dart_request(server_credentials, "GET", "tasks/list", params=params).json()

# Views Endpoints
@mcp.tool()
def get_view(server_credentials: dict, view_id: str) -> Dict:
    """Retrieve a view by ID"""
    return dart_request(server_credentials, "GET", f"views/{view_id}").json()

def main():
    print("Dart API MCP Server running...")
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
