import boto3
import os
from dotenv import load_dotenv
from PyPDF2 import PdfReader

# Load AWS credentials from .env
load_dotenv()

# Initialize S3 client
s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
)

def list_objects(bucket_name):
    """List all objects in a bucket."""
    response = s3.list_objects_v2(Bucket=bucket_name)
    contents = response.get("Contents", [])
    if contents:
        for obj in contents:
            print("📄", obj["Key"])
    else:
        print("No files found in the bucket.")

def delete_object(bucket_name, key):
    """Delete a file from a bucket."""
    s3.delete_object(Bucket=bucket_name, Key=key)
    print(f"🗑️ Deleted '{key}' from '{bucket_name}'")

def upload_text_file(bucket_name, key):
    """Upload a single-line text input to a file in S3."""
    text = input("Enter text to upload to S3: ")
    s3.put_object(Bucket=bucket_name, Key=key, Body=text.encode('utf-8'))
    print(f"✅ Uploaded text to '{key}'")

def download_and_print_file(bucket_name, key):
    """Download a .txt or .pdf file and print its content."""
    file_path = f"./temp_{os.path.basename(key)}"
    s3.download_file(bucket_name, key, file_path)

    if key.endswith('.txt'):
        with open(file_path, 'r') as f:
            print(f.read())
    elif key.endswith('.pdf'):
        reader = PdfReader(file_path)
        for page in reader.pages:
            print(page.extract_text())
    else:
        print("❌ Unsupported file format for preview.")

    os.remove(file_path)

def upload_file(bucket_name, file_path, s3_key=None):
    """Upload any file from local path to S3."""
    if not s3_key:
        s3_key = os.path.basename(file_path)

    try:
        s3.upload_file(file_path, bucket_name, s3_key)
        print(f"✅ Uploaded '{file_path}' as '{s3_key}'")
    except Exception as e:
        print(f"❌ Upload failed: {e}")

def type_and_upload_report(bucket_name, s3_key):
    """Type a full report (multi-line) and upload to S3."""
    print("📝 Type your report below. Press ENTER twice to finish.")
    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)

    report_text = "\n".join(lines)
    
    temp_file = "temp_report.txt"
    with open(temp_file, "w") as f:
        f.write(report_text)

    try:
        s3.upload_file(temp_file, bucket_name, s3_key)
        print(f"✅ Report uploaded as '{s3_key}'")
    except Exception as e:
        print(f"❌ Upload failed: {e}")
    finally:
        os.remove(temp_file)

# --- Main menu loop ---
if __name__ == "__main__":
    bucket = input("Enter your S3 bucket name: ").strip()

    while True:
        print("\n📦 S3 Bucket Tools")
        print("1. List objects")
        print("2. Upload one-line text input to a file")
        print("3. Delete an object")
        print("4. Read and print .txt or .pdf")
        print("5. Upload any file (PDF, DOCX, etc.)")
        print("6. Type and upload a full report")
        print("7. Exit")

        choice = input("Enter your choice (1–7): ")

        if choice == '1':
            list_objects(bucket)
        elif choice == '2':
            key = input("Enter filename to save text as (e.g., notes.txt): ").strip()
            upload_text_file(bucket, key)
        elif choice == '3':
            key = input("Enter object key to delete: ").strip()
            delete_object(bucket, key)
        elif choice == '4':
            key = input("Enter .txt or .pdf filename to download and read: ").strip()
            download_and_print_file(bucket, key)
        elif choice == '5':
            file_path = input("Enter full path to your file: ").strip()
            s3_key = input("Enter S3 filename (leave blank to use original name): ").strip() or None
            upload_file(bucket, file_path, s3_key)
        elif choice == '6':
            s3_key = input("Enter S3 filename for your report (e.g., my_report.txt): ").strip()
            type_and_upload_report(bucket, s3_key)
        elif choice == '7':
            print("👋 Exiting. Goodbye!")
            break
        else:
            print("❌ Invalid choice.")
