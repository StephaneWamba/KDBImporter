#!/usr/bin/env python3
"""
Test script to debug Paperless-ngx API connection
"""
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

PAPERLESS_URL = os.getenv("PAPERLESS_BASE_URL")
PAPERLESS_TOKEN = os.getenv("PAPERLESS_API_TOKEN")

print(f"Testing connection to: {PAPERLESS_URL}")
print(f"Token: {PAPERLESS_TOKEN[:10]}...")

# Test basic API connection
try:
    headers = {"Authorization": f"Token {PAPERLESS_TOKEN}"}
    
    # Test documents endpoint
    print("\n1. Testing documents endpoint...")
    response = requests.get(f"{PAPERLESS_URL}/documents/", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {data.get('count', 0)} documents")
    else:
        print(f"Error: {response.text}")
    
    # Test custom fields endpoint
    print("\n2. Testing custom fields endpoint...")
    response = requests.get(f"{PAPERLESS_URL}/custom_fields/", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data.get('results', []))} custom fields")
        for field in data.get('results', []):
            print(f"  - {field.get('name')}: {field.get('data_type')}")
    else:
        print(f"Error: {response.text}")
    
    # Test tags endpoint
    print("\n3. Testing tags endpoint...")
    response = requests.get(f"{PAPERLESS_URL}/tags/", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data.get('results', []))} tags")
        for tag in data.get('results', [])[:5]:  # Show first 5
            print(f"  - {tag.get('name')}")
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Connection error: {e}")

