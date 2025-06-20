# tools.py

print("tools.py loaded")

import requests
import os
import time
import base64
from dotenv import load_dotenv
  

# Always load the .env file from the QUICKBOOKS_ONLINE_MCP folder
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

print("ACCESS_TOKEN:", os.getenv("ACCESS_TOKEN"))
print("REFRESH_TOKEN:", os.getenv("REFRESH_TOKEN"))
print("ACCESS_TOKEN_EXPIRES_AT:", os.getenv("ACCESS_TOKEN_EXPIRES_AT"))

def clean(val):
    return val.strip('"\'') if val else val

def ensure_valid_token():
    try:
        expires_at = float(clean(os.getenv("ACCESS_TOKEN_EXPIRES_AT", "0")))
    except (ValueError, TypeError):
        expires_at = 0

    if time.time() > expires_at - 300:
        return refresh_access_token()
    return clean(os.getenv("ACCESS_TOKEN"))

def refresh_access_token():
    client_id     = clean(os.getenv("CLIENT_ID"))
    client_secret = clean(os.getenv("CLIENT_SECRET"))
    refresh_token = clean(os.getenv("REFRESH_TOKEN"))
    url           = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
    creds         = f"{client_id}:{client_secret}"

    headers = {
        "Authorization": "Basic " + base64.b64encode(creds.encode()).decode(),
        "Accept":        "application/json",
        "Content-Type":  "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type":    "refresh_token",
        "refresh_token": refresh_token
    }

    resp   = requests.post(url, headers=headers, data=data)
    result = resp.json()
    if resp.status_code == 200:
        new_access_token = result.get("access_token", os.getenv("ACCESS_TOKEN"))
        new_refresh_token = result.get("refresh_token", refresh_token)
        expires_in = result.get("expires_in", 3600)
        new_expires_at = str(time.time() + expires_in)
        os.environ["ACCESS_TOKEN"] = new_access_token
        os.environ["ACCESS_TOKEN_EXPIRES_AT"] = new_expires_at
        os.environ["REFRESH_TOKEN"] = new_refresh_token

        # Update .env file
        dotenv_path = os.path.join(os.path.dirname(__file__), "../../../.env")
        dotenv_path = os.path.abspath(dotenv_path)
        try:
            with open(dotenv_path, "r") as f:
                lines = f.readlines()
        except FileNotFoundError:
            lines = []
        env_vars = {k: v for k, v in [line.strip().split("=", 1) for line in lines if "=" in line]}
        env_vars["ACCESS_TOKEN"] = new_access_token
        env_vars["ACCESS_TOKEN_EXPIRES_AT"] = new_expires_at
        env_vars["REFRESH_TOKEN"] = new_refresh_token
        with open(dotenv_path, "w") as f:
            for k, v in env_vars.items():
                f.write(f"{k}={v}\n")
        return new_access_token
    else:
        raise Exception("Refresh failed", result)

def get_quickbooks_customers():
    print("ACCESS_TOKEN:", os.getenv("ACCESS_TOKEN"))
    print("REFRESH_TOKEN:", os.getenv("REFRESH_TOKEN"))
    print("REALM_ID:", os.getenv("REALM_ID"))
    print("ACCESS_TOKEN_EXPIRES_AT:", os.getenv("ACCESS_TOKEN_EXPIRES_AT"))
    print("Registering tool: get_quickbooks_customers")
    """Fetch all customers from QuickBooks Online."""
    token    = ensure_valid_token()
    realm_id = clean(os.getenv("REALM_ID"))
    url      = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{realm_id}/query"
    headers  = {
        "Authorization": f"Bearer {token}",
        "Accept":        "application/json",
        "Content-Type":  "application/text"
    }
    query    = "SELECT * FROM Customer"
    resp     = requests.get(url, headers=headers, params={"query": query})
    return resp.json()

def get_quickbooks_invoices():
    print("Registering tool: get_quickbooks_invoices")
    """Fetch all invoices from QuickBooks Online."""
    token    = ensure_valid_token()
    realm_id = clean(os.getenv("REALM_ID"))
    url      = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{realm_id}/query"
    headers  = {
        "Authorization": f"Bearer {token}",
        "Accept":        "application/json",
        "Content-Type":  "application/text"
    }
    query    = "SELECT * FROM Invoice"
    resp     = requests.get(url, headers=headers, params={"query": query})
    return resp.json()

def create_quickbooks_customer(data: dict):
    print("Registering tool: create_quickbooks_customer")
    """Create a customer in QuickBooks Online."""
    token    = ensure_valid_token()
    realm_id = clean(os.getenv("REALM_ID"))
    url      = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{realm_id}/customer?minorversion=75"
    headers  = {
        "Authorization": f"Bearer {token}",
        "Accept":        "application/json",
        "Content-Type":  "application/json"
    }
    resp     = requests.post(url, headers=headers, json=data)
    return resp.json()

def get_quickbooks_customer_by_id(customer_id: str):
    print("Registering tool: get_quickbooks_customer_by_id")
    """Fetch a customer by ID from QuickBooks Online."""
    token    = ensure_valid_token()
    realm_id = clean(os.getenv("REALM_ID"))
    url      = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{realm_id}/customer/{customer_id}?minorversion=75"
    headers  = {
        "Authorization": f"Bearer {token}",
        "Accept":        "application/json"
    }
    resp     = requests.get(url, headers=headers)
    return resp.json()

def create_quickbooks_invoice(data: dict):
    print("Registering tool: create_quickbooks_invoice")
    """Create an invoice in QuickBooks Online."""
    token    = ensure_valid_token()
    realm_id = clean(os.getenv("REALM_ID"))
    url      = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{realm_id}/invoice?minorversion=75"
    headers  = {
        "Authorization": f"Bearer {token}",
        "Accept":        "application/json",
        "Content-Type":  "application/json"
    }
    resp     = requests.post(url, headers=headers, json=data)
    return resp.json()

def update_quickbooks_invoice(invoice_id: str, data: dict):
    print("Registering tool: update_quickbooks_invoice")
    """Update an invoice in QuickBooks Online. 'data' must include the latest SyncToken."""
    token    = ensure_valid_token()
    realm_id = clean(os.getenv("REALM_ID"))
    url      = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{realm_id}/invoice?minorversion=75"
    headers  = {
        "Authorization": f"Bearer {token}",
        "Accept":        "application/json",
        "Content-Type":  "application/json"
    }
    # QBO requires the Id and SyncToken in the body for update
    data['Id'] = invoice_id
    resp     = requests.post(url, headers=headers, json=data)
    return resp.json()

def delete_quickbooks_invoice(invoice_id: str, sync_token: str):
    print("Registering tool: delete_quickbooks_invoice")
    """Delete an invoice in QuickBooks Online. Requires Id and latest SyncToken."""
    token    = ensure_valid_token()
    realm_id = clean(os.getenv("REALM_ID"))
    url      = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{realm_id}/invoice?operation=delete&minorversion=75"
    headers  = {
        "Authorization": f"Bearer {token}",
        "Accept":        "application/json",
        "Content-Type":  "application/json"
    }
    data = {
        "Id": invoice_id,
        "SyncToken": sync_token
    }
    resp     = requests.post(url, headers=headers, json=data)
    return resp.json()

tools = [
    get_quickbooks_customers,
    get_quickbooks_invoices,
    create_quickbooks_customer,
    get_quickbooks_customer_by_id,
    create_quickbooks_invoice,
    update_quickbooks_invoice,
    delete_quickbooks_invoice
]