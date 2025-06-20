import os
import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

def main():
    load_dotenv()
    DOCKERHUB_USERNAME = os.getenv("DOCKERHUB_USERNAME")
    DOCKERHUB_TOKEN = os.getenv("DOCKERHUB_TOKEN")
    BASE_URL = "https://hub.docker.com/v2"

    mcp = FastMCP("DockerHub MCP")

    @mcp.tool()
    def list_repositories() -> dict:
        url = f"{BASE_URL}/repositories/{DOCKERHUB_USERNAME}/"
        resp = requests.get(url, auth=(DOCKERHUB_USERNAME, DOCKERHUB_TOKEN))
        resp.raise_for_status()
        return resp.json()

    @mcp.tool()
    def list_tags(repo: str) -> dict:
        url = f"{BASE_URL}/repositories/{DOCKERHUB_USERNAME}/{repo}/tags/"
        resp = requests.get(url, auth=(DOCKERHUB_USERNAME, DOCKERHUB_TOKEN))
        resp.raise_for_status()
        return resp.json()

    @mcp.tool()
    def get_manifest(repo: str, tag: str) -> dict:
        url = f"{BASE_URL}/repositories/{DOCKERHUB_USERNAME}/{repo}/manifests/{tag}/"
        resp = requests.get(url, auth=(DOCKERHUB_USERNAME, DOCKERHUB_TOKEN))
        resp.raise_for_status()
        return resp.json()

    @mcp.tool()
    def search_repositories(query: str) -> dict:
        """Search public repositories by query string."""
        url = f"{BASE_URL}/search/repositories/?query={query}"
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()

    @mcp.tool()
    def get_repository_info(repo: str) -> dict:
        """Get details about a specific repository."""
        url = f"{BASE_URL}/repositories/{DOCKERHUB_USERNAME}/{repo}/"
        resp = requests.get(url, auth=(DOCKERHUB_USERNAME, DOCKERHUB_TOKEN))
        resp.raise_for_status()
        return resp.json()

    @mcp.tool()
    def list_collaborators(repo: str) -> dict:
        """List collaborators for a repository."""
        url = f"{BASE_URL}/repositories/{DOCKERHUB_USERNAME}/{repo}/collaborators/"
        resp = requests.get(url, auth=(DOCKERHUB_USERNAME, DOCKERHUB_TOKEN))
        resp.raise_for_status()
        return resp.json()

    @mcp.tool()
    def get_user_info(username: str) -> dict:
        """Get information about a Docker Hub user."""
        url = f"{BASE_URL}/users/{username}/"
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()

    @mcp.tool()
    def delete_repository(repo: str) -> dict:
        """Delete a repository (requires appropriate permissions)."""
        url = f"{BASE_URL}/repositories/{DOCKERHUB_USERNAME}/{repo}/"
        resp = requests.delete(url, auth=(DOCKERHUB_USERNAME, DOCKERHUB_TOKEN))
        if resp.status_code == 204:
            return {"status": "deleted"}
        resp.raise_for_status()
        return resp.json()
    # Run the MCP server
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
