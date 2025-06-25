import os
import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from typing import Dict, List, Optional

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
