# DATAROBOT MCP Server – Demos and Payload Examples

## 🎥 Demo Video
- **MCP server setup explanation + API Execution + Features Testing**: [Watch Here](https://drive.google.com/file/d/1bQjsX1lk5-T1KIdmyvdcV5HSNhgWcKaN/view?usp=sharing)

---

## 🎥 Credentials Gathering Video
- **Gathering Credentials & Setup(Full ene - to - end video)**: [Watch Here](https://drive.google.com/file/d/1qu05XvVdK4XRusdg-QqhdJKCEp9I4j9x/view?usp=sharing)

---

## 🔐 Credential JSON Payload
Example payload format for sending credentials to the MCP Server which going to be use it in Client API paylod:
```json
{
  "DATAROBOT": {
    "api_key": "your-datarobot-api-key",
    "file_path" : "absolute-path-to-file" #Optional
  }
}
``` 