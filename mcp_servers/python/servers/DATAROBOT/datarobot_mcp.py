from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import requests
import os
from typing import Any, Optional, Dict, Union, List
load_dotenv() 
# Initialize MCP server
mcp = FastMCP("DataRobot-MCP")
api_key = os.getenv("DATAROBOT_API_KEY")
api_url = os.getenv("DATAROBOT_ENDPOINT")

#works (checked)
@mcp.tool()
def create_project_from_file(file_path: str, project_name: str) -> dict:
    """
    Create a new DataRobot project by uploading a local file (resolved to absolute path).
    Automatically injects credentials and project metadata during upload.
    
    - Uses absolute file path to ensure consistent file access behavior.
    - Returns project ID on success, and additional metadata for debugging.
    
    Args:
        file_path: Local path to dataset file (required, converted to absolute path internally)
        project_name: Name of the project to be created (required)

    Returns:
        {
            "status": str,  # Status message indicating success or partial success
            "project_id": str,  # Project ID returned by DataRobot if creation is successful
            "absolute_path_used": str,  # Fully resolved path to the uploaded file
        }
        OR
        {
            "status": str,  # Indicates no JSON returned, fallback to status code
            "http_status_code": int,
            "absolute_path_used": str
        }
    """
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
#works (checked)
def set_target_and_start_training(project_id: str, target: str) -> dict:
    """
    Set the target feature and initiate model training for a given DataRobot project.
    
    - Uses PATCH request to the /aim endpoint to assign the target column.
    - Automatically triggers DataRobot's autopilot modeling process.
    
    Args:
        project_id: ID of the DataRobot project where training will be started (required)
        target: Name of the target column in the dataset (required)

    Returns:
        {
            "status": "Model training started",
            "project_id": str  # Confirmed project ID
        }
    """
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
#works (checked)
def get_status_of_project(project_id: str) -> dict:
    """
    Retrieve the current status of a DataRobot project, including autopilot completion and stage information.
    
    - Queries the `/status` endpoint to fetch real-time modeling progress.
    - Returns autopilot status, current stage, and descriptive label of the stage.
    
    Args:
        project_id: ID of the DataRobot project to check status for (required)
    
    Returns:
        {
            "status": "Project Status Obtained",
            "project_id": str,  # The ID of the queried project
            "Autopilot Done": bool,  # Whether modeling is complete
            "Stage Description": str,  # Human-readable description of the current stage
            "Current Stage": str  # Internal stage identifier (e.g., 'modeling', 'eda', etc.)
        }
    """
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
#works (checked)
def get_modeling_jobs(project_id: str, status: Optional[str] = None) -> Dict[str, Union[str, List[Dict]]]:
    """
    Get project jobs with EXACT behavior matching DataRobot's API spec:
    - Default returns only queued/in_progress jobs (excludes errored jobs)
    - Status filter returns ONLY jobs matching that exact status
    
    Args:
        project_id: DataRobot project ID (required, path parameter)
        status: If provided, returns ONLY jobs with this status (optional, query parameter)
    
    Returns:
        {
            "project_id": str,
            "status_filter": Optional[str],
            "jobs": List[Dict]  # Raw API response data
        }
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    params = {}
    if status:
        params["status"] = status  # Only add if explicitly provided
        
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
#works (checked)
def list_models(project_id: str) -> dict:
    """
    List all models built for a given DataRobot project.
    
    - Fetches model metadata including model type, ID, and associated metrics.
    - Useful for ranking models by performance or selecting one for deployment.
    
    Args:
        project_id: The ID of the DataRobot project for which to list models (required)
    
    Returns:
        {
            "status": "Success",
            "models": List[Dict]  # List of model summaries with:
                [
                    {
                        "model_id": str,  # Unique model identifier
                        "model_type": str,  # Type of model (e.g., 'RandomForestClassifier')
                        "metric": Dict  # Full metric dictionary for model performance
                    },
                    ...
                ]
        }
    """
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    response = requests.get(
        f"https://app.datarobot.com/api/v2/projects/{project_id}/models/",
        headers=headers
    )
    response.raise_for_status()
    models = response.json()

    return {
        "status": "Success",
        "models": [
            {
                "model_id": m["id"],
                "model_type": m["modelType"],
                "metric": m["metrics"]
            } for m in models
        ]
    }

@mcp.tool()
#works (checked)
def delete_project(project_id: str) -> dict:
    """
    Delete a specific DataRobot project permanently.
    
    - Sends a DELETE request to remove the project by its ID.
    - Use with caution: this action cannot be undone.
    
    Args:
        project_id: The ID of the DataRobot project to delete (required)
    
    Returns:
        {
            "status": "Project deleted",
            "project_id": str  # ID of the deleted project
        }
    """
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    response = requests.delete(
        f"https://app.datarobot.com/api/v2/projects/{project_id}",
        headers=headers
    )
    response.raise_for_status()
    return {"status": "Project deleted", "project_id": project_id}

@mcp.tool()
#works (checked)
def delete_deployment(deployment_id: str) -> dict:
    """
    Permanently delete a specific deployment in DataRobot.
    
    - Sends a DELETE request to remove the deployment by its ID.
    - Use with caution: this action is irreversible and will stop any ongoing predictions.
    
    Args:
        deployment_id: The ID of the deployment to delete (required)
    
    Returns:
        {
            "status": "Deployment deleted",
            "deployment_id": str  # ID of the deleted deployment
        }
    """
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    response = requests.delete(
        f"https://app.datarobot.com/api/v2/deployments/{deployment_id}",
        headers=headers
    )
    response.raise_for_status()
    return {"status": "Deployment deleted", "deployment_id": deployment_id}

@mcp.tool()
#works (checked)
def list_projects() -> dict:
    """
    List all available DataRobot projects accessible via the current API key.
    
    - Sends a GET request to fetch project metadata.
    - Returns a list of project IDs and names, along with the total count.
    
    Args:
        None
    
    Returns:
        {
            "status": "Success",
            "project_count": int,  # Total number of projects retrieved
            "projects": List[Dict]  # Each item contains project 'id' and 'name'
                [
                    {"id": str, "name": str},
                    ...
                ]
        }
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    response = requests.get(
        "https://app.datarobot.com/api/v2/projects/",
        headers=headers
    )
    response.raise_for_status()
    projects = response.json()

    return {
        "status": "Success",
        "project_count": len(projects),
        "projects": [
            {"id": project.get("id"), "name": project.get("projectName")}
            for project in projects
        ]
    }

@mcp.tool()
#works (checked)
def list_deployments() -> dict:
    """
    List all active deployments in the user's DataRobot account.
    
    - Retrieves deployment metadata, including status, label, and associated model details.
    - Useful for monitoring deployment health or fetching deployment IDs programmatically.
    
    Args:
        None

    Returns:
        {
            "deployments_count": int,  # Total number of deployments returned
            "deployments": List[Dict]  # Each entry includes:
                [
                    {
                        "id": str,  # Deployment ID
                        "label": str,  # Human-readable deployment label
                        "status": str,  # Deployment status (e.g., 'active', 'decommissioned')
                        "model_type": str,  # Model type associated with deployment (e.g., 'RandomForest')
                        "model_id": str  # Model ID used in the deployment
                    },
                    ...
                ]
        }
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    response = requests.get(
        "https://app.datarobot.com/api/v2/deployments/",
        headers=headers
    )
    response.raise_for_status()

    return {
        "deployments_count": response.json()["count"],
        "deployments": 
        [
            {
            "id": deployment.get("id"), 
             "label": deployment.get("label"),
             "status": deployment.get("status"),
             "model_type": deployment.get("model", {}).get("type"),
             "model_id": deployment.get("model", {}).get("id")
            }
            for deployment in response.json()["data"]
        ]
    }

@mcp.tool()
#works (checked)
def get_deployment_metrics(deployment_id: str) -> Dict[str, Any]:
    """
    Get deployment-level metrics including health, prediction usage, and model accuracy.

    Args:
        deployment_id: The unique identifier of the deployment.

    Returns:
        {
            "deployment_id": str,
            "label": str,
            "prediction_usage": Dict,
            "service_health": Dict,
            "model_health": Dict,
            "recent_accuracy": Dict
        }
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # 1. Fetch deployment metadata (includes health + prediction usage)
    deployment_resp = requests.get(
        f"{api_url}/api/v2/deployments/{deployment_id}/",
        headers=headers
    )
    deployment_resp.raise_for_status()
    deployment_data = deployment_resp.json()

    # 2. Fetch recent accuracy snapshot
    accuracy_resp = requests.get(
        f"{api_url}/api/v2/deployments/{deployment_id}/accuracy/",
        headers=headers,
        params={"window": "7d"}  # Optional: tweak the window as needed
    )
    accuracy_resp.raise_for_status()
    accuracy_data = accuracy_resp.json()

    return {
        "deployment_id": deployment_id,
        "label": deployment_data.get("label"),
        "prediction_usage": deployment_data.get("predictionUsage", {}),
        "service_health": deployment_data.get("serviceHealth", {}),
        "model_health": deployment_data.get("modelHealth", {}),
        "recent_accuracy": accuracy_data.get("data", {})
    }

@mcp.tool()
#invalid
def deploy_model(model_id: str, label: str, description: str = "Default deployment description") -> dict:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://app.datarobot.com/api/v2/deployments/fromLearningModel/",
        headers=headers,
        json={
            "modelId": model_id,
            "label": label            
        }
    )
    try:
        response.raise_for_status() 
    except requests.exceptions.HTTPError as err:
        print(err.response.json()) 
    return {"status": "Model deployed", "deployment_id": response.json()["id"]}

@mcp.tool()
#invalid
def predict(deployment_id: str, file_path: str) -> dict:
    headers = {
        "Authorization": f"Bearer {api_key}"  # Make sure `api_key` is defined globally or passed securely
    }

    with open(file_path, "rb") as f:
        files = {
            "file": f
        }
        response = requests.post(
            f"https://app.datarobot.com/api/v2/deployments/{deployment_id}/predictions/",
            headers=headers,
            files=files  # This triggers multipart/form-data automatically
        )
        response.raise_for_status()

    return {
        "status": "Prediction successful",
        "predictions": response.json()["data"]
    }

#invalid
@mcp.tool()
def create_prediction_server(hostname: str, name: str) -> dict:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        "https://app.datarobot.com/api/v2/predictionServers/",
        headers=headers,
        json={
            "name": name,
            "hostUrl": hostname,
            "authType": "basic",  # or "oauth" if needed
            "username": "your_username",  # if using basic auth
            "password": "your_password"   # if using basic auth
        }
    )
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    mcp.run(transport="stdio")