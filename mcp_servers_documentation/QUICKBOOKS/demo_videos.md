# QUICKBOOKS MCP Server – Demos and Payload Examples

## 🎥 Demo Video
- **MCP server setup explanation + API Execution + Features Testing**: [Watch Here](https://your-demo-video-link.com)

---

## 🎥 Credentials Gathering Video
- **Gathering Credentials & Setup(Full end - to - end video)**: [Watch Here](https://your-demo-video-link.com)

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