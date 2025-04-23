# 🗂️ Simple S3 MCP Server

This server exposes an AWS S3 interface as tools for an LLM agent via the Model Context Protocol (MCP).

## ✅ Available Tools

| Tool                        | Description |
|-----------------------------|-------------|
| `list_files`                | Lists all object keys in a bucket |
| `list_keys_with_metadata`   | Lists keys with storage class and region |
| `get_file_content`          | Returns content of UTF-8 `.txt` files |
| `upload_text`               | Uploads a text string as a file |
| `upload_file`               | Uploads a local file by path |
| `upload_report`             | Uploads multi-line report as `.txt` |
| `delete_file`               | Deletes a file from S3 |
| `download_and_preview`      | Downloads and prints `.txt` or `.pdf` |
| `check_authorization`       | Checks if AWS credentials are valid |
| `create_bucket`             | Creates a new S3 bucket |

---

## ⚠️ Common Problems and Fixes

### 1. ❌ `SSE connection not established` or `500 Internal Server Error`
- Cause: Tool crashed due to large files or invalid UTF-8 content
- Fix: Use `get_file_content` only for small `.txt` files

---

### 2. ❌ `MCP error -32001: Request timed out`
- Cause: Tool (e.g. `get_file_content`) taking too long or file is large
- Fix: Use truncated previews or limit to first few KB of content

---

### 3. ❌ `Invalid bucket name` or `The specified key does not exist`
- Fix: Ensure no trailing spaces in input fields
- Solution: All tools automatically apply `.strip()` to inputs

---

### 4. 🧠 JSON formatting issues in `upload_report`
- Fix: Must enter `lines` as valid JSON array:
  ```json
  [
    "Line 1",
    "Line 2"
  ]
