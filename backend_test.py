#!/usr/bin/env python3
"""
Comprehensive test script for Aquila S1000D-AI backend system.
"""

import os
import json
import base64
import time
import requests
from PIL import Image
import io
import sys
from pprint import pprint
import logging

import pytest

if not os.getenv("AQUILA_INTEGRATION_TESTS"):
    pytest.skip("Skipping backend integration tests", allow_module_level=True)

logger = logging.getLogger(__name__)

# API Base URL
API_BASE_URL = "http://localhost:8001/api"

# API Keys (read from environment if needed)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# Authentication token
AUTH_TOKEN = None

# Test data
SAMPLE_TEXT = """
The hydraulic system of the aircraft provides power for the operation of the landing gear, 
flaps, and brakes. The system consists of a main pump, an auxiliary pump, a reservoir, 
accumulators, and various control valves. The main pump is driven by the engine and 
provides pressure during normal operation. The auxiliary pump is electrically driven and 
serves as a backup in case of main pump failure. The reservoir stores hydraulic fluid and 
provides for thermal expansion. The accumulators store hydraulic pressure and dampen 
pressure fluctuations in the system.
"""

# Create a simple test image (a red square)
def create_test_image():
    img = Image.new('RGB', (100, 100), color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    return img_byte_arr.getvalue()

# Convert image to base64
def image_to_base64(image_data):
    return base64.b64encode(image_data).decode('utf-8')

# Helper function to get auth headers
def get_auth_headers():
    if AUTH_TOKEN:
        return {"Authorization": f"Bearer {AUTH_TOKEN}"}
    return {}

# Authentication function
def authenticate():
    global AUTH_TOKEN
    logger.warning("\n=== Authenticating ===\n")
    
    # First, register a test user
    try:
        response = requests.post(
            "http://localhost:8001/auth/register",
            data={"username": "testuser", "password": "testpass123"}
        )
        if response.status_code == 200:
            print_test_result("User Registration", True, response.json())
        else:
            print_test_result("User Registration", False, response.json())
    except Exception as e:
        print_test_result("User Registration", False, error=str(e))
    
    # Login to get token
    try:
        response = requests.post(
            "http://localhost:8001/auth/token",
            data={"username": "testuser", "password": "testpass123"}
        )
        if response.status_code == 200:
            AUTH_TOKEN = response.json()["access_token"]
            print_test_result("User Login", True, {"token_received": True})
            return True
        else:
            print_test_result("User Login", False, response.json())
            return False
    except Exception as e:
        print_test_result("User Login", False, error=str(e))
        return False
def print_test_result(test_name, success, response=None, error=None):
    if success:
        logger.warning(f"✅ {test_name}: PASSED")
        if response:
            logger.warning(f"   Response: {response}")
    else:
        logger.error(f"❌ {test_name}: FAILED")
        if error:
            logger.error(f"   Error: {error}")
        if response:
            logger.error(f"   Response: {response}")
    logger.warning("-" * 80)

# 1. Health Check & Basic APIs
def test_health_check():
    logger.warning("\n=== Testing Health Check & Basic APIs ===\n")
    
    # Test root endpoint
    try:
        response = requests.get(f"{API_BASE_URL}/")
        print_test_result("Root Endpoint", response.status_code == 200, response.json())
    except Exception as e:
        print_test_result("Root Endpoint", False, error=str(e))
    
    # Test health check endpoint
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print_test_result("Health Check", response.status_code == 200, response.json())
    except Exception as e:
        print_test_result("Health Check", False, error=str(e))

# 2. AI Provider Configuration
def test_provider_configuration():
    logger.warning("\n=== Testing AI Provider Configuration ===\n")
    
    # Get available providers
    try:
        response = requests.get(f"{API_BASE_URL}/providers", headers=get_auth_headers())
        print_test_result("Get Providers", response.status_code == 200, response.json())
    except Exception as e:
        print_test_result("Get Providers", False, error=str(e))
    
    # Test switching to OpenAI
    try:
        response = requests.post(
            f"{API_BASE_URL}/providers/set",
            params={"text_provider": "openai", "vision_provider": "openai"},
            headers=get_auth_headers()
        )
        print_test_result("Set Provider to OpenAI", response.status_code == 200, response.json())
    except Exception as e:
        print_test_result("Set Provider to OpenAI", False, error=str(e))
    
    # Test switching to Anthropic
    try:
        response = requests.post(
            f"{API_BASE_URL}/providers/set",
            params={"text_provider": "anthropic", "vision_provider": "anthropic"},
            headers=get_auth_headers()
        )
        print_test_result("Set Provider to Anthropic", response.status_code == 200, response.json())
    except Exception as e:
        print_test_result("Set Provider to Anthropic", False, error=str(e))
    
    # Switch back to OpenAI for subsequent tests
    try:
        response = requests.post(
            f"{API_BASE_URL}/providers/set",
            params={"text_provider": "openai", "vision_provider": "openai"},
            headers=get_auth_headers()
        )
        print_test_result("Reset Provider to OpenAI", response.status_code == 200, response.json())
    except Exception as e:
        print_test_result("Reset Provider to OpenAI", False, error=str(e))

# 3. AI Provider Testing
def test_ai_providers():
    logger.warning("\n=== Testing AI Provider Capabilities ===\n")
    
    # Test text processing with OpenAI
    try:
        response = requests.post(
            f"{API_BASE_URL}/test/text",
            params={"task_type": "classify", "text": SAMPLE_TEXT},
            headers=get_auth_headers()
        )
        print_test_result("OpenAI Text Classification", response.status_code == 200, response.json())
    except Exception as e:
        print_test_result("OpenAI Text Classification", False, error=str(e))
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/test/text",
            params={"task_type": "extract", "text": SAMPLE_TEXT},
            headers=get_auth_headers()
        )
        print_test_result("OpenAI Text Extraction", response.status_code == 200, response.json())
    except Exception as e:
        print_test_result("OpenAI Text Extraction", False, error=str(e))
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/test/text",
            params={"task_type": "rewrite", "text": SAMPLE_TEXT},
            headers=get_auth_headers()
        )
        print_test_result("OpenAI Text Rewrite", response.status_code == 200, response.json())
    except Exception as e:
        print_test_result("OpenAI Text Rewrite", False, error=str(e))
    
    # Test vision processing with OpenAI
    test_image = create_test_image()
    base64_image = image_to_base64(test_image)
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/test/vision",
            params={"task_type": "caption", "image_data": base64_image},
            headers=get_auth_headers()
        )
        print_test_result("OpenAI Vision Caption", response.status_code == 200, response.json())
    except Exception as e:
        print_test_result("OpenAI Vision Caption", False, error=str(e))
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/test/vision",
            params={"task_type": "objects", "image_data": base64_image},
            headers=get_auth_headers()
        )
        print_test_result("OpenAI Vision Objects", response.status_code == 200, response.json())
    except Exception as e:
        print_test_result("OpenAI Vision Objects", False, error=str(e))
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/test/vision",
            params={"task_type": "hotspots", "image_data": base64_image},
            headers=get_auth_headers()
        )
        print_test_result("OpenAI Vision Hotspots", response.status_code == 200, response.json())
    except Exception as e:
        print_test_result("OpenAI Vision Hotspots", False, error=str(e))
    
    # Switch to Anthropic and test
    try:
        requests.post(
            f"{API_BASE_URL}/providers/set",
            params={"text_provider": "anthropic", "vision_provider": "anthropic"},
            headers=get_auth_headers()
        )
        
        # Test text processing with Anthropic
        response = requests.post(
            f"{API_BASE_URL}/test/text",
            params={"task_type": "classify", "text": SAMPLE_TEXT},
            headers=get_auth_headers()
        )
        print_test_result("Anthropic Text Classification", response.status_code == 200, response.json())
    except Exception as e:
        print_test_result("Anthropic Text Classification", False, error=str(e))
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/test/vision",
            params={"task_type": "caption", "image_data": base64_image},
            headers=get_auth_headers()
        )
        print_test_result("Anthropic Vision Caption", response.status_code == 200, response.json())
    except Exception as e:
        print_test_result("Anthropic Vision Caption", False, error=str(e))
    
    # Switch back to OpenAI for subsequent tests
    try:
        requests.post(
            f"{API_BASE_URL}/providers/set",
            params={"text_provider": "openai", "vision_provider": "openai"},
            headers=get_auth_headers()
        )
    except Exception:
        pass

# 4. Document Management
def test_document_management():
    logger.warning("\n=== Testing Document Management ===\n")
    
    # Test document upload
    test_image = create_test_image()
    files = {'file': ('test_image.jpg', test_image, 'image/jpeg')}
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/documents/upload",
            files=files,
            headers=get_auth_headers()
        )
        print_test_result("Document Upload", response.status_code == 200, response.json())
        document_id = response.json().get('document_id')
    except Exception as e:
        print_test_result("Document Upload", False, error=str(e))
        document_id = None
    
    if not document_id:
        logger.warning("Cannot continue document tests without a valid document ID")
        return None
    
    # Test get documents
    try:
        response = requests.get(f"{API_BASE_URL}/documents", headers=get_auth_headers())
        print_test_result("Get Documents", response.status_code == 200, 
                         f"Found {len(response.json())} documents")
    except Exception as e:
        print_test_result("Get Documents", False, error=str(e))
    
    # Test get specific document
    try:
        response = requests.get(f"{API_BASE_URL}/documents/{document_id}", headers=get_auth_headers())
        print_test_result("Get Document", response.status_code == 200, response.json())
    except Exception as e:
        print_test_result("Get Document", False, error=str(e))
    
    # Test document processing
    try:
        response = requests.post(f"{API_BASE_URL}/documents/{document_id}/process", headers=get_auth_headers())
        print_test_result("Process Document", response.status_code == 200, response.json())
        
        # Extract data module IDs for later tests
        data_modules = response.json().get('modules', [])
        dmc_list = [dm.get('dmc') for dm in data_modules]
        return dmc_list
    except Exception as e:
        print_test_result("Process Document", False, error=str(e))
        return None

# 5. Data Module Management
def test_data_module_management(dmc_list):
    logger.warning("\n=== Testing Data Module Management ===\n")
    
    if not dmc_list:
        logger.warning("Cannot test data modules without valid DMC list")
        return
    
    # Test get all data modules
    try:
        response = requests.get(f"{API_BASE_URL}/data-modules", headers=get_auth_headers())
        print_test_result("Get Data Modules", response.status_code == 200, 
                         f"Found {len(response.json())} data modules")
    except Exception as e:
        print_test_result("Get Data Modules", False, error=str(e))
    
    # Test get specific data module
    dmc = dmc_list[0]
    try:
        response = requests.get(f"{API_BASE_URL}/data-modules/{dmc}", headers=get_auth_headers())
        print_test_result(f"Get Data Module {dmc}", response.status_code == 200, response.json())
    except Exception as e:
        print_test_result(f"Get Data Module {dmc}", False, error=str(e))
    
    # Test update data module
    try:
        update_data = {
            "title": "Updated Test Module",
            "content": "This is updated content for testing"
        }
        response = requests.put(
            f"{API_BASE_URL}/data-modules/{dmc}",
            json=update_data,
            headers=get_auth_headers()
        )
        print_test_result(f"Update Data Module {dmc}", response.status_code == 200, response.json())
    except Exception as e:
        print_test_result(f"Update Data Module {dmc}", False, error=str(e))
    
    # Test validate data module
    try:
        response = requests.post(f"{API_BASE_URL}/validate/{dmc}", headers=get_auth_headers())
        print_test_result(f"Validate Data Module {dmc}", response.status_code == 200, response.json())
    except Exception as e:
        print_test_result(f"Validate Data Module {dmc}", False, error=str(e))

    # Test export data module (XML)
    try:
        response = requests.get(f"{API_BASE_URL}/data-modules/{dmc}/export?format=xml", headers=get_auth_headers())
        print_test_result(f"Export Data Module {dmc} as XML", response.status_code == 200, 
                         f"XML content length: {len(response.content)} bytes")
    except Exception as e:
        print_test_result(f"Export Data Module {dmc} as XML", False, error=str(e))

# 6. ICN Management
def test_icn_management():
    logger.warning("\n=== Testing ICN Management ===\n")
    
    # Test get all ICNs
    try:
        response = requests.get(f"{API_BASE_URL}/icns", headers=get_auth_headers())
        print_test_result("Get ICNs", response.status_code == 200, 
                         f"Found {len(response.json())} ICNs")
        
        if len(response.json()) > 0:
            icn_id = response.json()[0].get('icn_id')
        else:
            icn_id = None
    except Exception as e:
        print_test_result("Get ICNs", False, error=str(e))
        icn_id = None
    
    if not icn_id:
        logger.warning("Cannot continue ICN tests without a valid ICN ID")
        return
    
    # Test get specific ICN
    try:
        response = requests.get(f"{API_BASE_URL}/icns/{icn_id}", headers=get_auth_headers())
        print_test_result(f"Get ICN {icn_id}", response.status_code == 200, response.json())
    except Exception as e:
        print_test_result(f"Get ICN {icn_id}", False, error=str(e))
    
    # Test get ICN image
    try:
        response = requests.get(f"{API_BASE_URL}/icns/{icn_id}/image", headers=get_auth_headers())
        print_test_result(f"Get ICN Image {icn_id}", 
                         response.status_code == 200, 
                         f"Image size: {len(response.content)} bytes")
    except Exception as e:
        print_test_result(f"Get ICN Image {icn_id}", False, error=str(e))
    
    # Test update ICN
    try:
        update_data = {
            "caption": "Updated test caption for ICN"
        }
        response = requests.put(
            f"{API_BASE_URL}/icns/{icn_id}",
            json=update_data,
            headers=get_auth_headers()
        )
        print_test_result(f"Update ICN {icn_id}", response.status_code == 200, response.json())
    except Exception as e:
        print_test_result(f"Update ICN {icn_id}", False, error=str(e))

# 7. Publication Module Management
def test_publication_module_management(dmc_list):
    logger.warning("\n=== Testing Publication Module Management ===\n")
    
    if not dmc_list:
        logger.warning("Cannot test publication modules without valid DMC list")
        return
    
    # Test create publication module
    pm_code = f"PMC-AQUILA-TEST-{int(time.time())}"
    try:
        pm_data = {
            "pm_code": pm_code,
            "title": "Test Publication Module",
            "dm_list": dmc_list,
            "structure": {
                "chapters": [
                    {
                        "title": "Chapter 1",
                        "sections": [
                            {
                                "title": "Section 1",
                                "dm_refs": dmc_list
                            }
                        ]
                    }
                ]
            }
        }
        response = requests.post(
            f"{API_BASE_URL}/publication-modules",
            json=pm_data,
            headers=get_auth_headers()
        )
        print_test_result("Create Publication Module", response.status_code == 200, response.json())
    except Exception as e:
        print_test_result("Create Publication Module", False, error=str(e))
    
    # Test get all publication modules
    try:
        response = requests.get(f"{API_BASE_URL}/publication-modules", headers=get_auth_headers())
        print_test_result("Get Publication Modules", response.status_code == 200, 
                         f"Found {len(response.json())} publication modules")
    except Exception as e:
        print_test_result("Get Publication Modules", False, error=str(e))
    
    # Test get specific publication module
    try:
        response = requests.get(f"{API_BASE_URL}/publication-modules/{pm_code}", headers=get_auth_headers())
        print_test_result(f"Get Publication Module {pm_code}", response.status_code == 200, response.json())
    except Exception as e:
        print_test_result(f"Get Publication Module {pm_code}", False, error=str(e))
    
    # Test publish publication module
    try:
        publish_options = {
            "formats": ["xml", "pdf"],
            "variants": ["verbatim", "ste"],
            "include_illustrations": True
        }
        response = requests.post(
            f"{API_BASE_URL}/publication-modules/{pm_code}/publish",
            json=publish_options,
            headers=get_auth_headers()
        )
        print_test_result(f"Publish Publication Module {pm_code}", response.status_code == 200, response.json())
    except Exception as e:
        print_test_result(f"Publish Publication Module {pm_code}", False, error=str(e))

def main():
    logger.warning("\n" + "=" * 80)
    logger.warning("AQUILA S1000D-AI BACKEND TEST SUITE")
    logger.warning("=" * 80 + "\n")
    
    # Authenticate first
    if not authenticate():
        logger.error("Authentication failed. Cannot continue with tests.")
        return
    
    # Run all tests
    test_health_check()
    test_provider_configuration()
    test_ai_providers()
    dmc_list = test_document_management()
    if dmc_list:
        test_data_module_management(dmc_list)
        test_publication_module_management(dmc_list)
    test_icn_management()
    
    logger.warning("\n" + "=" * 80)
    logger.warning("TEST SUITE COMPLETED")
    logger.warning("=" * 80 + "\n")

if __name__ == "__main__":
    main()