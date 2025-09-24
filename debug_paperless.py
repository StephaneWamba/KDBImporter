#!/usr/bin/env python3
"""
Debug script for PaperlessClient
"""
from src.api.clients.APIClient import APIClient
from dotenv import load_dotenv
import os
import sys
sys.path.append('/app')


# Load environment variables
load_dotenv()

PAPERLESS_URL = os.getenv("PAPERLESS_URL")
PAPERLESS_TOKEN = os.getenv("PAPERLESS_TOKEN")

print(f"Testing PaperlessClient initialization...")
print(f"URL: {PAPERLESS_URL}")
print(f"Token: {PAPERLESS_TOKEN[:10]}...")

try:
    # Test basic API client first
    headers = {"Authorization": f"Token {PAPERLESS_TOKEN}"}
    client = APIClient(base_url=PAPERLESS_URL, headers=headers)

    print("\n1. Testing custom fields endpoint...")
    response = client.get("/api/custom_fields/")
    print(f"Response type: {type(response)}")
    print(f"Response: {response}")

    if isinstance(response, dict) and "results" in response:
        print(f"Found {len(response['results'])} custom fields")
        for field in response['results']:
            print(f"  - {field.get('name')}: {field.get('data_type')}")
    else:
        print("ERROR: Response is not a dict with 'results' key")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
