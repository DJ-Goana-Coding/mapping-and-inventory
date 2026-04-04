#!/usr/bin/env python3
"""
🔐 CREDENTIAL VAULT INITIALIZATION
Initialize Quantum Vault with master password and populate email/GDrive accounts
"""

import os
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from security.core.quantum_vault import (
    QuantumVault,
    EmailCredentialManager,
    GDriveCredentialManager
)


def load_account_registry(registry_path: Path) -> dict:
    """Load unified account registry"""
    with open(registry_path, 'r') as f:
        return json.load(f)


def initialize_vault_with_master_password():
    """Initialize vault with operator's master password"""
    
    print("🔒 QUANTUM VAULT INITIALIZATION")
    print("=" * 60)
    
    # Check for master password in environment
    master_password = os.getenv('MASTER_PASSWORD')
    if not master_password:
        print("❌ MASTER_PASSWORD environment variable not set!")
        print("   This should be set in GitHub Secrets")
        return False
    
    print("✅ Master password loaded from environment")
    
    # Initialize vault
    vault_path = Path(__file__).parent.parent / "data" / "security" / "credentials.vault.enc"
    vault_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Vault location: {vault_path}")
    
    try:
        vault = QuantumVault(vault_path, master_key=master_password, use_env_key=False)
        print("✅ Quantum Vault initialized")
    except Exception as e:
        print(f"❌ Failed to initialize vault: {e}")
        return False
    
    # Load account registry
    registry_path = Path(__file__).parent.parent / "data" / "personal_archive" / "devices" / "unified_account_registry.json"
    
    if not registry_path.exists():
        print(f"❌ Account registry not found: {registry_path}")
        return False
    
    registry = load_account_registry(registry_path)
    print(f"✅ Loaded account registry: {registry['total_accounts']} accounts")
    
    # Initialize managers
    email_mgr = EmailCredentialManager(vault)
    gdrive_mgr = GDriveCredentialManager(vault)
    
    # Add email accounts
    print("\n📧 Adding email accounts...")
    emails = registry.get('unique_emails', [])
    
    for email in emails:
        # Determine provider from email domain
        if '@gmail.com' in email:
            provider = 'gmail'
        elif '@yahoo.com' in email:
            provider = 'yahoo'
        elif '@outlook.com' in email or '@hotmail.com' in email:
            provider = 'outlook'
        else:
            provider = 'custom'
        
        try:
            email_mgr.add_email_account(
                email=email,
                password=master_password,  # Using master password for all accounts
                provider=provider
            )
            print(f"   ✅ {email} ({provider})")
        except Exception as e:
            print(f"   ⚠️  {email}: {e}")
    
    # Add Google Drive accounts (Gmail accounts can access GDrive)
    print("\n☁️  Adding Google Drive accounts...")
    gmail_accounts = [email for email in emails if '@gmail.com' in email]
    
    for email in gmail_accounts:
        try:
            gdrive_mgr.add_gdrive_account(
                email=email,
                password=master_password
            )
            print(f"   ✅ {email}")
        except Exception as e:
            print(f"   ⚠️  {email}: {e}")
    
    # Save vault
    print("\n💾 Saving encrypted vault...")
    vault.save()
    
    # Generate audit log
    print("\n📊 Vault Statistics:")
    audit = vault.audit_log()
    print(f"   Total Credentials: {audit['total_credentials']}")
    print(f"   Email Accounts: {len(email_mgr.list_email_accounts())}")
    print(f"   GDrive Accounts: {len(gdrive_mgr.list_gdrive_accounts())}")
    
    print("\n✅ VAULT INITIALIZATION COMPLETE")
    print("\n🔐 Security Notes:")
    print("   - Vault encrypted with AES-256-GCM")
    print("   - Key derivation: PBKDF2-HMAC-SHA256 (600K iterations)")
    print("   - File permissions: 0o600 (owner read/write only)")
    print("   - Post-quantum ready architecture")
    print("\n⚠️  IMPORTANT:")
    print("   - Store MASTER_PASSWORD in GitHub Secrets")
    print("   - Never commit the vault file to git (.gitignore added)")
    print("   - Backup vault file securely")
    
    return True


def verify_vault_access():
    """Verify vault can be accessed"""
    print("\n🔍 VERIFYING VAULT ACCESS")
    print("=" * 60)
    
    master_password = os.getenv('MASTER_PASSWORD')
    if not master_password:
        print("❌ MASTER_PASSWORD not set")
        return False
    
    vault_path = Path(__file__).parent.parent / "data" / "security" / "credentials.vault.enc"
    
    if not vault_path.exists():
        print(f"❌ Vault not found: {vault_path}")
        return False
    
    try:
        vault = QuantumVault(vault_path, master_key=master_password, use_env_key=False)
        email_mgr = EmailCredentialManager(vault)
        
        accounts = email_mgr.list_email_accounts()
        print(f"✅ Vault accessible")
        print(f"   Email accounts: {len(accounts)}")
        
        if accounts:
            print(f"\n📧 Registered Email Accounts:")
            for email in accounts:
                print(f"   - {email}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to access vault: {e}")
        return False


def list_credentials():
    """List all credentials in vault"""
    print("\n📋 CREDENTIAL INVENTORY")
    print("=" * 60)
    
    master_password = os.getenv('MASTER_PASSWORD')
    if not master_password:
        print("❌ MASTER_PASSWORD not set")
        return
    
    vault_path = Path(__file__).parent.parent / "data" / "security" / "credentials.vault.enc"
    
    try:
        vault = QuantumVault(vault_path, master_key=master_password, use_env_key=False)
        
        all_creds = vault.list_credentials()
        print(f"Total credentials: {len(all_creds)}")
        
        for cred_id in all_creds:
            metadata = vault.get_metadata(cred_id)
            if metadata:
                print(f"\n  {cred_id}")
                print(f"    Created: {metadata.created_at}")
                print(f"    Accessed: {metadata.access_count} times")
                print(f"    Tags: {', '.join(metadata.tags)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Quantum Vault Credential Management")
    parser.add_argument(
        'action',
        choices=['init', 'verify', 'list'],
        help='Action to perform'
    )
    
    args = parser.parse_args()
    
    if args.action == 'init':
        success = initialize_vault_with_master_password()
        sys.exit(0 if success else 1)
    
    elif args.action == 'verify':
        success = verify_vault_access()
        sys.exit(0 if success else 1)
    
    elif args.action == 'list':
        list_credentials()
        sys.exit(0)
