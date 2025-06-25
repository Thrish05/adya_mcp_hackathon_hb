import requests
import base64
import os
import time
from dotenv import load_dotenv
import base64 as pybase64
import json

CLIENT_ID="AB8CNSbebfpV6QykrHQY3dCscMDc55yPko3bWzEFOm2iyuv5JQ"
CLIENT_SECRET="dGNk8m8i64kGWbcefpvqkxELPPIyGNpS6FYo1Xcd"
REDIRECT_URI="http://localhost:8000/callback"
AUTHORIZATION_CODE="XAB11750765064Eh2Vo5e9FjMoNFNmgWhbsp0TzFitZUG00Bdu"

load_dotenv()

def extract_realm_id_from_id_token(id_token):
    try:
        payload = id_token.split(".")[1]
        # Pad base64 string if needed
        padding = '=' * (-len(payload) % 4)
        decoded = pybase64.urlsafe_b64decode(payload + padding)
        data = json.loads(decoded)
        return data.get("realmId") or data.get("realmid") or data.get("realm_id") or data.get("realm_id")
    except Exception as e:
        print("Could not extract REALM_ID from id_token:", e)
        return None

def get_tokens():
    url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    headers = {
        "Authorization": "Basic " + base64.b64encode(credentials.encode()).decode(),
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    body = {
        "grant_type": "authorization_code",
        "code": AUTHORIZATION_CODE,
        "redirect_uri": REDIRECT_URI
    }

    response = requests.post(url, headers=headers, data=body)
    print(response.status_code, response.json())
    if response.status_code == 200:
        result = response.json()
        new_access_token = result.get("access_token")
        new_refresh_token = result.get("refresh_token")
        expires_in = result.get("expires_in", 3600)
        new_expires_at = str(time.time() + expires_in)
        id_token = result.get("id_token")
        realm_id = None
        if id_token:
            realm_id = extract_realm_id_from_id_token(id_token)
        # Update .env file with absolute path inside QUICKBOOKS_ONLINE_MCP
        dotenv_path = "C:/adya_ai/adya_mcp_hackathon_hb/mcp_servers/python/servers/QUICKBOOKS_ONLINE_MCP/.env"
        print("Updating .env at:", dotenv_path)
        try:
            with open(dotenv_path, "r") as f:
                lines = f.readlines()
        except FileNotFoundError:
            lines = []
        env_vars = {k: v for k, v in [line.strip().split("=", 1) for line in lines if "=" in line]}
        env_vars["ACCESS_TOKEN"] = new_access_token
        env_vars["REFRESH_TOKEN"] = new_refresh_token
        env_vars["ACCESS_TOKEN_EXPIRES_AT"] = new_expires_at
        if realm_id:
            env_vars["REALM_ID"] = str(realm_id)
        with open(dotenv_path, "w") as f:
            for k, v in env_vars.items():
                f.write(f"{k}={v}\n")

get_tokens() 