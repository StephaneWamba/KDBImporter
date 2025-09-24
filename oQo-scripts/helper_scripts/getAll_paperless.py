import requests
import os
from dotenv import load_dotenv

# Configuration

load_dotenv("../.env")

PAPERLESS_URL = "https://kdb.mohamedh.me"
API_TOKEN = os.getenv("PAPERLESS_TOKEN")
print(API_TOKEN)

# Setup headers
HEADERS = {
    "Authorization": f"Token {API_TOKEN}",
    "Accept": "application/json"
}

# Base endpoint for documents
DOCUMENTS_ENDPOINT = f"{PAPERLESS_URL}/api/documents/"

def get_all_documents():
    documents = []
    url = DOCUMENTS_ENDPOINT

    while url:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch data: {response.status_code} - {response.text}")

        data = response.json()
        documents.extend(data['results'])
        url = data['next']  # for pagination

    return documents

def main():
    docs = get_all_documents()
    print(f"Retrieved {len(docs)} documents.")
    for doc in docs:
        print(f"ID: {doc['id']}, Title: {doc['title']}, Created: {doc['created']}, Tags: {[tag['name'] for tag in doc['tags']]}")

if __name__ == "__main__":
    main()
