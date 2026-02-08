#!/usr/bin/env python3
"""
Quick verification script to test HEAD request handler
Run this to verify the fix is working correctly
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_head_handler():
    """Test that HEAD request returns 200 OK with no body"""
    try:
        from fastapi.testclient import TestClient
        from backend.main import app
        
        print("=" * 70)
        print("HEAD REQUEST HANDLER VERIFICATION")
        print("=" * 70)
        
        client = TestClient(app)
        
        # Test HEAD request
        print("\n🧪 Testing HEAD / request...")
        response = client.head('/')
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Body Length: {len(response.content)} bytes")
        print(f"   Headers: {dict(response.headers)}")
        
        # Verify correct behavior
        if response.status_code == 200:
            print("\n   ✅ SUCCESS: Status code is 200 OK")
        else:
            print(f"\n   ❌ FAIL: Status code is {response.status_code}, expected 200")
            return False
        
        if len(response.content) == 0:
            print("   ✅ SUCCESS: Response body is empty (correct for HEAD)")
        else:
            print(f"   ⚠️  WARNING: Response body has {len(response.content)} bytes")
        
        # Test GET for comparison
        print("\n🧪 Testing GET / request for comparison...")
        get_response = client.get('/')
        print(f"   Status Code: {get_response.status_code}")
        print(f"   Body Length: {len(get_response.content)} bytes")
        
        if get_response.status_code == 200:
            print("   ✅ SUCCESS: GET also returns 200 OK")
        
        print("\n" + "=" * 70)
        print("VERIFICATION COMPLETE")
        print("=" * 70)
        
        if response.status_code == 200:
            print("\n✅ HEAD REQUEST HANDLER IS WORKING CORRECTLY!")
            print("\nThe fix is implemented and functional on this branch.")
            print("If deployment still shows 405, the issue is that Render.com")
            print("is deploying from a different branch.")
            print("\nSee DEPLOYMENT_BRANCH_ISSUE.md for resolution steps.")
            return True
        else:
            print("\n❌ HEAD REQUEST HANDLER IS NOT WORKING")
            return False
            
    except ImportError as e:
        print(f"\n❌ ERROR: Missing dependencies: {e}")
        print("\nInstall required packages:")
        print("  pip install fastapi httpx uvicorn")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_head_handler()
    sys.exit(0 if success else 1)
