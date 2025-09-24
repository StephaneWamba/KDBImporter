import requests
import os
from dotenv import load_dotenv

# Configuration
load_dotenv("../.env", override=True)
PAPERLESS_URL = os.getenv("PAPERLESS_URL")
API_TOKEN = os.getenv("PAPERLESS_TOKEN")


HEADERS = {
    "Authorization": f"Token {API_TOKEN}",
    "Content-Type": "application/json"
}

# Utility functions
def get_existing(endpoint):
    items = []
    url = f"{PAPERLESS_URL}/api/{endpoint}/"
    print(url)
    while url:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        items.extend(data["results"])
        url = data.get("next")  # Will be None when no more pages
    return items

def post_if_not_exists(endpoint, name, extra_fields=None):
    
    existing = get_existing(endpoint)
    # print(existing) 
    if any(item["name"] == name for item in existing):
        print(f"{name} already exists in {endpoint}.")
        return
    payload = {"name": name}
    if extra_fields:
        payload.update(extra_fields)
    response = requests.post(f"{PAPERLESS_URL}/api/{endpoint}/", json=payload, headers=HEADERS)
    print(f"{PAPERLESS_URL}/api/{endpoint}/")
    response.raise_for_status()
    print(f"Created {name} in {endpoint}.")

def get_custom_fields():
    return get_existing("custom_fields")

def create_custom_field(name, field_type, select_options=None):
    existing_fields = get_custom_fields()
    for field in existing_fields:
        if field["name"] == name:
            print(f"Custom field '{name}' already exists.")
            # Check for and add missing select options if necessary
            if field_type == "select" and select_options:
                existing_options = [opt["label"] for opt in field.get("extra_data", {}).get("select_options", [])]
                missing_options = [opt for opt in select_options if opt not in existing_options]
                if missing_options:
                    print(f"Missing options for '{name}': {missing_options}")
                else:
                    print(f"All select options for '{name}' already exist.")
            return

    payload = {
        "name": name,
        "data_type": field_type,
    }

    if field_type == "select" and select_options:
        payload["extra_data"] = {
            "select_options": [{"label": opt, "id": None} for opt in select_options]
        }

    response = requests.post(f"{PAPERLESS_URL}/api/custom_fields/", json=payload, headers=HEADERS)
    response.raise_for_status()
    print(f"Created custom field '{name}' with type '{field_type}'.")


# Load from files
def load_list_from_file(filename):
    with open(filename, "r") as file:
        return [line.strip() for line in file if line.strip()]




if __name__ == "__main__":
    # Document Types
    doc_types = load_list_from_file("types.txt")
    for doc_type in doc_types:
        post_if_not_exists("document_types", doc_type)

    # Tags
    tags = load_list_from_file("tags.txt")
    for tag in tags:
        post_if_not_exists("tags", tag)

    # Custom Fields

    create_custom_field("Authors", "string")
    create_custom_field("Keywords", "string")
    create_custom_field("Affiliated-Organization", "string")

    create_custom_field("Source", "string")
    create_custom_field("Download-URL", "string")

    create_custom_field("Added-Via", "select", ["Manual", "Script"])

    create_custom_field("Scope", "select", ["Education", "Research", "Industry", "Regulatory"])

    
    create_custom_field("Download-URL", "string")

    create_custom_field("Qurisk-Relevance", "string")
    create_custom_field("Import-Query", "string")
