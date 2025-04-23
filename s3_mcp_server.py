import os
import boto3
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from PyPDF2 import PdfReader

# Load AWS credentials
load_dotenv()

# Create MCP server
mcp = FastMCP("S3 File Manager")

# Init S3 client
s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
)

@mcp.tool()
def list_files(bucket_name: str) -> list:
    """List all objects in a given S3 bucket."""
    response = s3.list_objects_v2(Bucket=bucket_name.strip())
    contents = response.get("Contents", [])
    return [obj["Key"] for obj in contents] if contents else ["No files found."]

@mcp.tool()
def delete_file(bucket_name: str, key: str) -> str:
    """Delete a file from a bucket."""
    s3.delete_object(Bucket=bucket_name.strip(), Key=key.strip())
    return f"🗑️ Deleted '{key}' from '{bucket_name}'."

@mcp.tool()
def upload_text(bucket_name: str, key: str, content: str) -> str:
    """Upload string content as a text file to S3."""
    s3.put_object(Bucket=bucket_name.strip(), Key=key.strip(), Body=content.encode('utf-8'))
    return f"✅ Uploaded text content as '{key}'."

@mcp.tool()
def upload_file(bucket_name: str, file_path: str, s3_key: str = None) -> str:
    """Upload a local file to S3."""
    s3_key = s3_key or os.path.basename(file_path)
    s3.upload_file(file_path, bucket_name.strip(), s3_key.strip())
    return f"✅ Uploaded '{file_path}' as '{s3_key}'"

@mcp.tool()
def download_and_preview(bucket_name: str, key: str) -> str:
    """Download and return preview of .txt or .pdf file from S3."""
    try:
        file_path = f"./temp_{os.path.basename(key)}"
        bucket = bucket_name.strip()
        s3.download_file(bucket, key.strip(), file_path)

        if key.endswith(".txt"):
            with open(file_path, "r") as f:
                content = f.read()
        elif key.endswith(".pdf"):
            reader = PdfReader(file_path)
            content = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        else:
            content = "❌ Unsupported file format for preview."

        os.remove(file_path)
        return content
    except Exception as e:
        return f"❌ Error during file preview: {str(e)}"

@mcp.tool()
def upload_report(bucket_name: str, key: str, lines: list[str]) -> str:
    """Upload a multi-line report as a .txt file to S3."""
    report = "\n".join(lines)
    temp_file = "temp_report.txt"
    with open(temp_file, "w") as f:
        f.write(report)

    try:
        s3.upload_file(temp_file, bucket_name.strip(), key.strip())
        return f"✅ Uploaded report as '{key}'"
    except Exception as e:
        return f"❌ Upload failed: {str(e)}"
    finally:
        os.remove(temp_file)