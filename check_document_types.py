#!/usr/bin/env python3
"""
Check document types in Paperless-ngx
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()
headers = {'Authorization': f'Token {os.getenv("PAPERLESS_API_TOKEN")}'}
response = requests.get(f'{os.getenv("PAPERLESS_BASE_URL")}/document_types/', headers=headers)
data = response.json()
print('Available document types:')
for dt in data.get('results', []):
    print(f'  - {dt.get("name")} (ID: {dt.get("id")})')

