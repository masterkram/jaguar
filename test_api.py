#!/usr/bin/env python3
"""
Simple test script for the Jaguar File Search API
"""

import requests
import json
import tempfile
import os
from pathlib import Path

# API base URL
BASE_URL = "http://localhost:8000"


def test_api_health():
    """Test if API is running"""
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ API Health Check: {response.status_code}")
        print(f"   Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ API Health Check failed: {e}")
        return False


def create_test_file():
    """Create a test text file"""
    content = """# Test Document

This is a test document for the Jaguar File Search API.

## Features
- Document processing with Unstructured
- Text search with ripgrep
- Metadata queries with jq
- File system search with find

## Sample Content
Machine learning is a subset of artificial intelligence.
Neural networks are a key component of deep learning.
Data science involves statistical analysis and visualization.

## Technical Details
- Python version: 3.13
- Framework: FastAPI
- Container: Docker
"""

    # Create temporary file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(content)
        return f.name


def test_file_upload():
    """Test file upload functionality"""
    print("\n📁 Testing File Upload...")

    test_file_path = create_test_file()

    try:
        with open(test_file_path, "rb") as f:
            files = {"file": ("test_document.txt", f, "text/plain")}
            response = requests.post(f"{BASE_URL}/upload/", files=files)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ File Upload: {response.status_code}")
            print(f"   File ID: {result['file_id']}")
            print(f"   Filename: {result['filename']}")
            print(f"   Processing Status: {result['processing_result']['status']}")
            return result["file_id"]
        else:
            print(f"❌ File Upload failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None

    except Exception as e:
        print(f"❌ File Upload failed: {e}")
        return None
    finally:
        # Clean up test file
        os.unlink(test_file_path)


def test_list_files():
    """Test file listing"""
    print("\n📋 Testing File Listing...")

    try:
        response = requests.get(f"{BASE_URL}/files/")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ File Listing: {response.status_code}")
            print(f"   Total files: {len(result['files'])}")
            return True
        else:
            print(f"❌ File Listing failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ File Listing failed: {e}")
        return False


def test_ripgrep_search(file_id=None):
    """Test ripgrep search"""
    print("\n🔍 Testing Ripgrep Search...")

    try:
        # Test 1: Search across all files
        params = {"pattern": "machine learning"}
        response = requests.get(f"{BASE_URL}/search/ripgrep/", params=params)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Ripgrep Search (all files): {response.status_code}")
            print(f"   Pattern: {result['pattern']}")
            print(f"   Total matches: {result['total_matches']}")
        else:
            print(f"❌ Ripgrep Search failed: {response.status_code}")

        # Test 2: Search specific file with context (if file_id provided)
        if file_id:
            params = {"pattern": "neural", "file_id": file_id, "context": 1}
            response = requests.get(f"{BASE_URL}/search/ripgrep/", params=params)

            if response.status_code == 200:
                result = response.json()
                print(f"✅ Ripgrep Search (specific file): {response.status_code}")
                print(f"   File ID: {result['file_id']}")
                print(f"   Total matches: {result['total_matches']}")
            else:
                print(
                    f"❌ Ripgrep Search (specific file) failed: {response.status_code}"
                )

    except Exception as e:
        print(f"❌ Ripgrep Search failed: {e}")


def test_find_search():
    """Test find search"""
    print("\n🔎 Testing Find Search...")

    try:
        params = {"name_pattern": "*.md", "file_type": "f"}
        response = requests.get(f"{BASE_URL}/search/find/", params=params)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Find Search: {response.status_code}")
            print(f"   Pattern: {result['search_parameters']['name_pattern']}")
            print(f"   Results count: {result['count']}")
        else:
            print(f"❌ Find Search failed: {response.status_code}")

    except Exception as e:
        print(f"❌ Find Search failed: {e}")


def test_jq_search(file_id):
    """Test jq search"""
    print("\n🔍 Testing JQ Search...")

    if not file_id:
        print("❌ JQ Search skipped: No file ID provided")
        return

    try:
        # Test extracting element count
        params = {"file_id": file_id, "jq_filter": "length"}
        response = requests.get(f"{BASE_URL}/search/jq/", params=params)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ JQ Search: {response.status_code}")
            print(f"   Filter: {result['jq_filter']}")
            print(f"   Result: {result['result']}")
        else:
            print(f"❌ JQ Search failed: {response.status_code}")
            print(f"   Error: {response.text}")

    except Exception as e:
        print(f"❌ JQ Search failed: {e}")


def main():
    """Run all tests"""
    print("🚀 Starting Jaguar API Tests\n")

    # Test API health
    if not test_api_health():
        print("\n❌ API is not running. Please start the service first.")
        print("   Run: docker-compose up --build")
        return

    # Test file upload
    file_id = test_file_upload()

    # Test file listing
    test_list_files()

    # Test search functions
    test_ripgrep_search(file_id)
    test_find_search()
    test_jq_search(file_id)

    print("\n🎉 All tests completed!")


if __name__ == "__main__":
    main()
