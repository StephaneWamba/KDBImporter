#!/usr/bin/env python3
"""
Integration Bridge between KDB-importer and Paperless-ngx
This script takes papers from KDB-importer and sends them to Paperless-ngx
"""
import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
KDB_BACKEND_URL = "http://localhost:8000/api"
PAPERLESS_URL = os.getenv("PAPERLESS_BASE_URL")
PAPERLESS_TOKEN = os.getenv("PAPERLESS_API_TOKEN")

def get_paperless_headers():
    """Get headers for Paperless-ngx API"""
    return {"Authorization": f"Token {PAPERLESS_TOKEN}"}

def get_document_types():
    """Get available document types from Paperless-ngx"""
    response = requests.get(f"{PAPERLESS_URL}/document_types/", headers=get_paperless_headers())
    if response.status_code == 200:
        data = response.json()
        return {dt["name"]: dt["id"] for dt in data.get("results", [])}
    return {}

def get_tags():
    """Get available tags from Paperless-ngx"""
    response = requests.get(f"{PAPERLESS_URL}/tags/", headers=get_paperless_headers())
    if response.status_code == 200:
        data = response.json()
        return {tag["name"]: tag["id"] for tag in data.get("results", [])}
    return {}

def download_pdf(pdf_url, title):
    """Download PDF from arXiv"""
    try:
        response = requests.get(pdf_url, timeout=30)
        if response.status_code == 200:
            return response.content
    except Exception as e:
        print(f"Error downloading PDF for {title}: {e}")
    return None

def upload_to_paperless(paper_data, pdf_content, metadata):
    """Upload paper to Paperless-ngx"""
    try:
        # Get document types and tags
        doc_types = get_document_types()
        tags = get_tags()
        
        # Prepare the upload data
        upload_data = {
            "title": paper_data["title"],
            "created": paper_data["published"][:10],  # Extract date part
        }
        
        # Add document type (convert name to ID)
        doc_type_name = metadata.get("document_type", "Scientific-Paper")
        if doc_type_name in doc_types:
            upload_data["document_type"] = doc_types[doc_type_name]
        
        # Add tags if provided (convert names to IDs)
        if metadata.get("tag"):
            tag_name = metadata.get("tag")
            if tag_name in tags:
                upload_data["tags"] = [tags[tag_name]]
        
        # Prepare files
        files = {
            "document": (f"{paper_data['id']}.pdf", pdf_content, "application/pdf")
        }
        
        # Upload to Paperless-ngx
        response = requests.post(
            f"{PAPERLESS_URL}/documents/post_document/",
            data=upload_data,
            files=files,
            headers=get_paperless_headers()
        )
        
        if response.status_code == 200:
            task_id = response.text.strip('"')  # Remove quotes from UUID
            print(f"✅ Successfully queued for upload: {paper_data['title']} (Task ID: {task_id[:8]}...)")
            
            # Note: In Paperless-ngx, documents are processed asynchronously
            # The actual document ID will be available after processing
            print(f"   📄 Document will be processed and available shortly")
            
            return task_id
        else:
            print(f"❌ Failed to upload {paper_data['title']}: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error uploading {paper_data['title']}: {e}")
        return None

def update_custom_fields(doc_id, paper_data, metadata):
    """Update custom fields for the uploaded document"""
    try:
        custom_fields_data = {
            "Authors": ", ".join(paper_data["authors"]),
            "Keywords": metadata.get("tag", ""),
            "Source": "arXiv",
            "Download-URL": paper_data["pdf_url"],
            "Added-Via": "KDB-Importer",
            "Import-Query": metadata.get("import_query", "")
        }
        
        # Update custom fields
        response = requests.patch(
            f"{PAPERLESS_URL}/documents/{doc_id}/",
            json={"custom_fields": custom_fields_data},
            headers=get_paperless_headers()
        )
        
        if response.status_code == 200:
            print(f"✅ Updated custom fields for document {doc_id}")
        else:
            print(f"⚠️ Failed to update custom fields: {response.status_code}")
            
    except Exception as e:
        print(f"⚠️ Error updating custom fields: {e}")

def import_papers_from_kdb(arxiv_ids, metadata_list=None):
    """Import papers from KDB-importer to Paperless-ngx"""
    print(f"🚀 Starting import of {len(arxiv_ids)} papers...")
    
    # Get available document types and tags
    doc_types = get_document_types()
    tags = get_tags()
    
    print(f"📋 Available document types: {list(doc_types.keys())}")
    print(f"🏷️ Available tags: {list(tags.keys())[:5]}...")
    
    # Import papers from KDB-importer
    import_data = {
        "inputs": arxiv_ids,
        "metadata": metadata_list or []
    }
    
    try:
        response = requests.post(f"{KDB_BACKEND_URL}/import", json=import_data)
        if response.status_code != 200:
            print(f"❌ Failed to get papers from KDB-importer: {response.status_code}")
            return
        
        results = response.json().get("results", [])
        print(f"📄 Retrieved {len(results)} papers from KDB-importer")
        
        # Process each paper
        successful_uploads = 0
        for i, result in enumerate(results):
            if not result.get("success"):
                print(f"⚠️ Skipping failed paper: {result.get('reason', 'Unknown error')}")
                continue
            
            paper_data = result["data"]["paper"]
            paper_metadata = result["data"]["metadata"]
            
            print(f"\n📖 Processing: {paper_data['title']}")
            print(f"   Authors: {', '.join(paper_data['authors'][:3])}{'...' if len(paper_data['authors']) > 3 else ''}")
            print(f"   PDF URL: {paper_data['pdf_url']}")
            
            # Download PDF
            pdf_content = download_pdf(paper_data["pdf_url"], paper_data["title"])
            if not pdf_content:
                print(f"❌ Failed to download PDF for {paper_data['title']}")
                continue
            
            # Upload to Paperless-ngx
            task_id = upload_to_paperless(paper_data, pdf_content, paper_metadata)
            if task_id:
                successful_uploads += 1
            
            # Add delay to avoid overwhelming the API
            import time
            time.sleep(2)
        
        print(f"\n🎉 Import completed! Successfully uploaded {successful_uploads}/{len(results)} papers")
        
    except Exception as e:
        print(f"❌ Error during import: {e}")

def main():
    """Main function"""
    print("🔗 KDB-importer ↔ Paperless-ngx Integration Bridge")
    print("=" * 50)
    
    # Test connections
    print("🔍 Testing connections...")
    
    # Test KDB-importer
    try:
        response = requests.get(f"{KDB_BACKEND_URL.replace('/api', '')}/docs")
        print(f"✅ KDB-importer backend: {response.status_code}")
    except Exception as e:
        print(f"❌ KDB-importer backend: {e}")
        return
    
    # Test Paperless-ngx
    try:
        response = requests.get(f"{PAPERLESS_URL}/documents/", headers=get_paperless_headers())
        print(f"✅ Paperless-ngx: {response.status_code} ({response.json().get('count', 0)} documents)")
    except Exception as e:
        print(f"❌ Paperless-ngx: {e}")
        return
    
    # Example import
    print("\n📚 Example: Importing some quantum computing papers...")
    
    # Sample arXiv IDs for quantum computing papers
    sample_papers = [
        "2301.12345",  # The one we tested earlier
        "2302.12345",  # Another sample
        "2303.12345"   # Another sample
    ]
    
    sample_metadata = [
        {"importance": "high", "tag": "Quantum Computing"},
        {"importance": "medium", "tag": "Quantum Algorithm"},
        {"importance": "high", "tag": "Quantum Hardware"}
    ]
    
    import_papers_from_kdb(sample_papers, sample_metadata)

if __name__ == "__main__":
    main()
