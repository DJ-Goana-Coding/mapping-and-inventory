#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
CREDENTIAL MANAGER - Secure Trading Credentials
═══════════════════════════════════════════════════════════════════════════
Purpose: Securely manage and validate trading API credentials
Authority: Citadel Architect v25.0.OMNI+
═══════════════════════════════════════════════════════════════════════════

Features:
- Environment variable loading
- Credential validation
- API connectivity testing
- Secret rotation tracking
- Audit logging
"""

import os
import json
import hashlib
import hmac
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple
import urllib.request
import urllib.error


class CredentialManager:
    """
    Manages trading API credentials securely.
    
    Credentials are NEVER stored in code or files.
    All credentials must be in environment variables or GitHub Secrets.
    """
    
    def __init__(self):
        """Initialize credential manager"""
        self.data_dir = Path("data/trading_safety")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.audit_log = self.data_dir / "credential_audit.json"
        self.validation_cache = self.data_dir / "credential_validation.json"
        
        self.credentials = {}
        self.validation_results = {}
    
    def load_mexc_credentials(self) -> Tuple[bool, str]:
        """
        Load MEXC API credentials from environment.
        
        Returns:
            (success: bool, message: str)
        """
        api_key = os.getenv("MEXC_API_KEY")
        api_secret = os.getenv("MEXC_API_SECRET")
        
        if not api_key:
            return False, "MEXC_API_KEY not found in environment"
        
        if not api_secret:
            return False, "MEXC_API_SECRET not found in environment"
        
        # Store credentials (in memory only)
        self.credentials["mexc"] = {
            "api_key": api_key,
            "api_secret": api_secret,
            "exchange": "MEXC",
            "loaded_at": datetime.utcnow().isoformat() + "Z"
        }
        
        self._log_audit("MEXC_CREDENTIALS_LOADED", {
            "api_key_hash": hashlib.sha256(api_key.encode()).hexdigest()[:16],
            "success": True
        })
        
        return True, "MEXC credentials loaded successfully"
    
    def load_wallet_credentials(self) -> Tuple[bool, str]:
        """
        Load Web3 wallet credentials from environment.
        
        Returns:
            (success: bool, message: str)
        """
        wallet_address = os.getenv("TRADING_WALLET_ADDRESS")
        private_key = os.getenv("TRADING_WALLET_PRIVATE_KEY")
        
        if not wallet_address and not private_key:
            # Wallet credentials are optional
            return True, "Wallet credentials not configured (optional)"
        
        if wallet_address and not private_key:
            return False, "Wallet address found but private key missing"
        
        self.credentials["wallet"] = {
            "address": wallet_address,
            "private_key": private_key,
            "loaded_at": datetime.utcnow().isoformat() + "Z"
        }
        
        self._log_audit("WALLET_CREDENTIALS_LOADED", {
            "address": wallet_address,
            "success": True
        })
        
        return True, "Wallet credentials loaded successfully"
    
    def validate_mexc_credentials(self) -> Tuple[bool, str]:
        """
        Validate MEXC credentials by testing API connectivity.
        Makes a safe read-only API call to verify credentials work.
        
        Returns:
            (valid: bool, message: str)
        """
        if "mexc" not in self.credentials:
            return False, "MEXC credentials not loaded"
        
        creds = self.credentials["mexc"]
        api_key = creds["api_key"]
        api_secret = creds["api_secret"]
        
        try:
            # Test with account endpoint (read-only)
            timestamp = str(int(time.time() * 1000))
            query_string = f"timestamp={timestamp}"
            
            # Create signature
            signature = hmac.new(
                api_secret.encode('utf-8'),
                query_string.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            url = f"https://api.mexc.com/api/v3/account?{query_string}&signature={signature}"
            
            req = urllib.request.Request(url)
            req.add_header("X-MEXC-APIKEY", api_key)
            req.add_header("Content-Type", "application/json")
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                
                # Check if we got valid account data
                if "balances" in data:
                    self.validation_results["mexc"] = {
                        "valid": True,
                        "validated_at": datetime.utcnow().isoformat() + "Z",
                        "account_exists": True
                    }
                    
                    self._log_audit("MEXC_VALIDATION_SUCCESS", {
                        "timestamp": timestamp,
                        "has_balances": True
                    })
                    
                    return True, "MEXC credentials validated successfully"
                else:
                    return False, "Unexpected API response format"
        
        except urllib.error.HTTPError as e:
            error_msg = f"HTTP {e.code}: {e.reason}"
            
            if e.code == 401:
                error_msg = "Invalid API key or signature"
            elif e.code == 403:
                error_msg = "API key lacks required permissions"
            
            self._log_audit("MEXC_VALIDATION_FAILED", {
                "error": error_msg,
                "http_code": e.code
            })
            
            return False, error_msg
        
        except Exception as e:
            error_msg = f"Validation error: {str(e)}"
            self._log_audit("MEXC_VALIDATION_ERROR", {"error": error_msg})
            return False, error_msg
    
    def get_mexc_balance(self) -> Tuple[bool, Dict]:
        """
        Get MEXC account balance (safe read-only operation).
        
        Returns:
            (success: bool, balance_data: dict)
        """
        if "mexc" not in self.credentials:
            return False, {"error": "MEXC credentials not loaded"}
        
        if "mexc" not in self.validation_results or not self.validation_results["mexc"]["valid"]:
            return False, {"error": "MEXC credentials not validated"}
        
        creds = self.credentials["mexc"]
        api_key = creds["api_key"]
        api_secret = creds["api_secret"]
        
        try:
            timestamp = str(int(time.time() * 1000))
            query_string = f"timestamp={timestamp}"
            
            signature = hmac.new(
                api_secret.encode('utf-8'),
                query_string.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            url = f"https://api.mexc.com/api/v3/account?{query_string}&signature={signature}"
            
            req = urllib.request.Request(url)
            req.add_header("X-MEXC-APIKEY", api_key)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                
                # Extract USDT balance
                usdt_balance = 0.0
                total_value = 0.0
                
                for balance in data.get("balances", []):
                    free = float(balance.get("free", 0))
                    locked = float(balance.get("locked", 0))
                    total = free + locked
                    
                    if balance["asset"] == "USDT":
                        usdt_balance = total
                    
                    # Simplified - in production would convert to USDT
                    if total > 0:
                        total_value += total
                
                return True, {
                    "usdt_balance": usdt_balance,
                    "total_assets": len([b for b in data.get("balances", []) if float(b.get("free", 0)) + float(b.get("locked", 0)) > 0]),
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
        
        except Exception as e:
            return False, {"error": str(e)}
    
    def _log_audit(self, event_type: str, details: Dict):
        """Log credential audit event"""
        event = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": event_type,
            "details": details
        }
        
        logs = []
        if self.audit_log.exists():
            with open(self.audit_log, 'r') as f:
                logs = json.load(f)
        
        logs.append(event)
        logs = logs[-500:]  # Keep last 500 events
        
        with open(self.audit_log, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def get_credential_status(self) -> Dict:
        """Get status of all credentials"""
        status = {
            "mexc": {
                "loaded": "mexc" in self.credentials,
                "validated": "mexc" in self.validation_results and self.validation_results["mexc"]["valid"],
                "last_validated": self.validation_results.get("mexc", {}).get("validated_at")
            },
            "wallet": {
                "loaded": "wallet" in self.credentials,
                "validated": False  # Web3 validation would require RPC call
            }
        }
        
        return status


if __name__ == "__main__":
    # Test credential manager
    print("🔐 Credential Manager Test\n")
    
    manager = CredentialManager()
    
    # Load MEXC credentials
    success, msg = manager.load_mexc_credentials()
    print(f"MEXC Load: {'✅' if success else '❌'} {msg}")
    
    # Validate MEXC credentials (if loaded)
    if success:
        valid, msg = manager.validate_mexc_credentials()
        print(f"MEXC Validate: {'✅' if valid else '❌'} {msg}")
        
        # Get balance (if validated)
        if valid:
            success, balance = manager.get_mexc_balance()
            if success:
                print(f"MEXC Balance: ${balance.get('usdt_balance', 0):.2f} USDT")
    
    # Load wallet credentials
    success, msg = manager.load_wallet_credentials()
    print(f"Wallet Load: {'✅' if success else '⚠️ '} {msg}")
    
    # Show status
    print("\n📊 Credential Status:")
    status = manager.get_credential_status()
    print(json.dumps(status, indent=2))
