from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import requests
import os
from typing import Any, Optional, Dict, Union, List

def main():
    load_dotenv()
    mcp = FastMCP("DataRobot-MCP")
    api_key = os.getenv("DATAROBOT_API_KEY")
    api_url = os.getenv("DATAROBOT_ENDPOINT")

    @mcp.tool()
    def create_project_from_file(file_path: str, project_name: str) -> dict:
        absolute_file_path = os.path.abspath(file_path)
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        with open(absolute_file_path, "rb") as file_data:
            files = {
                "file": file_data
            }
            data = {
                "projectName": project_name,
            }
            response = requests.post(
                "https://app.datarobot.com/api/v2/projects/",
                headers=headers,
                files=files,
                data=data
            )
            response.raise_for_status()
            if response.content:
                project_id = response.json()["id"]
                return {
                    "status": "Project created",
                    "project_id": project_id,
                    "absolute_path_used": absolute_file_path
                }
            else:
                return {
                    "status": "Project created (no JSON returned)",
                    "http_status_code": response.status_code,
                    "absolute_path_used": absolute_file_path
                }

    @mcp.tool()
    def set_target_and_start_training(project_id: str, target: str) -> dict:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        response = requests.patch(
            f"https://app.datarobot.com/api/v2/projects/{project_id}/aim",
            headers=headers,
            json={"target": target}
        )
        return {"status": "Model training started", "project_id": project_id}

    @mcp.tool()
    def get_status_of_project(project_id: str) -> dict:
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        response = requests.get(
            f"https://app.datarobot.com/api/v2/projects/{project_id}/status",
            headers=headers
        )
        response.raise_for_status()
        return {"status": "Project Status Obtained", 
                "project_id": project_id,
                "Autopilot Done": response.json()["autopilotDone"],
                "Stage Description": response.json()["stageDescription"],
                "Current Stage": response.json()["stage"]}

    @mcp.tool()
    def get_modeling_jobs(project_id: str, status: Optional[str] = None) -> Dict[str, Union[str, List[Dict]]]:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        params = {}
        if status:
            params["status"] = status
        response = requests.get(
            f"https://app.datarobot.com/api/v2/projects/{project_id}/jobs/",
            headers=headers,
            params=params
        )
        response.raise_for_status()
        return {
            "project_id": project_id,
            "status_filter": status,
            "jobs": response.json().get("jobs", [])
        }

    @mcp.tool()
    def list_models(project_id: str) -> dict:
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        response = requests.get(
            f"https://app.datarobot.com/api/v2/projects/{project_id}/models/",
            headers=headers
        )
        response.raise_for_status()
        return {"status": "Success", "models": response.json().get("models", [])}

    @mcp.tool()
    def delete_project(project_id: str) -> dict:
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        response = requests.delete(
            f"https://app.datarobot.com/api/v2/projects/{project_id}/",
            headers=headers
        )
        return {"status": "Project deleted", "project_id": project_id, "http_status_code": response.status_code}

    @mcp.tool()
    def delete_deployment(deployment_id: str) -> dict:
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        response = requests.delete(
            f"https://app.datarobot.com/api/v2/deployments/{deployment_id}/",
            headers=headers
        )
        return {"status": "Deployment deleted", "deployment_id": deployment_id, "http_status_code": response.status_code}

    @mcp.tool()
    def list_projects() -> dict:
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        response = requests.get(
            "https://app.datarobot.com/api/v2/projects/",
            headers=headers
        )
        response.raise_for_status()
        return {"status": "Success", "projects": response.json().get("projects", [])}

    @mcp.tool()
    def list_deployments() -> dict:
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        response = requests.get(
            "https://app.datarobot.com/api/v2/deployments/",
            headers=headers
        )
        response.raise_for_status()
        return {"status": "Success", "deployments": response.json().get("deployments", [])}

    @mcp.tool()
    def get_deployment_metrics(deployment_id: str) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        response = requests.get(
            f"https://app.datarobot.com/api/v2/deployments/{deployment_id}/metrics/",
            headers=headers
        )
        response.raise_for_status()
        return {"status": "Success", "metrics": response.json()}

    @mcp.tool()
    def deploy_model(model_id: str, label: str, description: str = "Default deployment description") -> dict:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "modelId": model_id,
            "label": label,
            "description": description
        }
        response = requests.post(
            "https://app.datarobot.com/api/v2/deployments/",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        return {"status": "Deployment created", "deployment_id": response.json().get("id")}

    @mcp.tool()
    def predict(deployment_id: str, file_path: str) -> dict:
        absolute_file_path = os.path.abspath(file_path)
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        with open(absolute_file_path, "rb") as file_data:
            files = {
                "file": file_data
            }
            response = requests.post(
                f"https://app.datarobot.com/api/v2/deployments/{deployment_id}/predictions/",
                headers=headers,
                files=files
            )
            response.raise_for_status()
            return {"status": "Prediction complete", "predictions": response.json()}

    @mcp.tool()
    def create_prediction_server(hostname: str, name: str) -> dict:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "hostname": hostname,
            "name": name
        }
        response = requests.post(
            "https://app.datarobot.com/api/v2/predictionServers/",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        return {"status": "Prediction server created", "server_id": response.json().get("id")}

    # Run the MCP server
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main() 