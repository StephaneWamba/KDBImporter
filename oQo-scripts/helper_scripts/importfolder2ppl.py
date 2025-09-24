import os
import argparse
import requests

from dotenv import load_dotenv

load_dotenv("../.env", override=True)
# === Configuration ===
PAPERLESS_URL = os.getenv("PAPERLESS_URL", "http://localhost:8000")
API_TOKEN = os.getenv("PAPERLESS_TOKEN")

# === Upload function ===
def upload_pdf(file_path, document_type=None, custom_fields=None):
    url = f"{PAPERLESS_URL}/api/documents/post_document/"
    headers = {
        "Authorization": f"Token {API_TOKEN}",
    }

    files = {
        "document": open(file_path, "rb")
    }

    data = {}
    if document_type:
        data["document_type"] = document_type

    # Custom fields
    if custom_fields:
        for key, value in custom_fields.items():
            if value:
                data[f"custom_fields.{key}"] = value

    response = requests.post(url, headers=headers, files=files, data=data)
    return response.status_code, response.text

# === Argument parser ===
def main():
    parser = argparse.ArgumentParser(description="Upload PDFs to Paperless-ngx")

    parser.add_argument("folder", help="Path to folder containing PDFs")
    parser.add_argument("--document_type", default=None, help="Document type ID")
    parser.add_argument("--added_via", default=None, help="Custom field: Added-Via")
    parser.add_argument("--scope", default=None, help="Custom field: Scope")
    parser.add_argument("--authors", default=None, help="Custom field: Authors")
    parser.add_argument("--source", default=None, help="Custom field: Source")

    args = parser.parse_args()

    # Prepare custom fields
    custom_fields = {
        "Added-Via": args.added_via,
        "Scope": args.scope,
        "Authors": args.authors,
        "Source": args.source,
    }

    # Upload all PDF files in the folder
    for filename in os.listdir(args.folder):
        if filename.lower().endswith(".pdf"):
            file_path = os.path.join(args.folder, filename)
            print(f"Uploading: {file_path}")
            status, response = upload_pdf(file_path, args.document_type, custom_fields)
            print(f"Status: {status}, Response: {response}")

if __name__ == "__main__":
    main()
