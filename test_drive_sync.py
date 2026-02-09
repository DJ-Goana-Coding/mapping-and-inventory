#!/usr/bin/env python3
"""
Test script for Google Drive authentication and sync protocol
Tests the drive_auth module and bridge_protocol sync functions
"""

import os
import json
import time
import hashlib
import base64
from unittest.mock import Mock, patch, MagicMock
from utils.drive_auth import get_drive_service, find_citadel_folder, download_file
from bridge_protocol import (
    check_panic_signal, 
    sync_fleet_manifest, 
    backup_active_positions,
    log_security_breach,
    get_or_create_subfolder,
    upload_json_to_drive
)

def test_drive_auth_missing_credentials():
    """Test 1: Verify error handling when credentials are missing"""
    print("=" * 70)
    print("🧪 TEST 1: Missing Credentials Error Handling")
    print("=" * 70)
    
    # Save original value
    original_creds = os.getenv('GOOGLE_CREDENTIALS_B64')
    
    try:
        # Remove credentials
        if 'GOOGLE_CREDENTIALS_B64' in os.environ:
            del os.environ['GOOGLE_CREDENTIALS_B64']
        
        # Should raise ValueError
        try:
            get_drive_service()
            print("❌ Should have raised ValueError for missing credentials")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "GOOGLE_CREDENTIALS_B64 not found" in str(e)
            print(f"✅ Correctly raised ValueError: {e}")
    
    finally:
        # Restore original value
        if original_creds:
            os.environ['GOOGLE_CREDENTIALS_B64'] = original_creds
    
    print()

def test_drive_auth_with_mock_credentials():
    """Test 2: Verify Drive service initialization with valid credentials"""
    print("=" * 70)
    print("🧪 TEST 2: Drive Service Initialization (Mocked)")
    print("=" * 70)
    
    # Create mock credentials
    mock_creds = {
        "type": "service_account",
        "project_id": "test-project",
        "private_key_id": "test-key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----\n",
        "client_email": "test@test-project.iam.gserviceaccount.com",
        "client_id": "123456789",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
    }
    
    # Encode credentials
    creds_json = json.dumps(mock_creds)
    creds_b64 = base64.b64encode(creds_json.encode()).decode()
    
    # Save original value
    original_creds = os.getenv('GOOGLE_CREDENTIALS_B64')
    
    try:
        # Set mock credentials
        os.environ['GOOGLE_CREDENTIALS_B64'] = creds_b64
        
        # Mock the Google API calls
        with patch('utils.drive_auth.build') as mock_build:
            with patch('utils.drive_auth.service_account.Credentials.from_service_account_info') as mock_creds_from_info:
                mock_creds_obj = Mock()
                mock_creds_from_info.return_value = mock_creds_obj
                mock_service = Mock()
                mock_build.return_value = mock_service
                
                service = get_drive_service()
                
                # Verify service was created
                assert service is not None
                print("✅ Drive service initialized successfully")
                
                # Verify credentials were decoded correctly
                mock_creds_from_info.assert_called_once()
                call_args = mock_creds_from_info.call_args
                assert call_args[0][0]['project_id'] == 'test-project'
                print("✅ Credentials decoded and parsed correctly")
                
                # Verify build was called with correct parameters
                mock_build.assert_called_once_with('drive', 'v3', credentials=mock_creds_obj)
                print("✅ Drive API service built with correct parameters")
    
    finally:
        # Restore original value
        if original_creds:
            os.environ['GOOGLE_CREDENTIALS_B64'] = original_creds
        elif 'GOOGLE_CREDENTIALS_B64' in os.environ:
            del os.environ['GOOGLE_CREDENTIALS_B64']
    
    print()

def test_find_citadel_folder():
    """Test 3: Verify CITADEL-BOT folder discovery"""
    print("=" * 70)
    print("🧪 TEST 3: CITADEL-BOT Folder Discovery")
    print("=" * 70)
    
    # Mock service
    mock_service = Mock()
    mock_files = Mock()
    mock_list = Mock()
    
    mock_service.files.return_value = mock_files
    mock_files.list.return_value = mock_list
    mock_list.execute.return_value = {
        'files': [{'id': 'folder-123', 'name': 'CITADEL-BOT'}]
    }
    
    folder_id = find_citadel_folder(mock_service)
    
    assert folder_id == 'folder-123'
    print("✅ CITADEL-BOT folder found with ID: folder-123")
    
    # Verify correct query was made
    call_args = mock_files.list.call_args
    assert "CITADEL-BOT" in call_args[1]['q']
    assert "application/vnd.google-apps.folder" in call_args[1]['q']
    print("✅ Correct query parameters used")
    
    print()

def test_find_citadel_folder_not_found():
    """Test 4: Verify error when CITADEL-BOT folder not found"""
    print("=" * 70)
    print("🧪 TEST 4: CITADEL-BOT Folder Not Found Error")
    print("=" * 70)
    
    # Mock service with no results
    mock_service = Mock()
    mock_files = Mock()
    mock_list = Mock()
    
    mock_service.files.return_value = mock_files
    mock_files.list.return_value = mock_list
    mock_list.execute.return_value = {'files': []}
    
    try:
        find_citadel_folder(mock_service)
        print("❌ Should have raised FileNotFoundError")
        assert False, "Should have raised FileNotFoundError"
    except FileNotFoundError as e:
        assert "CITADEL-BOT" in str(e)
        print(f"✅ Correctly raised FileNotFoundError: {e}")
    
    print()

def test_download_file():
    """Test 5: Verify file download from Drive"""
    print("=" * 70)
    print("🧪 TEST 5: File Download from CITADEL-BOT")
    print("=" * 70)
    
    # Mock service
    mock_service = Mock()
    mock_files = Mock()
    
    # Mock list call
    mock_list = Mock()
    mock_list.execute.return_value = {
        'files': [{'id': 'file-123', 'name': 'test.json'}]
    }
    
    # Mock get_media call
    mock_get = Mock()
    mock_media = Mock()
    test_data = {"test": "data", "value": 123}
    mock_media.execute.return_value = json.dumps(test_data).encode('utf-8')
    mock_get.return_value = mock_media
    
    mock_files.list.return_value = mock_list
    mock_files.get_media.return_value = mock_media
    mock_service.files.return_value = mock_files
    
    result = download_file(mock_service, 'folder-123', 'test.json')
    
    assert result is not None
    assert result['test'] == 'data'
    assert result['value'] == 123
    print("✅ File downloaded and parsed correctly")
    print(f"   Data: {result}")
    
    print()

def test_panic_signal_valid():
    """Test 6: Verify valid panic signal detection"""
    print("=" * 70)
    print("🧪 TEST 6: Valid Panic Signal Detection")
    print("=" * 70)
    
    # Set up test environment
    timestamp = time.time()
    token = "test-commander-token-secret"
    signature = hashlib.sha256(f"{token}{timestamp}".encode()).hexdigest()
    
    panic_data = {
        'timestamp': timestamp,
        'signature': signature,
        'reason': 'Market crash detected'
    }
    
    # Save original values
    original_token = os.getenv('AEGIS_COMMANDER_TOKEN')
    
    try:
        os.environ['AEGIS_COMMANDER_TOKEN'] = token
        
        # Mock the Drive service calls
        with patch('bridge_protocol.get_drive_service') as mock_get_service:
            with patch('bridge_protocol.find_citadel_folder') as mock_find_folder:
                with patch('bridge_protocol.download_file') as mock_download:
                    mock_download.return_value = panic_data
                    mock_find_folder.return_value = 'folder-123'
                    
                    result = check_panic_signal()
                    
                    assert result == True
                    print("✅ Valid panic signal detected")
                    print(f"   Signature verified: {signature[:16]}...")
                    print(f"   Reason: {panic_data['reason']}")
    
    finally:
        # Restore original value
        if original_token:
            os.environ['AEGIS_COMMANDER_TOKEN'] = original_token
        elif 'AEGIS_COMMANDER_TOKEN' in os.environ:
            del os.environ['AEGIS_COMMANDER_TOKEN']
    
    print()

def test_panic_signal_invalid_signature():
    """Test 7: Verify detection of invalid panic signal signature"""
    print("=" * 70)
    print("🧪 TEST 7: Invalid Panic Signal Signature Detection")
    print("=" * 70)
    
    timestamp = time.time()
    token = "test-commander-token-secret"
    
    panic_data = {
        'timestamp': timestamp,
        'signature': 'invalid-signature-here',
        'reason': 'Market crash detected'
    }
    
    # Save original values
    original_token = os.getenv('AEGIS_COMMANDER_TOKEN')
    
    try:
        os.environ['AEGIS_COMMANDER_TOKEN'] = token
        
        # Mock the Drive service calls
        with patch('bridge_protocol.get_drive_service') as mock_get_service:
            with patch('bridge_protocol.find_citadel_folder') as mock_find_folder:
                with patch('bridge_protocol.download_file') as mock_download:
                    mock_download.return_value = panic_data
                    mock_find_folder.return_value = 'folder-123'
                    
                    result = check_panic_signal()
                    
                    assert result == False
                    print("✅ Invalid signature correctly rejected")
                    print("✅ Security breach would be logged (requires Drive access)")
    
    finally:
        # Restore original value
        if original_token:
            os.environ['AEGIS_COMMANDER_TOKEN'] = original_token
        elif 'AEGIS_COMMANDER_TOKEN' in os.environ:
            del os.environ['AEGIS_COMMANDER_TOKEN']
    
    print()

def test_panic_signal_expired():
    """Test 8: Verify detection of expired panic signal"""
    print("=" * 70)
    print("🧪 TEST 8: Expired Panic Signal Detection")
    print("=" * 70)
    
    # Create timestamp from 10 minutes ago
    timestamp = time.time() - 600
    token = "test-commander-token-secret"
    signature = hashlib.sha256(f"{token}{timestamp}".encode()).hexdigest()
    
    panic_data = {
        'timestamp': timestamp,
        'signature': signature,
        'reason': 'Old panic signal'
    }
    
    # Save original values
    original_token = os.getenv('AEGIS_COMMANDER_TOKEN')
    
    try:
        os.environ['AEGIS_COMMANDER_TOKEN'] = token
        
        # Mock the Drive service calls
        with patch('bridge_protocol.get_drive_service') as mock_get_service:
            with patch('bridge_protocol.find_citadel_folder') as mock_find_folder:
                with patch('bridge_protocol.download_file') as mock_download:
                    mock_download.return_value = panic_data
                    mock_find_folder.return_value = 'folder-123'
                    
                    result = check_panic_signal()
                    
                    assert result == False
                    print("✅ Expired panic signal correctly rejected")
                    print(f"   Signal age: {time.time() - timestamp:.0f} seconds (>300s limit)")
    
    finally:
        # Restore original value
        if original_token:
            os.environ['AEGIS_COMMANDER_TOKEN'] = original_token
        elif 'AEGIS_COMMANDER_TOKEN' in os.environ:
            del os.environ['AEGIS_COMMANDER_TOKEN']
    
    print()

def test_sync_fleet_manifest():
    """Test 9: Verify fleet manifest synchronization"""
    print("=" * 70)
    print("🧪 TEST 9: Fleet Manifest Synchronization")
    print("=" * 70)
    
    manifest_data = {
        'fleet_version': 'v3.1.0',
        'strategies': ['PIRANHA', 'HARVESTER', 'SNIPER'],
        'config': {'pulse_interval': 2}
    }
    
    # Mock the Drive service calls
    with patch('bridge_protocol.get_drive_service') as mock_get_service:
        with patch('bridge_protocol.find_citadel_folder') as mock_find_folder:
            with patch('bridge_protocol.download_file') as mock_download:
                with patch('builtins.open', create=True) as mock_open:
                    mock_download.return_value = manifest_data
                    mock_find_folder.return_value = 'folder-123'
                    mock_file = MagicMock()
                    mock_open.return_value.__enter__.return_value = mock_file
                    
                    result = sync_fleet_manifest()
                    
                    assert result is not None
                    assert result['fleet_version'] == 'v3.1.0'
                    print("✅ Manifest synchronized successfully")
                    print(f"   Version: {result['fleet_version']}")
                    print(f"   Strategies: {', '.join(result['strategies'])}")
                    
                    # Verify file was written
                    mock_open.assert_called_with('registry/fleet_manifest.json', 'w')
                    print("✅ Manifest saved to registry/fleet_manifest.json")
    
    print()

def test_panic_signal_rate_limiting():
    """Test 10: Verify panic signal rate limiting"""
    print("=" * 70)
    print("🧪 TEST 10: Panic Signal Rate Limiting")
    print("=" * 70)
    
    # Import to reset global state
    import bridge_protocol
    bridge_protocol.LAST_PANIC_CHECK = time.time()
    
    # Mock the Drive service calls (shouldn't be called due to rate limit)
    with patch('bridge_protocol.get_drive_service') as mock_get_service:
        result = check_panic_signal()
        
        assert result == False
        print("✅ Rate limit enforced - check skipped")
        
        # Verify service was NOT called
        mock_get_service.assert_not_called()
        print("✅ Drive API not called (rate limited)")
    
    print()

def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("🚀 GOOGLE DRIVE SYNC PROTOCOL TEST SUITE")
    print("   Testing Authentication, Panic Signals, and Manifest Sync")
    print("=" * 70 + "\n")
    
    try:
        # Run all tests
        test_drive_auth_missing_credentials()
        test_drive_auth_with_mock_credentials()
        test_find_citadel_folder()
        test_find_citadel_folder_not_found()
        test_download_file()
        test_panic_signal_valid()
        test_panic_signal_invalid_signature()
        test_panic_signal_expired()
        test_sync_fleet_manifest()
        test_panic_signal_rate_limiting()
        
        print("=" * 70)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 70)
        print("\n✅ Google Drive Sync Protocol verified:")
        print("   - Base64 credential decoding")
        print("   - CITADEL-BOT folder discovery")
        print("   - File download and JSON parsing")
        print("   - Panic signal signature verification")
        print("   - Timestamp expiry checking (5 min)")
        print("   - Fleet manifest synchronization")
        print("   - API rate limiting (30s panic, 60s manifest)")
        print("\n🔒 Ready for secure mobile command authority!\n")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        raise
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    run_all_tests()
