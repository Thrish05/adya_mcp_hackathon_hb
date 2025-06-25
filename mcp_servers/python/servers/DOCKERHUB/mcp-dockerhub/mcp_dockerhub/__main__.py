import os
import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from typing import Dict, List, Optional
from dotenv import set_key

load_dotenv()

DOCKERHUB_TOKEN = os.getenv("DOCKERHUB_TOKEN")
BASE_URL = "https://hub.docker.com/v2"

def validate_token(username, token):
    url = f"{BASE_URL}/repositories/{username}/"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    return response.status_code == 200

if not DOCKERHUB_TOKEN:
    # Prompt user for credentials (do this securely in production)
    username = os.getenv("DOCKERHUB_USERNAME")
    password = os.getenv("DOCKERHUB_PASS")
    login_url = f"{BASE_URL}/users/login/"
    response = requests.post(login_url, json={"username": username, "password": password})
    jwt_token = response.json().get('token')
    pat_url = f"{BASE_URL}/access-tokens"
    headers = {"Authorization": f"Bearer {jwt_token}"}
    pat_data = {
        "token_label": "MCP Server Token",
        "scopes": ["repo:admin", "repo:write", "repo:read"]
    }
    response = requests.post(pat_url, headers=headers, json=pat_data)
    new_token = response.json().get('token')
    DOCKERHUB_TOKEN = new_token
    set_key('.env', "DOCKERHUB_TOKEN", new_token)

def main():
    load_dotenv()
    mcp = FastMCP("DockerHub MCP")
    
    # Helper function to get credentials
    def get_dockerhub_creds(server_credentials: dict) -> Dict[str, str]:
        """Extract DockerHub credentials from server_credentials"""
        creds = {
            "username": server_credentials.get("username") or os.getenv("DOCKERHUB_USERNAME"),
            "token": server_credentials.get("token") or os.getenv("DOCKERHUB_TOKEN")
        }
        if not creds["username"] or not creds["token"]:
            raise ValueError("Missing DockerHub credentials")
        return creds

    @mcp.tool()
    def list_my_repositories(server_credentials: dict) -> dict:
        """List my repositories"""
        creds = get_dockerhub_creds(server_credentials)
        user = creds["username"]
        url = f"https://hub.docker.com/v2/repositories/{user}/"
        resp = requests.get(url, auth=(creds["username"], creds["token"]))
        resp.raise_for_status()
        return resp.json()

    @mcp.tool()
    def list_repositories(server_credentials: dict, username: Optional[str] = None) -> dict:
        """List repositories for a user"""
        creds = get_dockerhub_creds(server_credentials)
        user = username or creds["username"]
        url = f"https://hub.docker.com/v2/repositories/{user}/"
        resp = requests.get(url, auth=(creds["username"], creds["token"]))
        resp.raise_for_status()
        return resp.json()
    
    @mcp.tool()
    def list_tags(server_credentials: dict, repo: str, username: Optional[str] = None) -> dict:
        """List tags for a repository"""
        creds = get_dockerhub_creds(server_credentials)
        user = username or creds["username"]
        url = f"https://hub.docker.com/v2/repositories/{user}/{repo}/tags/"
        resp = requests.get(url, auth=(creds["username"], creds["token"]))
        resp.raise_for_status()
        return resp.json()


    @mcp.tool()
    def search_repositories(query: str) -> dict:
        """Search public repositories by query string"""
        url = f"https://hub.docker.com/v2/search/repositories/?query={query}"
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()

    @mcp.tool()
    def get_repository_info(server_credentials: dict, repo: str, username: Optional[str] = None) -> dict:
        """Get details about a specific repository"""
        creds = get_dockerhub_creds(server_credentials)
        user = username or creds["username"]
        url = f"https://hub.docker.com/v2/repositories/{user}/{repo}/"
        resp = requests.get(url, auth=(creds["username"], creds["token"]))
        resp.raise_for_status()
        return resp.json()

    @mcp.tool()
    def list_collaborators(server_credentials: dict, repo: str, username: Optional[str] = None) -> dict:
        """List collaborators for a repository"""
        creds = get_dockerhub_creds(server_credentials)
        user = username or creds["username"]
        url = f"https://hub.docker.com/v2/repositories/{user}/{repo}/collaborators/"
        resp = requests.get(url, auth=(creds["username"], creds["token"]))
        resp.raise_for_status()
        return resp.json()

    @mcp.tool()
    def get_user_info(username: str) -> dict:
        """Get information about a Docker Hub user"""
        url = f"https://hub.docker.com/v2/users/{username}/"
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()

    # Run the MCP server
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
