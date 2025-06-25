# tools.py
print("tools.py loaded")

import requests
import time
import base64

# Centralized configuration for QuickBooks API
QBO_BASE_URL = "https://sandbox-quickbooks.api.intuit.com/v3/company"

def _qbo_api_request(server_credentials: dict, method: str, endpoint: str, **kwargs) -> dict:
    """
    A centralized function to make authenticated requests to the QuickBooks Online API.
    Uses credentials from server_credentials dictionary.
    """
    # Extract credentials
    token = server_credentials.get("access_token")
    realm_id = server_credentials.get("realm_id")
    url = f"{QBO_BASE_URL}/{realm_id}/{endpoint}"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        **kwargs.pop("extra_headers", {})
    }

    try:
        resp = requests.request(
            method,
            url,
            headers=headers,
            **kwargs
        )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError as e:
        print(f"QuickBooks API Error: {e.response.status_code} - {e.response.text}")
        return e.response.json()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {"error": "An unexpected error occurred", "details": str(e)}

def refresh_access_token(server_credentials: dict) -> dict:
    """
    Refreshes the OAuth2 access token using the refresh token from server_credentials.
    Returns updated tokens and updates server_credentials in-place.
    """
    client_id = server_credentials.get("client_id")
    client_secret = server_credentials.get("client_secret")
    refresh_token = server_credentials.get("refresh_token")
    url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
    
    if not all([client_id, client_secret, refresh_token]):
        raise Exception("CLIENT_ID, CLIENT_SECRET, and REFRESH_TOKEN must be provided in server_credentials")

    creds = f"{client_id}:{client_secret}"
    headers = {
        "Authorization": "Basic " + base64.b64encode(creds.encode()).decode(),
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    resp = requests.post(url, headers=headers, data=data)
    result = resp.json()

    if resp.status_code == 200:
        print("Successfully refreshed access token.")
        # Update server_credentials with new tokens
        server_credentials["access_token"] = result["access_token"]
        server_credentials["refresh_token"] = result.get("refresh_token", refresh_token)
        server_credentials["access_token_expires_at"] = time.time() + result["expires_in"]
        return server_credentials
    else:
        raise Exception("Failed to refresh access token", result)

def ensure_valid_token(server_credentials: dict) -> str:
    """
    Checks if the current access token is expired and refreshes it if needed.
    Returns a valid access token and updates server_credentials in-place.
    """
    expires_at = server_credentials.get("access_token_expires_at", 0)
    
    # Refresh token if expired or near expiration (5 minute buffer)
    if time.time() > expires_at - 300:
        print("Access token expired or nearing expiration, refreshing...")
        refreshed_creds = refresh_access_token(server_credentials)
        return refreshed_creds["access_token"]
    
    return server_credentials["access_token"]

# ==============================================================================
#  TOOL DEFINITIONS (UPDATED WITH SERVER_CREDENTIALS PARAMETER)
# ==============================================================================

def get_quickbooks_customers(server_credentials: dict, query: str = "SELECT * FROM Customer") -> dict:
    """Fetch customers from QuickBooks Online."""
    if not server_credentials:
        return {"error": "No server credentials provided"}
    
    if not isinstance(server_credentials, dict):
        return {"error": f"Server credentials must be a dictionary, got {type(server_credentials)}"}
    
    # Check for required credentials
    required_keys = ["access_token", "realm_id"]
    missing_keys = [key for key in required_keys if key not in server_credentials]
    if missing_keys:
        return {"error": f"Missing required credentials: {missing_keys}"}
    
    ensure_valid_token(server_credentials)
    return _qbo_api_request(
        server_credentials,
        "GET",
        "query",
        params={"query": query},
        extra_headers={"Content-Type": "application/text"}
    )

def get_quickbooks_invoices(server_credentials: dict, query: str = "SELECT * FROM Invoice") -> dict:
    """Fetch invoices from QuickBooks Online."""
    ensure_valid_token(server_credentials)
    return _qbo_api_request(
        server_credentials,
        "GET",
        "query",
        params={"query": query},
        extra_headers={"Content-Type": "application/text"}
    )

def create_quickbooks_customer(server_credentials: dict, data: dict) -> dict:
    """Create a customer in QuickBooks Online."""
    ensure_valid_token(server_credentials)
    return _qbo_api_request(
        server_credentials,
        "POST",
        "customer?minorversion=75",
        json=data,
        extra_headers={"Content-Type": "application/json"}
    )

def get_quickbooks_customer_by_id(server_credentials: dict, customer_id: str) -> dict:
    """Fetch a customer by ID from QuickBooks Online."""
    ensure_valid_token(server_credentials)
    return _qbo_api_request(
        server_credentials,
        "GET",
        f"customer/{customer_id}?minorversion=75"
    )

def create_quickbooks_invoice(server_credentials: dict, data: dict) -> dict:
    """Create an invoice in QuickBooks Online."""
    ensure_valid_token(server_credentials)
    return _qbo_api_request(
        server_credentials,
        "POST",
        "invoice?minorversion=75",
        json=data,
        extra_headers={"Content-Type": "application/json"}
    )

def update_quickbooks_invoice(server_credentials: dict, invoice_id: str, sync_token: str, data: dict) -> dict:
    """Update an invoice in QuickBooks Online."""
    ensure_valid_token(server_credentials)
    data['Id'] = invoice_id
    data['SyncToken'] = sync_token
    return _qbo_api_request(
        server_credentials,
        "POST",
        "invoice?minorversion=75",
        json=data,
        extra_headers={"Content-Type": "application/json"}
    )

def delete_quickbooks_invoice(server_credentials: dict, invoice_id: str, sync_token: str) -> dict:
    """Delete an invoice in QuickBooks Online."""
    ensure_valid_token(server_credentials)
    data = {
        "Id": invoice_id,
        "SyncToken": sync_token
    }
    return _qbo_api_request(
        server_credentials,
        "POST",
        "invoice?operation=delete&minorversion=75",
        json=data,
        extra_headers={"Content-Type": "application/json"}
    )

def create_quickbooks_purchase(server_credentials: dict, data: dict) -> dict:
    """Create a purchase in QuickBooks Online."""
    ensure_valid_token(server_credentials)
    return _qbo_api_request(
        server_credentials,
        "POST",
        "purchase?minorversion=75",
        json=data,
        extra_headers={"Content-Type": "application/json"}
    )

def create_quickbooks_vendor(server_credentials: dict, data: dict) -> dict:
    """Create a vendor in QuickBooks Online."""
    ensure_valid_token(server_credentials)
    return _qbo_api_request(
        server_credentials,
        "POST",
        "vendor?minorversion=75",
        json=data,
        extra_headers={"Content-Type": "application/json"}
    )

def get_quickbooks_accounts(server_credentials: dict, query: str = "SELECT * FROM Account") -> dict:
    """Fetch all accounts from the Chart of Accounts."""
    ensure_valid_token(server_credentials)
    return _qbo_api_request(
        server_credentials,
        "POST",
        "query",
        data=query,
        extra_headers={"Content-Type": "application/text"}
    )

def create_quickbooks_account(server_credentials: dict, data: dict) -> dict:
    """Create an account in QuickBooks Online."""
    ensure_valid_token(server_credentials)
    return _qbo_api_request(
        server_credentials,
        "POST",
        "account?minorversion=75",
        json=data,
        extra_headers={"Content-Type": "application/json"}
    )

def update_quickbooks_account(server_credentials: dict, account_id: str, sync_token: str, data: dict) -> dict:
    """Update an account in QuickBooks Online."""
    ensure_valid_token(server_credentials)
    data['Id'] = account_id
    data['SyncToken'] = sync_token
    return _qbo_api_request(
        server_credentials,
        "POST",
        "account?minorversion=75",
        json=data,
        extra_headers={"Content-Type": "application/json"}
    )

def deactivate_quickbooks_account(server_credentials: dict, account_id: str, sync_token: str) -> dict:
    """Deactivates an account in QuickBooks."""
    ensure_valid_token(server_credentials)
    data = {
        'Id': account_id,
        'SyncToken': sync_token,
        'Active': False
    }
    return _qbo_api_request(
        server_credentials,
        "POST",
        "account?operation=update",
        json=data,
        extra_headers={"Content-Type": "application/json"}
    )

def get_quickbooks_purchases(server_credentials: dict, query: str = "SELECT * FROM Purchase") -> dict:
    """Fetch all purchases from QuickBooks Online."""
    ensure_valid_token(server_credentials)
    return _qbo_api_request(
        server_credentials,
        "GET",
        "query",
        params={"query": query},
        extra_headers={"Content-Type": "application/text"}
    )

def update_quickbooks_purchase(server_credentials: dict, purchase_id: str, sync_token: str, data: dict) -> dict:
    """Update a purchase in QuickBooks Online."""
    ensure_valid_token(server_credentials)
    data['Id'] = purchase_id
    data['SyncToken'] = sync_token
    return _qbo_api_request(
        server_credentials,
        "POST",
        "purchase?minorversion=75",
        json=data,
        extra_headers={"Content-Type": "application/json"}
    )

def delete_quickbooks_purchase(server_credentials: dict, purchase_id: str, sync_token: str) -> dict:
    """Delete a purchase in QuickBooks Online."""
    ensure_valid_token(server_credentials)
    data = {
        'Id': purchase_id,
        'SyncToken': sync_token
    }
    return _qbo_api_request(
        server_credentials,
        "POST",
        "purchase?operation=delete&minorversion=75",
        json=data,
        extra_headers={"Content-Type": "application/json"}
    )

def update_quickbooks_customer(server_credentials: dict, customer_id: str, sync_token: str, data: dict) -> dict:
    """Update a customer in QuickBooks Online."""
    ensure_valid_token(server_credentials)
    data['Id'] = customer_id
    data['SyncToken'] = sync_token
    return _qbo_api_request(
        server_credentials,
        "POST",
        "customer?minorversion=75",
        json=data,
        extra_headers={"Content-Type": "application/json"}
    )

def deactivate_quickbooks_customer(server_credentials: dict, customer_id: str, sync_token: str) -> dict:
    """Deactivates a customer in QuickBooks Online."""
    ensure_valid_token(server_credentials)
    data = {
        'Id': customer_id,
        'SyncToken': sync_token,
        'Active': False
    }
    return _qbo_api_request(
        server_credentials,
        "POST",
        "customer?operation=update&minorversion=75",
        json=data,
        extra_headers={"Content-Type": "application/json"}
    )

tools = [
    get_quickbooks_customers,
    get_quickbooks_invoices,
    create_quickbooks_customer,
    get_quickbooks_customer_by_id,
    create_quickbooks_invoice,
    update_quickbooks_invoice,
    delete_quickbooks_invoice,
    create_quickbooks_purchase,
    create_quickbooks_vendor,
    get_quickbooks_accounts,
    create_quickbooks_account,
    update_quickbooks_account,
    deactivate_quickbooks_account,
    get_quickbooks_purchases,
    update_quickbooks_purchase,
    delete_quickbooks_purchase,
    update_quickbooks_customer,
    deactivate_quickbooks_customer,
]
