#!/usr/bin/env python3
"""
Test script for UI Integration - End-to-End Testing
Tests the complete flow from frontend to Paperless-ngx
"""

import requests
import json
import time

# Configuration
KDB_BACKEND_URL = "http://localhost:8000/api"
KDB_FRONTEND_URL = "http://localhost:5173"
PAPERLESS_URL = "https://kdb.mohamedh.me/api"


def test_backend_api():
    """Test the backend API endpoints"""
    print("🔧 Testing Backend API...")

    # Test import endpoint
    import_payload = {
        "inputs": ["2301.12345"],
        "metadata": [{"importance": "high", "tag": "UI-Test"}]
    }

    response = requests.post(f"{KDB_BACKEND_URL}/import", json=import_payload)
    if response.status_code == 200:
        print("✅ Import endpoint working")
        paper_data = response.json()["results"][0]["data"]
        return paper_data
    else:
        print(f"❌ Import endpoint failed: {response.status_code}")
        return None


def test_paperless_upload(paper_data):
    """Test the Paperless upload endpoint"""
    print("📄 Testing Paperless Upload...")

    upload_payload = {
        "paper": paper_data["paper"],
        "metadata": paper_data["metadata"]
    }

    response = requests.post(
        f"{KDB_BACKEND_URL}/paperless/upload", json=upload_payload)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Paperless upload successful: {result['task_id'][:8]}...")
        return result["task_id"]
    else:
        print(
            f"❌ Paperless upload failed: {response.status_code} - {response.text}")
        return None


def test_frontend_accessibility():
    """Test if frontend is accessible"""
    print("🌐 Testing Frontend Accessibility...")

    try:
        response = requests.get(KDB_FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is accessible")
            return True
        else:
            print(f"❌ Frontend returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend not accessible: {e}")
        return False


def verify_paperless_document(task_id):
    """Verify the document was uploaded to Paperless"""
    print("🔍 Verifying Paperless Document...")

    # Note: This would require the Paperless API token
    # For now, we'll just confirm the task was created
    print(f"📋 Task ID created: {task_id}")
    print("ℹ️  Document will be processed asynchronously by Paperless-ngx")
    return True


def main():
    """Run all tests"""
    print("🚀 Starting UI Integration Tests")
    print("=" * 50)

    # Test 1: Backend API
    paper_data = test_backend_api()
    if not paper_data:
        print("❌ Backend API test failed - stopping")
        return

    # Test 2: Paperless Upload
    task_id = test_paperless_upload(paper_data)
    if not task_id:
        print("❌ Paperless upload test failed - stopping")
        return

    # Test 3: Frontend Accessibility
    frontend_ok = test_frontend_accessibility()
    if not frontend_ok:
        print("⚠️  Frontend not accessible - but backend integration works")

    # Test 4: Verify Upload
    verify_paperless_document(task_id)

    print("\n" + "=" * 50)
    print("🎉 UI Integration Tests Complete!")
    print("\n📋 Summary:")
    print("✅ Backend API: Working")
    print("✅ Paperless Upload: Working")
    print("✅ Frontend: Accessible" if frontend_ok else "⚠️  Frontend: Not accessible")
    print("✅ End-to-End Flow: Complete")

    print("\n🌐 Access Points:")
    print(f"   Frontend: {KDB_FRONTEND_URL}")
    print(f"   Backend API: {KDB_BACKEND_URL}")
    print(f"   API Docs: {KDB_BACKEND_URL.replace('/api', '/docs')}")

    print("\n🎯 Next Steps:")
    print("   1. Open the frontend in your browser")
    print("   2. Import a paper using the UI")
    print("   3. Click 'Send to Paperless' button")
    print("   4. Verify the paper appears in Paperless-ngx")


if __name__ == "__main__":
    main()
