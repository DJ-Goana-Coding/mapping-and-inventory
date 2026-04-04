#!/usr/bin/env python3
"""
☁️ GOOGLE DRIVE HARVESTER
Access GDrive accounts from Quantum Vault and map data
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from security.core.quantum_vault import (
    QuantumVault,
    GDriveCredentialManager
)


class GDriveHarvester:
    """Harvest data from Google Drive accounts"""
    
    def __init__(self, vault: QuantumVault):
        self.vault = vault
        self.gdrive_mgr = GDriveCredentialManager(vault)
        self.harvest_results = []
    
    def check_account_access(self, email_address: str) -> Dict[str, Any]:
        """
        Check if GDrive account is accessible
        
        Note: This is a placeholder. Full implementation requires:
        1. Google API Client Library (google-api-python-client)
        2. OAuth2 authentication flow
        3. Service account or user consent
        
        For production:
        - Use rclone for filesystem-level access
        - Use Google Drive API for programmatic access
        - Use gdown for public file downloads
        """
        print(f"\n☁️  Checking: {email_address}")
        
        credential = self.gdrive_mgr.get_gdrive_account(email_address)
        
        if not credential:
            print(f"   ❌ Credentials not found")
            return {
                'email': email_address,
                'status': 'no_credentials',
                'accessible': False,
                'checked_at': datetime.utcnow().isoformat()
            }
        
        # For now, just verify credentials exist
        # Full implementation would connect to Drive API
        result = {
            'email': email_address,
            'status': 'credentials_available',
            'accessible': True,  # Marked as accessible if credentials exist
            'credential_type': 'password_auth',
            'has_oauth_tokens': bool(credential.get('oauth_tokens')),
            'has_service_account': bool(credential.get('service_account_key')),
            'scopes_configured': credential.get('scopes', []),
            'checked_at': datetime.utcnow().isoformat(),
            'note': 'Requires OAuth2 flow or rclone configuration for actual access'
        }
        
        print(f"   ✅ Credentials available")
        print(f"      OAuth tokens: {'Yes' if result['has_oauth_tokens'] else 'No'}")
        print(f"      Service account: {'Yes' if result['has_service_account'] else 'No'}")
        
        return result
    
    def harvest_all_accounts(self) -> List[Dict[str, Any]]:
        """Check all GDrive accounts in vault"""
        print("🔍 GOOGLE DRIVE ACCOUNT CHECKER")
        print("=" * 60)
        
        accounts = self.gdrive_mgr.list_gdrive_accounts()
        print(f"Found {len(accounts)} GDrive accounts in vault\n")
        
        results = []
        for email_address in accounts:
            result = self.check_account_access(email_address)
            results.append(result)
            self.harvest_results.append(result)
        
        return results
    
    def generate_rclone_config(self, output_path: Path) -> None:
        """
        Generate rclone configuration file template
        
        Operator must complete OAuth2 flow manually:
        1. Install rclone: https://rclone.org/install/
        2. Run: rclone config
        3. Choose Google Drive
        4. Follow OAuth2 authentication flow
        5. Config saved to ~/.config/rclone/rclone.conf
        """
        accounts = self.gdrive_mgr.list_gdrive_accounts()
        
        rclone_template = {
            'version': '1.0',
            'note': 'Rclone configuration template for GDrive accounts',
            'instructions': [
                '1. Install rclone: https://rclone.org/install/',
                '2. Run: rclone config',
                '3. Choose "n" for new remote',
                '4. Name it as shown below (e.g., gdrive_account1)',
                '5. Choose "drive" for Google Drive',
                '6. Leave client_id and client_secret blank (uses rclone defaults)',
                '7. Choose "1" for full access',
                '8. Leave root_folder_id blank',
                '9. Leave service_account_file blank',
                '10. Choose "n" for advanced config',
                '11. Choose "y" for auto config (opens browser)',
                '12. Authenticate with Google account',
                '13. Choose "n" for team drive',
                '14. Confirm and repeat for other accounts'
            ],
            'accounts': []
        }
        
        for idx, email in enumerate(accounts, 1):
            rclone_template['accounts'].append({
                'remote_name': f'gdrive_account{idx}',
                'email': email,
                'type': 'drive',
                'scope': 'drive',
                'token_file': f'~/.config/rclone/tokens/{email.replace("@", "_at_")}.token'
            })
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(rclone_template, f, indent=2)
        
        print(f"\n📄 Rclone config template: {output_path}")
    
    def generate_oauth_instructions(self, output_path: Path) -> None:
        """Generate OAuth2 setup instructions"""
        instructions = """
# 🔐 GOOGLE DRIVE OAUTH2 SETUP INSTRUCTIONS

## Method 1: Using rclone (Recommended)

Rclone is the easiest way to access Google Drive from command line.

### Installation:
```bash
# Linux/macOS
curl https://rclone.org/install.sh | sudo bash

# Windows (PowerShell)
# Download from https://rclone.org/downloads/
```

### Configuration:
```bash
# Start interactive configuration
rclone config

# For each Google account:
# 1. Choose "n" for new remote
# 2. Name: gdrive_<email_prefix>  (e.g., gdrive_chanceroofing)
# 3. Storage: 13 (Google Drive)
# 4. Client ID: <leave blank for rclone defaults>
# 5. Client Secret: <leave blank>
# 6. Scope: 1 (Full access)
# 7. Root folder: <leave blank>
# 8. Service account: <leave blank>
# 9. Advanced config: n
# 10. Auto config: y (opens browser)
# 11. Authenticate in browser
# 12. Team drive: n
# 13. Confirm: y
```

### Testing Access:
```bash
# List files
rclone ls gdrive_<name>:

# Get account info
rclone about gdrive_<name>:

# Copy files to local
rclone copy gdrive_<name>:/path/to/folder ./local_folder
```

## Method 2: Using Google Drive API

### Enable API:
1. Go to https://console.cloud.google.com/
2. Create new project: "Citadel GDrive Harvester"
3. Enable Google Drive API
4. Create OAuth 2.0 Client ID (Desktop app)
5. Download credentials.json
6. Place in: data/security/google_drive_credentials.json

### Install Python Client:
```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### Authentication Flow:
```python
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# First time - opens browser for authentication
flow = InstalledAppFlow.from_client_secrets_file(
    'credentials.json', SCOPES)
creds = flow.run_local_server(port=0)

# Save credentials for future use
with open('token.json', 'w') as token:
    token.write(creds.to_json())
```

## Method 3: Using gdown (Public Files Only)

For public Google Drive files:
```bash
pip install gdown

# Download file
gdown <google_drive_file_id>

# Download folder
gdown --folder <google_drive_folder_id>
```

## Recommended Workflow

1. **Use rclone for initial setup** - Easiest OAuth2 flow
2. **Store tokens securely** - Save to Quantum Vault
3. **Use in scripts** - Access Drive programmatically
4. **Schedule harvests** - GitHub Actions with secrets

## Security Notes

- ✅ OAuth2 tokens stored in Quantum Vault
- ✅ Refresh tokens enable long-term access
- ✅ Tokens encrypted with AES-256-GCM
- ⚠️  Never commit tokens to git
- ⚠️  Rotate tokens if compromised

## Next Steps

1. Setup rclone for each account
2. Test access: `rclone ls gdrive_<name>:`
3. Run: `python scripts/harvest_gdrive_data.py`
4. Review: `data/personal_archive/gdrive_harvest_report.json`
"""
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(instructions)
        
        print(f"\n📘 OAuth2 instructions: {output_path}")
    
    def generate_report(self, output_path: Path) -> None:
        """Generate harvest report"""
        report = {
            'harvest_timestamp': datetime.utcnow().isoformat(),
            'total_accounts': len(self.harvest_results),
            'accounts_with_credentials': sum(1 for r in self.harvest_results if r['accessible']),
            'results': self.harvest_results,
            'next_steps': [
                'Configure rclone for each Google account',
                'Complete OAuth2 authentication flow',
                'Test access with: rclone ls gdrive_<name>:',
                'Run GDrive data harvester to map files'
            ]
        }
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 Report saved to: {output_path}")
        print(f"\n✅ Accounts with credentials: {report['accounts_with_credentials']}/{report['total_accounts']}")
        
        print("\n☁️  GOOGLE DRIVE ACCOUNTS:")
        for result in self.harvest_results:
            if result['accessible']:
                print(f"   ✅ {result['email']}")
                print(f"      Status: {result['status']}")


def main():
    """Main execution"""
    # Check for master password
    master_password = os.getenv('MASTER_PASSWORD')
    if not master_password:
        print("❌ MASTER_PASSWORD environment variable not set!")
        return False
    
    # Load vault
    vault_path = Path(__file__).parent.parent / "data" / "security" / "credentials.vault.enc"
    
    if not vault_path.exists():
        print(f"❌ Vault not found: {vault_path}")
        print("   Run: python scripts/initialize_credential_vault.py init")
        return False
    
    try:
        vault = QuantumVault(vault_path, master_key=master_password, use_env_key=False)
        print("✅ Vault loaded")
    except Exception as e:
        print(f"❌ Failed to load vault: {e}")
        return False
    
    # Create harvester
    harvester = GDriveHarvester(vault)
    
    # Check all accounts
    results = harvester.harvest_all_accounts()
    
    # Generate outputs
    output_dir = Path(__file__).parent.parent / "data" / "personal_archive"
    
    # Report
    report_path = output_dir / "gdrive_harvest_report.json"
    harvester.generate_report(report_path)
    
    # Rclone config template
    rclone_path = output_dir / "rclone_config_template.json"
    harvester.generate_rclone_config(rclone_path)
    
    # OAuth instructions
    oauth_path = Path(__file__).parent.parent / "GDRIVE_OAUTH_SETUP.md"
    harvester.generate_oauth_instructions(oauth_path)
    
    print("\n📚 Documentation Generated:")
    print(f"   - OAuth2 Setup Guide: GDRIVE_OAUTH_SETUP.md")
    print(f"   - Rclone Template: {rclone_path}")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
