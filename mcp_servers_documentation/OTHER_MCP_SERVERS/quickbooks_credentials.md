# QuickBooks MCP Server Credentials

## Overview

This document provides instructions on obtaining and structuring the credentials needed to connect the QuickBooks MCP Server in the Vanij Platform.

---

## Credential Format

```json
{
  "QUICKBOOKS": {
    "access_token": "your_access_token_here",
    "refresh_token": "your_refresh_token_here",
    "client_id": "your_client_id_here",
    "client_secret": "your_client_secret_here",
    "realm_id": "your_realm_id_here"
  }
}
```

## Required Fields

### access_token

- **Type**: String
- **Description**: OAuth2 access token for QuickBooks API authentication
- **How to obtain**: Generated through OAuth2 flow with QuickBooks

### refresh_token

- **Type**: String
- **Description**: OAuth2 refresh token used to get new access tokens
- **How to obtain**: Generated through OAuth2 flow with QuickBooks

### client_id

- **Type**: String
- **Description**: QuickBooks App Client ID from your QuickBooks app
- **How to obtain**: From QuickBooks Developer Dashboard

### client_secret

- **Type**: String
- **Description**: QuickBooks App Client Secret from your QuickBooks app
- **How to obtain**: From QuickBooks Developer Dashboard

### realm_id

- **Type**: String
- **Description**: QuickBooks Company/Realm ID
- **How to obtain**: From QuickBooks API response or developer dashboard

## Setup Instructions

1. Create a QuickBooks app in the [QuickBooks Developer Dashboard](https://developer.intuit.com/)
2. Configure OAuth2 settings with your redirect URI
3. Use the OAuth2 flow to obtain access_token and refresh_token
4. Extract realm_id from the OAuth2 response
5. Use the credential format above in your API requests

## Example Request

```json
{
  "selected_server_credentials": {
    "QUICKBOOKS": {
      "access_token": "AB8CNSbebfpV6QykrHQY3dCscMDc55yPko3bWzEFOm2iyuv5JQ",
      "refresh_token": "dGNk8m8i64kGWbcefpvqkxELPPIyGNpS6FYo1Xcd",
      "client_id": "AB8CNSbebfpV6QykrHQY3dCscMDc55yPko3bWzEFOm2iyuv5JQ",
      "client_secret": "dGNk8m8i64kGWbcefpvqkxELPPIyGNpS6FYo1Xcd",
      "realm_id": "4620816365326124560"
    }
  },
  "client_details": {
    "input": "fetch me customers from quickbooks",
    "prompt": "you are a helpful assistant"
  },
  "selected_client": "MCP_CLIENT_GEMINI",
  "selected_servers": ["QUICKBOOKS"]
}
```
