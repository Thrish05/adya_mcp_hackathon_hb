from fastmcp import FastMCP
import os
import requests
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP(
    name="Notion Integration Server",
    instructions="MCP server for comprehensive Notion API operations"
)

# Notion API Setup
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_VERSION = os.getenv("NOTION_VERSION", "2022-06-28")
BASE_URL = "https://api.notion.com/v1"
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json"
}

def raise_if_error(response):
    if not response.ok:
        print(f"[ERROR] {response.status_code}: {response.text}")
    response.raise_for_status()


# ------------------------ DATABASE TOOLS ------------------------

@mcp.tool
def create_database(parent_page_id: str, title: List[Dict], properties: Dict) -> Dict:
    url = f"{BASE_URL}/databases"
    payload = {
        "parent": {"type": "page_id", "page_id": parent_page_id},
        "title": title,
        "properties": properties
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    raise_if_error(response)
    return response.json()

@mcp.tool
def retrieve_database(database_id: str) -> Dict:
    url = f"{BASE_URL}/databases/{database_id}"
    response = requests.get(url, headers=HEADERS)
    raise_if_error(response)
    return response.json()

@mcp.tool
def query_database(database_id: str, filters: Optional[Dict] = None,
                   sorts: Optional[List[Dict]] = None, page_size: int = 100) -> Dict:
    url = f"{BASE_URL}/databases/{database_id}/query"
    payload = {"page_size": page_size}
    if filters:
        payload["filter"] = filters
    if sorts:
        payload["sorts"] = sorts
    response = requests.post(url, headers=HEADERS, json=payload)
    raise_if_error(response)
    return response.json()


# ------------------------ PAGE TOOLS ------------------------

@mcp.tool
def create_page(parent: Dict[str, Any], properties: Dict,
                children: Optional[List[Dict]] = None) -> Dict:
    url = f"{BASE_URL}/pages"
    payload = {"parent": parent, "properties": properties}
    if children and isinstance(children, list):
        payload["children"] = children

    if parent.get("type") == "workspace":
        payload["properties"] = {
            "title": {
                "title": [
                    {"type": "text", "text": {"content": properties["title"]}}
                ]
            }
        }

    response = requests.post(url, headers=HEADERS, json=payload)
    raise_if_error(response)
    return response.json()

@mcp.tool
def retrieve_page(page_id: str) -> Dict:
    url = f"{BASE_URL}/pages/{page_id}"
    response = requests.get(url, headers=HEADERS)
    raise_if_error(response)
    return response.json()

@mcp.tool
def update_page(page_id: str, properties: Dict) -> Dict:
    if not properties:
        raise ValueError("Missing required parameter: 'properties'")
    url = f"{BASE_URL}/pages/{page_id}"
    response = requests.patch(url, headers=HEADERS, json={"properties": properties})
    raise_if_error(response)
    return response.json()

@mcp.tool
def archive_page(page_id: str) -> Dict:
    url = f"{BASE_URL}/pages/{page_id}"
    response = requests.patch(url, headers=HEADERS, json={"archived": True})
    raise_if_error(response)
    return response.json()


# ------------------------ BLOCK TOOLS ------------------------

@mcp.tool
def append_blocks(page_id: str, blocks: List[Dict]) -> Dict:
    url = f"{BASE_URL}/blocks/{page_id}/children"
    response = requests.patch(url, headers=HEADERS, json={"children": blocks})
    raise_if_error(response)
    return response.json()

@mcp.tool
def retrieve_page_blocks(page_id: str) -> Dict:
    url = f"{BASE_URL}/blocks/{page_id}/children"
    response = requests.get(url, headers=HEADERS)
    raise_if_error(response)
    return response.json()

@mcp.tool
def update_block(block_id: str, new_text: str) -> Dict:
    url = f"{BASE_URL}/blocks/{block_id}"
    response = requests.patch(url, headers=HEADERS, json={
        "paragraph": {
            "rich_text": [{"type": "text", "text": {"content": new_text}}]
        }
    })
    raise_if_error(response)
    return response.json()

@mcp.tool
def delete_block(block_id: str) -> Dict:
    url = f"{BASE_URL}/blocks/{block_id}"
    response = requests.delete(url, headers=HEADERS)
    raise_if_error(response)
    return {"status": "deleted"}


# ------------------------ ADVANCED TOOLS ------------------------

@mcp.tool
def duplicate_page(original_page_id: str, parent: Dict[str, Any]) -> Dict:
    original = retrieve_page(original_page_id)
    blocks = retrieve_page_blocks(original_page_id)
    new_page = create_page(
        parent=parent,
        properties=original.get("properties", {}),
        children=blocks.get("results", [])
    )
    return new_page

@mcp.tool
def assign_user_property(page_id: str, field_name: str, user_id: str) -> Dict:
    url = f"{BASE_URL}/pages/{page_id}"
    payload = {
        "properties": {
            field_name: {
                "people": [{"object": "user", "id": user_id}]
            }
        }
    }
    response = requests.patch(url, headers=HEADERS, json=payload)
    raise_if_error(response)
    return response.json()

@mcp.tool
def extract_page_summary(page_id: str) -> str:
    blocks = retrieve_page_blocks(page_id)
    content = []
    for block in blocks.get("results", []):
        if block.get("type") == "paragraph":
            texts = block.get("paragraph", {}).get("rich_text", [])
            for t in texts:
                content.append(t.get("text", {}).get("content", ""))
    return "\n".join(content)


# ------------------------ SEARCH ------------------------

@mcp.tool
def search(query: str = "", filter_dict: Optional[Dict] = None,
           sort_dict: Optional[Dict] = None, page_size: int = 100) -> Dict:
    url = f"{BASE_URL}/search"
    payload = {"query": query, "page_size": page_size}
    if filter_dict:
        payload["filter"] = filter_dict
    if sort_dict:
        payload["sort"] = sort_dict

    response = requests.post(url, headers=HEADERS, json=payload)
    raise_if_error(response)
    return response.json()


# ------------------------ RUN MCP ------------------------

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
