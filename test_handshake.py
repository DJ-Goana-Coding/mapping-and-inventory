"""
Test script for Pioneer Trader Grand Handshake Protocol
"""

import os
from bridge_protocol import PioneerBridge


def test_handshake():
    """Test the Pioneer Trader handshake protocol"""
    print("🧪 [T.I.A.] Testing Grand Handshake Protocol...")
    print("=" * 60)
    
    # Check environment variables
    pioneer_url = os.getenv("PIONEER_TRADER_URL")
    auth_token = os.getenv("PIONEER_AUTH_TOKEN")
    
    print(f"📍 PIONEER_TRADER_URL: {'✅ Set' if pioneer_url else '❌ Not set'}")
    print(f"🔑 PIONEER_AUTH_TOKEN: {'✅ Set' if auth_token else '❌ Not set'}")
    print()
    
    if not pioneer_url or not auth_token:
        print("⚠️  Required environment variables not set!")
        print("   Set PIONEER_TRADER_URL and PIONEER_AUTH_TOKEN before testing.")
        return False
    
    # Initialize bridge
    bridge = PioneerBridge()
    
    # Fetch status
    result = bridge.fetch_pioneer_status()
    
    print()
    print("=" * 60)
    print("HANDSHAKE RESULT:")
    print("=" * 60)
    
    if result.get("success"):
        print("✅ Handshake successful!")
        print(f"   Timestamp: {result.get('timestamp')}")
        print(f"   Wallet: {result['data'].get('wallet')}")
        print(f"   Equity: {result['data'].get('equity')}")
        print(f"   Status: {result['data'].get('status')}")
        print(f"   Slots: {len(result['data'].get('slots', {}))}")
        
        # Display slots
        slots = result['data'].get('slots', {})
        if slots:
            print("\n   Slot Details:")
            for slot_id, slot_data in slots.items():
                print(f"     Slot {slot_id}: {slot_data.get('type', 'UNKNOWN')} - {slot_data.get('status', 'INACTIVE')}")
        
        # Test shadow archive
        print("\n💾 Testing shadow archive sync...")
        bridge.sync_to_shadow_archive(result)
        print("✅ Shadow archive test complete")
        
    else:
        print(f"❌ Handshake failed: {result.get('error')}")
        print(f"   Timestamp: {result.get('timestamp')}")
    
    print("=" * 60)
    
    return result.get("success", False)


if __name__ == "__main__":
    success = test_handshake()
    exit(0 if success else 1)
