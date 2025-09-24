#!/usr/bin/env python3
"""
Keyword Management System - Comprehensive Test
Tests all keyword management features end-to-end
"""

import requests
import json
import time

# Configuration
KDB_BACKEND_URL = "http://localhost:8000/api"
KDB_FRONTEND_URL = "http://localhost:5173"


def test_keyword_extraction():
    """Test AI-powered keyword extraction"""
    print("🤖 Testing AI Keyword Extraction...")

    # First import a paper
    import_payload = {
        "inputs": ["2301.12345"],
        "metadata": [{"importance": "high", "tag": "keyword-test"}]
    }

    response = requests.post(f"{KDB_BACKEND_URL}/import", json=import_payload)
    if response.status_code != 200:
        print(f"❌ Import failed: {response.status_code}")
        return None

    paper_data = response.json()["results"][0]["data"]["paper"]

    # Extract keywords
    keyword_payload = {"paper_data": paper_data}
    response = requests.post(
        f"{KDB_BACKEND_URL}/keywords/extract", json=keyword_payload)

    if response.status_code == 200:
        result = response.json()
        print(f"✅ Keyword extraction successful!")
        print(f"   Primary keywords: {len(result['primary_keywords'])}")
        print(f"   Secondary keywords: {len(result['secondary_keywords'])}")
        print(f"   Technical terms: {len(result['technical_terms'])}")
        print(f"   Domain tags: {len(result['domain_tags'])}")
        print(f"   Confidence: {result['confidence_score']:.2f}")
        print(f"   Method: {result['extraction_method']}")

        # Show sample keywords
        if result['primary_keywords']:
            print(f"   Sample primary: {result['primary_keywords'][:3]}")

        return result
    else:
        print(
            f"❌ Keyword extraction failed: {response.status_code} - {response.text}")
        return None


def test_keyword_validation():
    """Test keyword validation and normalization"""
    print("\n🔍 Testing Keyword Validation...")

    test_keywords = [
        "quantum computing",
        "machine learning",
        "invalid keyword with spaces and numbers 123",
        "quantum algorithm",
        "a",  # Too short
        "very long keyword that exceeds the maximum length limit and should be invalid",
        "IBM Qiskit",  # Technical term
        "Quantum Error Correction"  # Domain tag
    ]

    validation_payload = {"keywords": test_keywords}
    response = requests.post(
        f"{KDB_BACKEND_URL}/keywords/validate", json=validation_payload)

    if response.status_code == 200:
        result = response.json()
        print(f"✅ Keyword validation successful!")
        print(f"   Valid keywords: {len(result['valid_keywords'])}")
        print(f"   Invalid keywords: {len(result['invalid_keywords'])}")
        print(f"   Suggestions: {len(result['suggestions'])}")
        print(f"   Normalized: {len(result['normalized_keywords'])}")

        # Show details
        if result['valid_keywords']:
            print(f"   Valid: {result['valid_keywords']}")
        if result['invalid_keywords']:
            print(f"   Invalid: {result['invalid_keywords']}")
        if result['suggestions']:
            # Show first 2
            print(f"   Suggestions: {result['suggestions'][:2]}")

        return result
    else:
        print(
            f"❌ Keyword validation failed: {response.status_code} - {response.text}")
        return None


def test_domains_endpoint():
    """Test available domains and technical terms"""
    print("\n🏷️ Testing Domains Endpoint...")

    response = requests.get(f"{KDB_BACKEND_URL}/keywords/domains")

    if response.status_code == 200:
        result = response.json()
        print(f"✅ Domains endpoint successful!")
        print(f"   Available domains: {len(result['domains'])}")
        print(f"   Technical terms: {len(result['technical_terms'])}")

        # Show sample domains
        print(f"   Sample domains: {result['domains'][:5]}")
        print(f"   Sample technical terms: {result['technical_terms'][:5]}")

        return result
    else:
        print(
            f"❌ Domains endpoint failed: {response.status_code} - {response.text}")
        return None


def test_frontend_accessibility():
    """Test if frontend is accessible"""
    print("\n🌐 Testing Frontend Accessibility...")

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


def test_keyword_workflow():
    """Test complete keyword workflow"""
    print("\n🔄 Testing Complete Keyword Workflow...")

    # Step 1: Import paper
    print("   Step 1: Importing paper...")
    import_payload = {
        "inputs": ["2301.12345"],
        "metadata": [{"importance": "high", "tag": "workflow-test"}]
    }

    response = requests.post(f"{KDB_BACKEND_URL}/import", json=import_payload)
    if response.status_code != 200:
        print(f"   ❌ Import failed: {response.status_code}")
        return False

    paper_data = response.json()["results"][0]["data"]["paper"]
    print(f"   ✅ Paper imported: {paper_data['title'][:50]}...")

    # Step 2: Extract keywords
    print("   Step 2: Extracting keywords...")
    keyword_payload = {"paper_data": paper_data}
    response = requests.post(
        f"{KDB_BACKEND_URL}/keywords/extract", json=keyword_payload)

    if response.status_code != 200:
        print(f"   ❌ Keyword extraction failed: {response.status_code}")
        return False

    keywords_result = response.json()
    print(
        f"   ✅ Keywords extracted: {len(keywords_result['primary_keywords'])} primary")

    # Step 3: Validate extracted keywords
    print("   Step 3: Validating keywords...")
    all_keywords = keywords_result['primary_keywords'] + \
        keywords_result['secondary_keywords']
    validation_payload = {"keywords": all_keywords[:5]}  # Test first 5

    response = requests.post(
        f"{KDB_BACKEND_URL}/keywords/validate", json=validation_payload)
    if response.status_code != 200:
        print(f"   ❌ Validation failed: {response.status_code}")
        return False

    validation_result = response.json()
    print(
        f"   ✅ Keywords validated: {len(validation_result['valid_keywords'])} valid")

    # Step 4: Upload to Paperless with keywords
    print("   Step 4: Uploading to Paperless with keywords...")
    upload_payload = {
        "paper": paper_data,
        "metadata": {
            "importance": "high",
            "tag": "workflow-test",
            # Use top 3 keywords
            "keywords": keywords_result['primary_keywords'][:3]
        }
    }

    response = requests.post(
        f"{KDB_BACKEND_URL}/paperless/upload", json=upload_payload)
    if response.status_code != 200:
        print(f"   ❌ Paperless upload failed: {response.status_code}")
        return False

    upload_result = response.json()
    print(f"   ✅ Uploaded to Paperless: {upload_result['task_id'][:8]}...")

    return True


def main():
    """Run all keyword management tests"""
    print("🚀 Starting Keyword Management System Tests")
    print("=" * 60)

    # Test individual components
    extraction_result = test_keyword_extraction()
    validation_result = test_keyword_validation()
    domains_result = test_domains_endpoint()
    frontend_ok = test_frontend_accessibility()

    # Test complete workflow
    workflow_ok = test_keyword_workflow()

    print("\n" + "=" * 60)
    print("🎉 Keyword Management Tests Complete!")

    print("\n📋 Summary:")
    print(
        f"✅ AI Keyword Extraction: {'Working' if extraction_result else 'Failed'}")
    print(
        f"✅ Keyword Validation: {'Working' if validation_result else 'Failed'}")
    print(
        f"✅ Domains & Technical Terms: {'Working' if domains_result else 'Failed'}")
    print(
        f"✅ Frontend Accessibility: {'Working' if frontend_ok else 'Failed'}")
    print(f"✅ Complete Workflow: {'Working' if workflow_ok else 'Failed'}")

    print("\n🎯 Key Features:")
    print("   • AI-powered keyword extraction using GPT-4")
    print("   • Intelligent keyword validation and normalization")
    print("   • Quantum computing domain classification")
    print("   • Technical term recognition")
    print("   • Confidence scoring for extractions")
    print("   • Integration with Paperless-ngx upload")

    print("\n🌐 Access Points:")
    print(f"   Frontend: {KDB_FRONTEND_URL}")
    print(f"   Backend API: {KDB_BACKEND_URL}")
    print(f"   API Docs: {KDB_BACKEND_URL.replace('/api', '/docs')}")

    print("\n🎯 Next Steps:")
    print("   1. Open frontend and test keyword management UI")
    print("   2. Import papers and click 'Keywords' button")
    print("   3. Review AI-extracted keywords")
    print("   4. Validate and customize keywords")
    print("   5. Upload to Paperless with enhanced metadata")

    # Overall success
    all_tests_passed = all([
        extraction_result, validation_result, domains_result,
        frontend_ok, workflow_ok
    ])

    if all_tests_passed:
        print("\n🎉 All tests passed! Keyword Management System is fully functional!")
    else:
        print("\n⚠️ Some tests failed. Check the logs above for details.")


if __name__ == "__main__":
    main()
