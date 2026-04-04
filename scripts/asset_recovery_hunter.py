#!/usr/bin/env python3
"""
🏛️ CITADEL OMNI-PERFECTION: Asset Recovery Hunter
Phase 1.6 - Discover lost crypto wallets, forgotten assets, and recovery opportunities

Scans for wallet files, seed phrases, transaction histories, and recovery leads.
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set
import hashlib

class AssetRecoveryHunter:
    """Hunts for lost crypto assets and recovery opportunities"""
    
    def __init__(self):
        self.repo_root = Path("/home/runner/work/mapping-and-inventory/mapping-and-inventory")
        self.data_dir = self.repo_root / "data"
        self.discoveries_dir = self.data_dir / "discoveries"
        self.discoveries_dir.mkdir(parents=True, exist_ok=True)
        
        self.recovery_leads = {
            "timestamp": datetime.utcnow().isoformat(),
            "wallet_files": [],
            "address_mentions": [],
            "transaction_records": [],
            "exchange_references": [],
            "seed_phrase_indicators": [],
            "summary": {
                "total_leads": 0,
                "wallet_files_found": 0,
                "addresses_found": 0,
                "high_priority": 0,
                "medium_priority": 0,
                "low_priority": 0
            }
        }
        
        # Patterns for crypto addresses
        self.address_patterns = {
            "bitcoin": re.compile(r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b'),
            "ethereum": re.compile(r'\b0x[a-fA-F0-9]{40}\b'),
            "litecoin": re.compile(r'\b[LM3][a-km-zA-HJ-NP-Z1-9]{26,33}\b'),
            "dogecoin": re.compile(r'\bD{1}[5-9A-HJ-NP-U]{1}[1-9A-HJ-NP-Za-km-z]{32}\b'),
            "ripple": re.compile(r'\br[a-zA-Z0-9]{24,34}\b'),
            "cardano": re.compile(r'\baddr1[a-z0-9]{58}\b'),
        }
        
        # Wallet file extensions and names
        self.wallet_file_patterns = [
            "wallet.dat",
            "*.wallet",
            "keystore",
            "*.key",
            "*.keystore",
            "mnemonic.txt",
            "seed.txt",
            "recovery.txt"
        ]
        
        # Exchange keywords
        self.exchange_keywords = [
            "binance", "coinbase", "kraken", "bitfinex", "gemini",
            "kucoin", "okex", "huobi", "bittrex", "poloniex",
            "mexc", "bybit", "ftx", "crypto.com"
        ]
    
    def scan_for_wallet_files(self) -> List[Dict]:
        """Scan for potential wallet files"""
        print("🔍 Scanning for wallet files...")
        leads = []
        
        # Search for wallet-related files
        for root, dirs, files in os.walk(self.repo_root):
            # Skip certain directories
            if any(skip in root for skip in ['.git', 'node_modules', '__pycache__', '.pytest_cache']):
                continue
            
            for file in files:
                filepath = Path(root) / file
                
                # Check if filename matches wallet patterns
                for pattern in self.wallet_file_patterns:
                    if file.lower() == pattern.lower() or (
                        '*' in pattern and file.lower().endswith(pattern.replace('*', ''))
                    ):
                        lead = {
                            "type": "wallet_file",
                            "file": str(filepath.relative_to(self.repo_root)),
                            "filename": file,
                            "size_bytes": filepath.stat().st_size if filepath.exists() else 0,
                            "priority": "high" if filepath.stat().st_size > 0 else "low",
                            "detected_at": datetime.utcnow().isoformat(),
                            "notes": "Potential wallet file - investigate carefully"
                        }
                        leads.append(lead)
                        self.recovery_leads["wallet_files"].append(lead)
                        self.recovery_leads["summary"]["wallet_files_found"] += 1
                        print(f"  📁 Found: {file} ({lead['size_bytes']} bytes)")
        
        return leads
    
    def scan_for_addresses(self) -> List[Dict]:
        """Scan files for cryptocurrency addresses"""
        print("\n🔍 Scanning for crypto addresses...")
        leads = []
        addresses_found = set()
        
        # Scan text files
        text_extensions = {'.txt', '.md', '.json', '.log', '.csv', '.py', '.js', '.ts'}
        
        for root, dirs, files in os.walk(self.repo_root):
            if any(skip in root for skip in ['.git', 'node_modules', '__pycache__']):
                continue
            
            for file in files:
                filepath = Path(root) / file
                
                if filepath.suffix.lower() not in text_extensions:
                    continue
                
                # Don't scan large files
                if filepath.stat().st_size > 1024 * 1024:  # Skip files > 1MB
                    continue
                
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Search for each crypto address pattern
                    for crypto_type, pattern in self.address_patterns.items():
                        matches = pattern.findall(content)
                        
                        for match in matches:
                            # Skip if already found or looks like example/placeholder
                            if match in addresses_found:
                                continue
                            
                            if any(placeholder in match.lower() for placeholder in 
                                   ['example', 'xxx', '000', '111', 'test', 'sample']):
                                continue
                            
                            addresses_found.add(match)
                            
                            lead = {
                                "type": "crypto_address",
                                "cryptocurrency": crypto_type,
                                "address": match,
                                "file": str(filepath.relative_to(self.repo_root)),
                                "priority": "medium",
                                "detected_at": datetime.utcnow().isoformat(),
                                "notes": f"{crypto_type.title()} address found in {filepath.name}"
                            }
                            leads.append(lead)
                            self.recovery_leads["address_mentions"].append(lead)
                            self.recovery_leads["summary"]["addresses_found"] += 1
                            
                            if len(leads) <= 5:  # Print first 5
                                print(f"  💰 Found {crypto_type}: {match[:20]}... in {filepath.name}")
                
                except Exception as e:
                    pass  # Skip files that can't be read
        
        if len(leads) > 5:
            print(f"  ... and {len(leads) - 5} more addresses")
        
        return leads
    
    def scan_for_transaction_records(self) -> List[Dict]:
        """Scan for transaction histories and trade records"""
        print("\n🔍 Scanning for transaction records...")
        leads = []
        
        # Look for CSV, JSON files that might contain transaction data
        for root, dirs, files in os.walk(self.repo_root):
            if any(skip in root for skip in ['.git', 'node_modules']):
                continue
            
            for file in files:
                if not (file.endswith('.csv') or file.endswith('.json')):
                    continue
                
                filepath = Path(root) / file
                
                # Check if filename suggests trading/transaction data
                if any(keyword in file.lower() for keyword in 
                       ['transaction', 'trade', 'order', 'balance', 'withdraw', 'deposit', 'history']):
                    
                    lead = {
                        "type": "transaction_record",
                        "file": str(filepath.relative_to(self.repo_root)),
                        "size_kb": round(filepath.stat().st_size / 1024, 2),
                        "priority": "high" if filepath.stat().st_size > 0 else "low",
                        "detected_at": datetime.utcnow().isoformat(),
                        "notes": "Potential transaction history - may contain trade data"
                    }
                    leads.append(lead)
                    self.recovery_leads["transaction_records"].append(lead)
                    print(f"  📊 Found: {file} ({lead['size_kb']} KB)")
        
        return leads
    
    def scan_for_exchange_references(self) -> List[Dict]:
        """Scan for exchange API keys and account references"""
        print("\n🔍 Scanning for exchange references...")
        leads = []
        
        # Scan configuration and credential files
        config_extensions = {'.env', '.ini', '.cfg', '.conf', '.json', '.yaml', '.yml', '.txt'}
        
        for root, dirs, files in os.walk(self.repo_root):
            if any(skip in root for skip in ['.git', 'node_modules']):
                continue
            
            for file in files:
                filepath = Path(root) / file
                
                if filepath.suffix.lower() not in config_extensions:
                    continue
                
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().lower()
                    
                    # Check for exchange references
                    for exchange in self.exchange_keywords:
                        if exchange in content:
                            # Check for API key patterns
                            has_api_key = any(keyword in content for keyword in 
                                            ['api_key', 'api-key', 'apikey', 'access_key', 'secret'])
                            
                            lead = {
                                "type": "exchange_reference",
                                "exchange": exchange,
                                "file": str(filepath.relative_to(self.repo_root)),
                                "has_api_key_mention": has_api_key,
                                "priority": "high" if has_api_key else "low",
                                "detected_at": datetime.utcnow().isoformat(),
                                "notes": f"Reference to {exchange} exchange found"
                            }
                            leads.append(lead)
                            self.recovery_leads["exchange_references"].append(lead)
                            
                            if has_api_key:
                                print(f"  🔑 Found {exchange} with API key mention in {filepath.name}")
                            
                            break  # Only report each exchange once per file
                
                except Exception as e:
                    pass
        
        return leads
    
    def generate_recovery_report(self) -> None:
        """Generate comprehensive recovery report"""
        # Update summary
        all_leads = (
            len(self.recovery_leads["wallet_files"]) +
            len(self.recovery_leads["address_mentions"]) +
            len(self.recovery_leads["transaction_records"]) +
            len(self.recovery_leads["exchange_references"])
        )
        self.recovery_leads["summary"]["total_leads"] = all_leads
        
        # Count priorities
        for category in ["wallet_files", "address_mentions", "transaction_records", "exchange_references"]:
            for lead in self.recovery_leads[category]:
                priority = lead.get("priority", "low")
                if priority == "high":
                    self.recovery_leads["summary"]["high_priority"] += 1
                elif priority == "medium":
                    self.recovery_leads["summary"]["medium_priority"] += 1
                else:
                    self.recovery_leads["summary"]["low_priority"] += 1
        
        # Save JSON report
        report_file = self.discoveries_dir / "asset_recovery_leads.json"
        with open(report_file, 'w') as f:
            json.dump(self.recovery_leads, f, indent=2)
        
        # Generate markdown report
        md_content = f"""# 💰 ASSET RECOVERY REPORT

**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}  
**Total Leads:** {all_leads}

## 🎯 Summary

- **Wallet Files:** {len(self.recovery_leads['wallet_files'])}
- **Crypto Addresses:** {len(self.recovery_leads['address_mentions'])}
- **Transaction Records:** {len(self.recovery_leads['transaction_records'])}
- **Exchange References:** {len(self.recovery_leads['exchange_references'])}

### Priority Breakdown
- 🔴 **High Priority:** {self.recovery_leads['summary']['high_priority']}
- 🟡 **Medium Priority:** {self.recovery_leads['summary']['medium_priority']}
- 🟢 **Low Priority:** {self.recovery_leads['summary']['low_priority']}

---

## 📁 Wallet Files

"""
        if self.recovery_leads["wallet_files"]:
            for wallet in self.recovery_leads["wallet_files"]:
                md_content += f"- **{wallet['filename']}** ({wallet['size_bytes']} bytes) - `{wallet['file']}`\n"
        else:
            md_content += "*No wallet files detected*\n"
        
        md_content += "\n## 💎 Crypto Addresses\n\n"
        
        # Group addresses by cryptocurrency
        address_by_crypto = {}
        for addr in self.recovery_leads["address_mentions"]:
            crypto = addr["cryptocurrency"]
            if crypto not in address_by_crypto:
                address_by_crypto[crypto] = []
            address_by_crypto[crypto].append(addr)
        
        for crypto, addresses in sorted(address_by_crypto.items()):
            md_content += f"### {crypto.title()} ({len(addresses)})\n\n"
            for addr in addresses[:5]:  # Show first 5
                md_content += f"- `{addr['address']}` - Found in `{addr['file']}`\n"
            if len(addresses) > 5:
                md_content += f"\n*...and {len(addresses) - 5} more*\n"
            md_content += "\n"
        
        md_content += """
---

## ⚠️ Important Notes

1. **Security**: Do NOT commit actual wallet files or private keys to repositories
2. **Verification**: Verify all addresses before assuming they contain funds
3. **Privacy**: Some addresses may be examples or test addresses
4. **Action Items**: 
   - Check wallet files for actual balances
   - Verify addresses on blockchain explorers
   - Review transaction records for unclaimed assets
   - Secure any actual wallet files immediately

---

**🏛️ Asset Recovery Protocol Active. Scan Complete.**
"""
        
        md_file = self.discoveries_dir / "ASSET_RECOVERY_REPORT.md"
        with open(md_file, 'w') as f:
            f.write(md_content)
        
        print(f"\n💾 Reports saved:")
        print(f"   JSON: {report_file}")
        print(f"   Markdown: {md_file}")
    
    def run_full_scan(self) -> None:
        """Run complete asset recovery scan"""
        print("🏛️ CITADEL ASSET RECOVERY HUNTER")
        print("=" * 60)
        print("💰 Scanning for lost crypto assets and recovery opportunities...\n")
        
        self.scan_for_wallet_files()
        self.scan_for_addresses()
        self.scan_for_transaction_records()
        self.scan_for_exchange_references()
        
        self.generate_recovery_report()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 RECOVERY SCAN SUMMARY")
        print("=" * 60)
        print(f"Total Leads: {self.recovery_leads['summary']['total_leads']}")
        print(f"Wallet Files: {self.recovery_leads['summary']['wallet_files_found']}")
        print(f"Addresses: {self.recovery_leads['summary']['addresses_found']}")
        print(f"\nPriority:")
        print(f"  🔴 High: {self.recovery_leads['summary']['high_priority']}")
        print(f"  🟡 Medium: {self.recovery_leads['summary']['medium_priority']}")
        print(f"  🟢 Low: {self.recovery_leads['summary']['low_priority']}")

def main():
    """Main execution"""
    hunter = AssetRecoveryHunter()
    hunter.run_full_scan()

if __name__ == "__main__":
    main()
