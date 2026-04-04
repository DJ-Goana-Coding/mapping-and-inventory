#!/usr/bin/env python3
"""
📧 EMAIL ACCOUNT HARVESTER
Access email accounts from Quantum Vault and harvest data
"""

import os
import sys
import json
import imaplib
import email
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from security.core.quantum_vault import (
    QuantumVault,
    EmailCredentialManager
)


class EmailHarvester:
    """Harvest emails from multiple accounts"""
    
    def __init__(self, vault: QuantumVault):
        self.vault = vault
        self.email_mgr = EmailCredentialManager(vault)
        self.harvest_results = []
    
    def connect_to_account(self, email_address: str) -> tuple:
        """
        Connect to email account via IMAP
        
        Returns:
            (imap_connection, credential_dict) tuple
        """
        credential = self.email_mgr.get_email_account(email_address)
        
        if not credential:
            raise ValueError(f"Credentials not found for {email_address}")
        
        try:
            # Connect to IMAP server
            imap = imaplib.IMAP4_SSL(
                credential['imap_server'],
                credential['imap_port']
            )
            
            # Login
            imap.login(credential['email'], credential['password'])
            
            return imap, credential
            
        except imaplib.IMAP4.error as e:
            raise ConnectionError(f"IMAP connection failed for {email_address}: {e}")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to {email_address}: {e}")
    
    def harvest_account_info(self, email_address: str) -> Dict[str, Any]:
        """
        Harvest basic information from email account
        
        Returns:
            Dictionary with account information
        """
        print(f"\n📧 Harvesting: {email_address}")
        
        try:
            imap, credential = self.connect_to_account(email_address)
            
            # List mailboxes
            status, mailboxes = imap.list()
            mailbox_list = [box.decode() for box in mailboxes] if status == 'OK' else []
            
            # Select INBOX
            imap.select('INBOX')
            
            # Get email count
            status, messages = imap.search(None, 'ALL')
            email_ids = messages[0].split() if status == 'OK' else []
            total_emails = len(email_ids)
            
            # Get recent emails (last 7 days)
            since_date = (datetime.now() - timedelta(days=7)).strftime("%d-%b-%Y")
            status, recent = imap.search(None, f'SINCE {since_date}')
            recent_ids = recent[0].split() if status == 'OK' else []
            recent_count = len(recent_ids)
            
            # Get unread count
            status, unread = imap.search(None, 'UNSEEN')
            unread_ids = unread[0].split() if status == 'OK' else []
            unread_count = len(unread_ids)
            
            # Close connection
            imap.close()
            imap.logout()
            
            result = {
                'email': email_address,
                'status': 'success',
                'provider': credential['provider'],
                'total_emails': total_emails,
                'recent_emails': recent_count,
                'unread_emails': unread_count,
                'mailboxes': len(mailbox_list),
                'harvested_at': datetime.utcnow().isoformat(),
                'accessible': True
            }
            
            print(f"   ✅ Success - {total_emails} emails, {unread_count} unread")
            
            return result
            
        except ConnectionError as e:
            print(f"   ⚠️  Connection failed: {e}")
            return {
                'email': email_address,
                'status': 'connection_failed',
                'error': str(e),
                'harvested_at': datetime.utcnow().isoformat(),
                'accessible': False
            }
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return {
                'email': email_address,
                'status': 'error',
                'error': str(e),
                'harvested_at': datetime.utcnow().isoformat(),
                'accessible': False
            }
    
    def harvest_all_accounts(self) -> List[Dict[str, Any]]:
        """Harvest information from all email accounts in vault"""
        print("🔍 EMAIL ACCOUNT HARVESTER")
        print("=" * 60)
        
        accounts = self.email_mgr.list_email_accounts()
        print(f"Found {len(accounts)} email accounts in vault\n")
        
        results = []
        for email_address in accounts:
            result = self.harvest_account_info(email_address)
            results.append(result)
            self.harvest_results.append(result)
        
        return results
    
    def generate_report(self, output_path: Path) -> None:
        """Generate harvest report"""
        report = {
            'harvest_timestamp': datetime.utcnow().isoformat(),
            'total_accounts': len(self.harvest_results),
            'accessible_accounts': sum(1 for r in self.harvest_results if r['accessible']),
            'failed_accounts': sum(1 for r in self.harvest_results if not r['accessible']),
            'results': self.harvest_results
        }
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 Report saved to: {output_path}")
        print(f"\n✅ Accessible: {report['accessible_accounts']}/{report['total_accounts']}")
        print(f"❌ Failed: {report['failed_accounts']}/{report['total_accounts']}")
        
        # Print summary of accessible accounts
        print("\n📧 ACCESSIBLE EMAIL ACCOUNTS:")
        for result in self.harvest_results:
            if result['accessible']:
                print(f"   ✅ {result['email']}")
                print(f"      Provider: {result.get('provider', 'unknown')}")
                print(f"      Total Emails: {result.get('total_emails', 0)}")
                print(f"      Unread: {result.get('unread_emails', 0)}")
        
        if report['failed_accounts'] > 0:
            print("\n⚠️  FAILED EMAIL ACCOUNTS:")
            for result in self.harvest_results:
                if not result['accessible']:
                    print(f"   ❌ {result['email']}")
                    print(f"      Error: {result.get('error', 'Unknown error')}")


def main():
    """Main execution"""
    # Check for master password
    master_password = os.getenv('MASTER_PASSWORD')
    if not master_password:
        print("❌ MASTER_PASSWORD environment variable not set!")
        print("   Set it in GitHub Secrets or export it locally")
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
    harvester = EmailHarvester(vault)
    
    # Harvest all accounts
    results = harvester.harvest_all_accounts()
    
    # Generate report
    report_path = Path(__file__).parent.parent / "data" / "personal_archive" / "email_harvest_report.json"
    harvester.generate_report(report_path)
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
