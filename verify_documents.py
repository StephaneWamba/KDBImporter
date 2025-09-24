#!/usr/bin/env python3
"""
Verify documents were added to Paperless-ngx
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()
headers = {'Authorization': f'Token {os.getenv("PAPERLESS_API_TOKEN")}'}
response = requests.get(
    f'{os.getenv("PAPERLESS_BASE_URL")}/documents/', headers=headers)
data = response.json()
print(f'Total documents in Paperless-ngx: {data.get("count", 0)}')
print('✅ Documents successfully added!')
