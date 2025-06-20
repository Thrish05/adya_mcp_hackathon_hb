import os
import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
import json

def main():
    load_dotenv()
    DATAROBOT_API_TOKEN = os.getenv("DATAROBOT_API_TOKEN")
    DATAROBOT_ENDPOINT = os.getenv("DATAROBOT_ENDPOINT", "https://app.datarobot.com/api/v2")
    PREDICTION_SERVER_ID = os.getenv("PREDICTION_SERVER_ID")
    HEADERS = {
        "Authorization": f"Bearer {DATAROBOT_API_TOKEN}"
    }

    mcp = FastMCP("DataRobot MCP")

    @mcp.tool()
    def list_projects() -> dict:
        """List all DataRobot projects."""
        url = f"{DATAROBOT_ENDPOINT}/projects/"
        resp = requests.get(url, headers=HEADERS)
        resp.raise_for_status()
        return resp.json()

    @mcp.tool()
    def create_project(file_path: str, project_name: str = None) -> dict:
        """Create a new DataRobot project by uploading a dataset (CSV)."""
        try:
            # Verify file existence first
            if not os.path.isfile(file_path):
                return {
                    "success": False,
                    "error": "File not found",
                    "details": f"No file at {file_path}"
                }

            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {"projectName": project_name} if project_name else {}
                
                resp = requests.post(
                    f"{DATAROBOT_ENDPOINT}/projects/",
                    headers=HEADERS,
                    files=files,
                    data=data
                )

                # Handle successful responses with potential warnings
                if resp.status_code in (200, 201):
                    try:
                        response_data = resp.json()
                        return {
                            "success": True,
                            "project_id": response_data.get("id"),
                            "warnings": response_data.get("warnings", []),
                            "message": "Project created successfully"
                        }
                    except json.JSONDecodeError:
                        return {
                            "success": True,
                            "project_id": resp.headers.get('Location', '').split('/')[-1],
                            "message": "Project created with non-JSON response"
                        }

                # Handle error responses
                try:
                    error_data = resp.json()
                    return {
                        "success": False,
                        "error": error_data.get("message", "Unknown error"),
                        "status_code": resp.status_code
                    }
                except json.JSONDecodeError:
                    return {
                        "success": False,
                        "error": f"HTTP Error {resp.status_code}",
                        "response_text": resp.text[:200]  # Show first 200 chars for debugging
                    }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "type": type(e).__name__
            }

    @mcp.tool()
    def set_target_and_start_training(project_id: str, target: str) -> dict:
        headers = {
            "Authorization": f"Bearer {DATAROBOT_API_TOKEN}",
            "Content-Type": "application/json"
        }

        response = requests.patch(
            f"{DATAROBOT_ENDPOINT}/projects/{project_id}/aim",
            headers=HEADERS,
            json={"target": target}
        )
        
        return {"status": "Model training started", "project_id": project_id}
    
    @mcp.tool()
    def get_status_of_project(project_id: str) -> dict:
        headers = {
            "Authorization": f"Bearer {DATAROBOT_API_TOKEN}"
        }

        response = requests.get(
            f"{DATAROBOT_ENDPOINT}/projects/{project_id}/status",
            headers=HEADERS
        )
        response.raise_for_status()
        return {"status": "Project Status Obtained", 
                "project_id": project_id,
                "Autopilot Done": response.json()["autopilotDone"],
                "Stage Description": response.json()["stageDescription"],
                "Current Stage": response.json()["stage"]}

    @mcp.tool()
    def get_project_info(project_id: str) -> dict:
        """Get metadata and status for a specific project."""
        url = f"{DATAROBOT_ENDPOINT}/projects/{project_id}/"
        resp = requests.get(url, headers=HEADERS)
        resp.raise_for_status()
        return resp.json()

    @mcp.tool()
    def delete_project(project_id: str) -> dict:
        """Delete a DataRobot project."""
        url = f"{DATAROBOT_ENDPOINT}/projects/{project_id}/"
        resp = requests.delete(url, headers=HEADERS)
        resp.raise_for_status()
        return {"status": "deleted"}

    @mcp.tool()
    def list_models(project_id: str) -> dict:
        """List all models for a project."""
        url = f"{DATAROBOT_ENDPOINT}/projects/{project_id}/models/"
        resp = requests.get(url, headers=HEADERS)
        resp.raise_for_status()
        return resp.json()

    @mcp.tool()
    def get_model_info(project_id: str, model_id: str) -> dict:
        """Get details for a specific model."""
        url = f"{DATAROBOT_ENDPOINT}/projects/{project_id}/models/{model_id}/"
        resp = requests.get(url, headers=HEADERS)
        resp.raise_for_status()
        return resp.json()

    @mcp.tool()
    def list_deployments() -> dict:
        """List all active model deployments."""
        url = f"{DATAROBOT_ENDPOINT}/deployments/"
        resp = requests.get(url, headers=HEADERS)
        resp.raise_for_status()
        return resp.json()

    @mcp.tool()
    def list_datasets() -> dict:
        """List all uploaded datasets."""
        url = f"{DATAROBOT_ENDPOINT}/datasets/"
        resp = requests.get(url, headers=HEADERS)
        resp.raise_for_status()
        return resp.json()

    @mcp.tool()
    def get_dataset_info(dataset_id: str) -> dict:
        """Get metadata/statistics for a dataset."""
        url = f"{DATAROBOT_ENDPOINT}/datasets/{dataset_id}/"
        resp = requests.get(url, headers=HEADERS)
        resp.raise_for_status()
        return resp.json()

    @mcp.tool()
    def delete_dataset(dataset_id: str) -> dict:
        """Delete a dataset."""
        url = f"{DATAROBOT_ENDPOINT}/datasets/{dataset_id}/"
        resp = requests.delete(url, headers=HEADERS)
        resp.raise_for_status()
        return {"status": "deleted"}

    @mcp.tool()
    def get_deployment_info(deployment_id: str) -> dict:
        """Get deployment status and configuration."""
        url = f"{DATAROBOT_ENDPOINT}/deployments/{deployment_id}/"
        resp = requests.get(url, headers=HEADERS)
        resp.raise_for_status()
        return resp.json()

    @mcp.tool()
    def delete_deployment(deployment_id: str) -> dict:
        """Delete a deployed model."""
        url = f"{DATAROBOT_ENDPOINT}/deployments/{deployment_id}/"
        resp = requests.delete(url, headers=HEADERS)
        resp.raise_for_status()
        return {"status": "deleted"}

    @mcp.tool()
    def make_predictions(deployment_id: str, data: list) -> dict:
        """Submit data to a deployed model and get predictions (real-time)."""
        url = f"{DATAROBOT_ENDPOINT}/deployments/{deployment_id}/predictions/"
        resp = requests.post(url, headers={**HEADERS, "Content-Type": "application/json"}, json={"data": data})
        resp.raise_for_status()
        return resp.json()

    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
