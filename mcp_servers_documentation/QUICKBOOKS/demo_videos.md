# QUICKBOOKS MCP Server – Demos and Payload Examples

## 🎥 Demo Video

- **MCP server setup explanation + API Execution + Features Testing**: [Watch Here](https://drive.google.com/file/d/164ZxRXaSuL67-V1HSOWGlyZtEG3tUXzF/view)

---

## 🎥 Credentials Gathering Video

- **Gathering Credentials & Setup(Full end - to - end video)**: [Watch Here](https://drive.google.com/file/d/1nY_T_5YJ8jQxClRnaX48xzFNsJFX2Vcr/view)

---

## 🔐 Credential JSON Payload

Example payload format for sending credentials to the MCP Server which going to be use it in Client API paylod:

```json
{
  "QUICKBOOKS": {
    "access_token": "your_quickbooks_access_token_here",
    "refresh_token": "your_quickbooks_refresh_token_here",
    "client_id": "your_quickbooks_client_id_here",
    "client_secret": "your_quickbooks_client_secret_here",
    "realm_id": "your_quickbooks_realm_id_here"
  }
}
```

## ENSURE THAT YOU SIGN IN AND CREATE A WORKSPACE, AND AN APP IN IT BEFORE MOVING ON TO GATHERING CREDENTIALS VIDEO ("https://developer.intuit.com/app/developer/homepage")
