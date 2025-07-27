#!/usr/bin/env python3
"""
Test script for the unified RunPod handler
"""

def test_handler_structure():
    """Test that the handler can be imported and has the right structure."""
    try:
        # Test import
        from runpod_handler import handler
        print("✅ Handler import successful")
        
        # Test basic structure
        test_event = {
            "input": {
                "operation": "get_kokoro_voices",
                "parameters": {}
            }
        }
        
        print(f"📝 Testing with event: {test_event}")
        
        # This should work without requiring models to be loaded
        # since get_kokoro_voices just returns available voices
        result = handler(test_event)
        print(f"✅ Handler call successful: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Handler test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_supported_operations():
    """Test that all supported operations are documented."""
    test_event = {
        "input": {}  # Missing operation
    }
    
    try:
        from runpod_handler import handler
        result = handler(test_event)
        
        if "supported_operations" in result:
            print(f"✅ Supported operations: {result['supported_operations']}")
            return True
        else:
            print(f"❌ No supported operations listed in error response: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Operation test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing unified RunPod handler...")
    
    print("\n1. Testing handler structure...")
    structure_ok = test_handler_structure()
    
    print("\n2. Testing supported operations...")
    operations_ok = test_supported_operations()
    
    if structure_ok and operations_ok:
        print("\n✅ All tests passed! Handler is ready for deployment.")
    else:
        print("\n❌ Some tests failed. Check the implementation.")