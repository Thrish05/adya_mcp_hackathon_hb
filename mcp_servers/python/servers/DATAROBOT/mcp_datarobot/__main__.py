from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import requests
import os
from typing import Any, Optional, Dict, Union, List

def main():
    load_dotenv()
    mcp = FastMCP("DataRobot-MCP")
    
    # Helper function to get API key from server_credentials
    def get_api_key(server_credentials: dict) -> str:
        """Get API key from server_credentials or environment"""
        # Priority 1: Credentials from server_credentials
        if server_credentials and "api_key" in server_credentials:
            return server_credentials["api_key"]
        
        # Priority 2: Environment variable
        env_key = os.getenv("DATAROBOT_API_KEY")
        if env_key:
            return env_key
            
        raise ValueError("No DataRobot API key provided")

    # All tools use server_credentials parameter
    @mcp.tool() #works in postman
    def create_project(server_credentials: dict, project_name: str = "") -> dict:
        """
        Create a new project in DataRobot.
        The file path is provided in the server_credentials.
        """
        api_key = get_api_key(server_credentials)
        
        absolute_file_path = os.path.abspath(server_credentials.get("file_path")).replace("\\", "/")
        headers = {"Authorization": f"Bearer {api_key}"}
        with open(absolute_file_path, "rb") as file_data:
            files = {"file": file_data}
            data = {"projectName": project_name}
            response = requests.post(
                "https://app.datarobot.com/api/v2/projects/",
                headers=headers,
                files=files,
                data=data
            )
            response.raise_for_status()
            if response.content:
                project_id = response.json().get("id")
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

    @mcp.tool() #works in postman
    def set_target_and_start_training(server_credentials: dict, project_id: str, target: str) -> dict:
        api_key = get_api_key(server_credentials)
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

    @mcp.tool() #works in postman
    def get_status_of_project(server_credentials: dict, project_id: str) -> dict:
        api_key = get_api_key(server_credentials)
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(
            f"https://app.datarobot.com/api/v2/projects/{project_id}/status",
            headers=headers
        )
        response.raise_for_status()
        return {"status": "Project Status Obtained", 
                "project_id": project_id,
                "Autopilot Done": response.json().get("autopilotDone"),
                "Stage Description": response.json().get("stageDescription"),
                "Current Stage": response.json().get("stage")}

    @mcp.tool() #works in postman
    def get_modeling_jobs(server_credentials: dict, project_id: str, status: Optional[str] = None) -> Dict[str, Union[str, List[Dict]]]:
        api_key = get_api_key(server_credentials)
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

    @mcp.tool() #works in postman
    def list_models(server_credentials: dict, project_id: str) -> dict:
        api_key = get_api_key(server_credentials)
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(
            f"https://app.datarobot.com/api/v2/projects/{project_id}/models/",
            headers=headers
        )
        response.raise_for_status()
        models = response.json()
        summarized_models = []
        for model in models:
            summarized_models.append({
                "id": model.get("id"),
                "modelType": model.get("modelType"),
                "modelFamily": model.get("modelFamilyFullName"),
                "featurelistName": model.get("featurelistName"),
                "metrics": {
                    "RMSE": model.get("metrics", {}).get("RMSE", {}),
                    "R Squared": model.get("metrics", {}).get("R Squared", {}),
                    "MAE": model.get("metrics", {}).get("MAE", {}),
                },
                "stage": model.get("lifecycle", {}).get("stage"),
                "isFrozen": model.get("isFrozen"),
                "samplePct": model.get("samplePct")
            })

        return {
            "status": "Success",
            "model_count": len(models),
            "models_summary": summarized_models
        }
    
    @mcp.tool() #works in postman
    def select_best_model(server_credentials: dict, project_id: str) -> dict:
        api_key = get_api_key(server_credentials)
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(
            f"https://app.datarobot.com/api/v2/projects/{project_id}/models/",
            headers=headers
        )
        response.raise_for_status()
        models = response.json()

        best_model = None
        best_rmse = float("inf")

        for model in models:
            rmse_info = model.get("metrics", {}).get("RMSE", {})
            rmse = rmse_info.get("validation")
            if rmse is not None and rmse < best_rmse:
                best_model = model
                best_rmse = rmse

        if not best_model:
            return {"status": "No suitable model found."}

        return {
            "status": "Success",
            "best_model_id": best_model["id"],
            "rmse": best_rmse,
            "model_type": best_model.get("modelType"),
            "featurelist": best_model.get("featurelistName")
        }
    
    @mcp.tool() #works in postman
    def delete_project(server_credentials: dict, project_id: str) -> dict:
        api_key = get_api_key(server_credentials)
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.delete(
            f"https://app.datarobot.com/api/v2/projects/{project_id}/",
            headers=headers
        )
        return {"status": "Project deleted", "project_id": project_id, "http_status_code": response.status_code}

    @mcp.tool() #works in postman
    def delete_deployment(server_credentials: dict, deployment_id: str) -> dict:
        api_key = get_api_key(server_credentials)
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.delete(
            f"https://app.datarobot.com/api/v2/deployments/{deployment_id}/",
            headers=headers
        )
        return {"status": "Deployment deleted", "deployment_id": deployment_id, "http_status_code": response.status_code}

    @mcp.tool() #works in postman
    def list_projects(server_credentials: dict) -> dict:
        api_key = get_api_key(server_credentials)
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(
            "https://app.datarobot.com/api/v2/projects/",
            headers=headers
        )
        response.raise_for_status()
        projects = response.json()
        return {
            "status": "Success", 
            "projects": projects,
            "count": len(projects)
        }

    @mcp.tool() #works in postman
    def list_deployments(server_credentials: dict) -> dict:
        api_key = get_api_key(server_credentials)
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(
            "https://app.datarobot.com/api/v2/deployments/",
            headers=headers
        )
        response.raise_for_status()
        json_data = response.json()

        deployments = json_data.get("data", [])

        # Optionally extract a brief summary
        deployment_summaries = []
        for dep in deployments:
            deployment_summaries.append({
                "id": dep.get("id"),
                "label": dep.get("label"),
                "status": dep.get("status"),
                "createdAt": dep.get("createdAt"),
                "modelId": dep.get("model", {}).get("id"),
                "modelType": dep.get("model", {}).get("type"),
                "projectId": dep.get("model", {}).get("projectId"),
                "projectName": dep.get("model", {}).get("projectName"),
                "predictionEnvironment": dep.get("predictionEnvironment", {}).get("name"),
                "approvalStatus": dep.get("approvalStatus")
            })

        return {
            "status": "Success",
            "deployment_count": json_data.get("count", 0),
            "deployments_summary": deployment_summaries
        }

    @mcp.tool() #works in postman
    def get_deployment_metrics(server_credentials: dict, deployment_id: str) -> Dict[str, Any]:
        """
        Retrieve deployment-level metrics including accuracy snapshot, supported capabilities, and feature importances.

        Args:
            server_credentials: Dictionary containing API key info.
            deployment_id: Unique identifier of the deployment.

        Returns:
            {
                "deployment_id": str,
                "accuracy_metrics": Dict[str, Any],
                "supported_capabilities": List[str],
                "unsupported_capabilities": Dict[str, List[str]],
                "top_features": List[Dict[str, Any]]
            }
        """
        api_key = get_api_key(server_credentials)
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        api_url = "https://app.datarobot.com/api/v2"

        # 1. Accuracy metrics
        accuracy_resp = requests.get(
            f"{api_url}/deployments/{deployment_id}/accuracy/",
            headers=headers,
        )
        accuracy_resp.raise_for_status()
        accuracy_data = accuracy_resp.json().get("metrics", {})

        # 2. Capabilities
        capabilities_resp = requests.get(
            f"{api_url}/deployments/{deployment_id}/capabilities/",
            headers=headers
        )
        capabilities_resp.raise_for_status()
        capabilities_data = capabilities_resp.json().get("data", [])

        supported = [cap["name"] for cap in capabilities_data if cap["supported"]]
        unsupported = {
            cap["name"]: cap.get("messages", [])
            for cap in capabilities_data if not cap["supported"]
        }

        # 3. Feature importances
        features_resp = requests.get(
            f"{api_url}/deployments/{deployment_id}/features/",
            headers=headers
        )
        features_resp.raise_for_status()
        feature_data = features_resp.json().get("data", [])

        top_features = sorted(
            feature_data,
            key=lambda x: abs(x.get("importance", 0)),
            reverse=True
        )

        return {
            "deployment_id": deployment_id,
            "accuracy_metrics": accuracy_data,
            "supported_capabilities": supported,
            "unsupported_capabilities": unsupported,
            "top_features": top_features[:10]  # Top 10 by absolute importance
        }

    @mcp.tool() #works in postman
    def get_deployment_summary(server_credentials: dict, deployment_id: str) -> Dict[str, Any]:
        """
        Summarizes key metrics and health statuses for a given deployment.

        Args:
            server_credentials: Dict containing API key.
            deployment_id: Unique identifier of the deployment.

        Returns:
            Dictionary with deployment summary including label, status, health metrics, usage, and model details.
        """
        api_key = get_api_key(server_credentials)
        headers = {"Authorization": f"Bearer {api_key}"}

        response = requests.get(
            f"https://app.datarobot.com/api/v2/deployments/{deployment_id}/",
            headers=headers
        )
        response.raise_for_status()
        data = response.json()

        return {
            "deployment_id": data.get("id"),
            "label": data.get("label"),
            "status": data.get("status"),
            "created_at": data.get("createdAt"),
            "model": {
                "type": data.get("model", {}).get("type"),
                "project_name": data.get("model", {}).get("projectName"),
                "target": data.get("model", {}).get("targetName")
            },
            "prediction_environment": data.get("predictionEnvironment", {}).get("name"),
            "prediction_usage_last_7_days": data.get("predictionUsage", {}).get("dailyRates", []),
            "health": {
                "service": data.get("serviceHealth", {}).get("status"),
                "model": data.get("modelHealth", {}).get("status"),
                "accuracy": data.get("accuracyHealth", {}).get("status"),
                "custom_metrics": data.get("customMetricsHealth", {}).get("status"),
                "fairness": data.get("fairnessHealth", {}).get("status")
            },
            "governance_approval": data.get("governance", {}).get("approvalStatus"),
            "creator": {
                "name": f"{data.get('creator', {}).get('firstName')} {data.get('creator', {}).get('lastName')}",
                "email": data.get("creator", {}).get("email")
            },
            "has_error": data.get("hasError", False)
        }

        api_key = get_api_key(server_credentials)
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

    # Run the MCP server
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
