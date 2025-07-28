#!/usr/bin/env python3
"""
Test script for deployed RunPod serverless endpoint
Usage: python test_runpod_endpoint.py <ENDPOINT_URL>
"""

import sys
import json
import requests
import time
from typing import Dict, Any

def test_runpod_endpoint(endpoint_url: str) -> bool:
    """Test the deployed RunPod serverless endpoint."""
    
    if not endpoint_url:
        print("❌ Error: Please provide the RunPod serverless endpoint URL")
        print("Usage: python test_runpod_endpoint.py <ENDPOINT_URL>")
        return False
    
    print(f"🧪 Testing RunPod endpoint: {endpoint_url}")
    
    # Test cases
    test_cases = [
        {
            "name": "TTS - Kokoro Voices List",
            "payload": {
                "input": {
                    "operation": "get_kokoro_voices",
                    "parameters": {}
                }
            },
            "expected_keys": ["voices"]
        },
        {
            "name": "TTS - Kokoro Generation",
            "payload": {
                "input": {
                    "operation": "generate_kokoro_tts",
                    "parameters": {
                        "text": "Hello, this is a test of text-to-speech",
                        "voice": "af_heart",
                        "speed": 1.0
                    }
                }
            },
            "expected_keys": ["audio_url", "storage_url"]
        },
        {
            "name": "Storage - File Status",
            "payload": {
                "input": {
                    "operation": "file_status",
                    "parameters": {
                        "storage_key": "test-file.txt"
                    }
                }
            },
            "expected_keys": ["exists", "storage_key"]
        },
        {
            "name": "Utility - List Fonts",
            "payload": {
                "input": {
                    "operation": "list_fonts",
                    "parameters": {}
                }
            },
            "expected_keys": ["fonts", "total_count"]
        }
    ]
    
    success_count = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}/{total_tests}: {test_case['name']}")
        print(f"📤 Payload: {json.dumps(test_case['payload'], indent=2)}")
        
        try:
            # Send request
            response = requests.post(
                endpoint_url,
                json=test_case['payload'],
                headers={'Content-Type': 'application/json'},
                timeout=120  # 2 minutes timeout for serverless cold starts
            )
            
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"📥 Response: {json.dumps(result, indent=2)}")
                
                # Check for errors in response
                if "error" in result:
                    print(f"❌ Error in response: {result['error']}")
                else:
                    # Check expected keys
                    missing_keys = [key for key in test_case['expected_keys'] if key not in result]
                    if missing_keys:
                        print(f"⚠️  Missing expected keys: {missing_keys}")
                    else:
                        print("✅ Test passed!")
                        success_count += 1
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"📄 Response: {response.text}")
                
        except requests.exceptions.Timeout:
            print("❌ Request timed out (serverless cold start may take time)")
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    # Summary
    print(f"\n📈 Test Summary: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 All tests passed! RunPod endpoint is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")
        return False

def check_runpod_status(endpoint_url: str, job_id: str) -> Dict[str, Any]:
    """Check the status of a RunPod job."""
    status_url = f"{endpoint_url}/status/{job_id}"
    
    try:
        response = requests.get(status_url, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Status check failed: {response.status_code}"}
    except Exception as e:
        return {"error": f"Status check error: {e}"}

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("❌ Error: Please provide the RunPod serverless endpoint URL")
        print("Usage: python test_runpod_endpoint.py <ENDPOINT_URL>")
        print("\nExample:")
        print("python test_runpod_endpoint.py https://api.runpod.ai/v2/your-endpoint-id/runsync")
        sys.exit(1)
    
    endpoint_url = sys.argv[1]
    success = test_runpod_endpoint(endpoint_url)
    sys.exit(0 if success else 1)