"""
Pioneer Bridge Protocol - T.I.A. Grand Handshake
Establishes live telemetry sync between mapping-and-inventory (Brain) and pioneer-trader (Muscle)
"""

import os
import requests
from datetime import datetime
import json
import time


class PioneerBridge:
    """Bridge protocol for communicating with Pioneer Trader system"""
    
    def __init__(self):
        self.pioneer_url = os.getenv("PIONEER_TRADER_URL")
        self.auth_token = os.getenv("PIONEER_AUTH_TOKEN")
        self.cache = {}
        self.last_sync = None
        self.shadow_archive_path = os.getenv("SHADOW_ARCHIVE_PATH", "/app/shadow_archive")
    
    def fetch_pioneer_status(self):
        """
        Fetches live telemetry from Pioneer Trader's /telemetry endpoint.
        
        Returns:
            dict: {
                "success": bool,
                "data": {
                    "wallet": str,
                    "equity": str,
                    "slots": dict,
                    "status": str
                },
                "timestamp": str,
                "error": str (if failed)
            }
        """
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        # Check environment variables
        if not self.pioneer_url:
            print("⚠️ [T.I.A.] PIONEER_TRADER_URL not configured")
            return {
                "success": False,
                "error": "PIONEER_TRADER_URL environment variable not set",
                "timestamp": timestamp
            }
        
        if not self.auth_token:
            print("⚠️ [T.I.A.] PIONEER_AUTH_TOKEN not configured")
            return {
                "success": False,
                "error": "PIONEER_AUTH_TOKEN environment variable not set",
                "timestamp": timestamp
            }
        
        # Construct telemetry URL
        telemetry_url = f"{self.pioneer_url.rstrip('/')}/telemetry"
        
        # Retry logic with exponential backoff
        max_retries = 3
        base_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                print(f"🌉 [T.I.A.] Handshake attempt {attempt + 1}/{max_retries}...")
                
                # Make authenticated GET request
                headers = {
                    "Authorization": f"Bearer {self.auth_token}",
                    "Content-Type": "application/json"
                }
                
                response = requests.get(
                    telemetry_url,
                    headers=headers,
                    timeout=10
                )
                
                # Check response status
                if response.status_code == 200:
                    data = response.json()
                    
                    # Update cache with successful response
                    result = {
                        "success": True,
                        "data": data,
                        "timestamp": timestamp
                    }
                    self.cache = result
                    self.last_sync = timestamp
                    
                    print(f"✅ [T.I.A.] Handshake successful - {data.get('status', 'UNKNOWN')}")
                    return result
                
                elif response.status_code == 401:
                    print(f"🔒 [T.I.A.] Authentication failed - Invalid token")
                    return {
                        "success": False,
                        "error": "Authentication failed: Invalid PIONEER_AUTH_TOKEN",
                        "timestamp": timestamp
                    }
                
                else:
                    print(f"⚠️ [T.I.A.] Unexpected status code: {response.status_code}")
                    
                    # If not last attempt, retry with backoff
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        print(f"   Retrying in {delay} seconds...")
                        time.sleep(delay)
                        continue
                    
                    return {
                        "success": False,
                        "error": f"HTTP {response.status_code}: {response.text}",
                        "timestamp": timestamp
                    }
            
            except requests.exceptions.Timeout:
                print(f"⏱️ [T.I.A.] Request timeout on attempt {attempt + 1}")
                
                # If not last attempt, retry with backoff
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    print(f"   Retrying in {delay} seconds...")
                    time.sleep(delay)
                    continue
                
                # On final timeout, use cached data if available
                if self.cache.get("success"):
                    print(f"📦 [T.I.A.] Using cached data from {self.cache.get('timestamp')}")
                    return self.cache
                
                return {
                    "success": False,
                    "error": "Connection timeout - Pioneer Trader unreachable",
                    "timestamp": timestamp
                }
            
            except requests.exceptions.ConnectionError as e:
                print(f"🔌 [T.I.A.] Connection error on attempt {attempt + 1}: {str(e)}")
                
                # If not last attempt, retry with backoff
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    print(f"   Retrying in {delay} seconds...")
                    time.sleep(delay)
                    continue
                
                # On final failure, use cached data if available
                if self.cache.get("success"):
                    print(f"📦 [T.I.A.] Using cached data from {self.cache.get('timestamp')}")
                    return self.cache
                
                return {
                    "success": False,
                    "error": f"Connection error: {str(e)}",
                    "timestamp": timestamp
                }
            
            except Exception as e:
                print(f"❌ [T.I.A.] Unexpected error on attempt {attempt + 1}: {str(e)}")
                
                # If not last attempt, retry
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    print(f"   Retrying in {delay} seconds...")
                    time.sleep(delay)
                    continue
                
                return {
                    "success": False,
                    "error": f"Unexpected error: {str(e)}",
                    "timestamp": timestamp
                }
        
        # Should not reach here, but return failure if we do
        return {
            "success": False,
            "error": "Max retries exceeded",
            "timestamp": timestamp
        }
    
    def sync_to_shadow_archive(self, data):
        """
        Backs up telemetry data to shadow archive for persistence.
        
        Args:
            data: Telemetry data from Pioneer Trader
        """
        try:
            # Create shadow archive directory if it doesn't exist
            os.makedirs(self.shadow_archive_path, exist_ok=True)
            
            # Prepare data with sync metadata
            archive_data = {
                "telemetry": data,
                "sync_metadata": {
                    "archived_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "source": "PioneerBridge",
                    "version": "1.0.0"
                }
            }
            
            # Implement atomic write (tmp file + rename)
            final_path = os.path.join(self.shadow_archive_path, "pioneer_status.json")
            tmp_path = os.path.join(self.shadow_archive_path, "pioneer_status.json.tmp")
            
            # Write to temporary file
            print(f"💾 [T.I.A.] Writing to shadow archive: {final_path}")
            with open(tmp_path, "w") as f:
                json.dump(archive_data, f, indent=2)
            
            # Atomic rename
            os.replace(tmp_path, final_path)
            
            print(f"✅ [T.I.A.] Shadow archive updated successfully")
            
        except Exception as e:
            print(f"❌ [T.I.A.] Shadow archive write failed: {str(e)}")
            # Don't crash - logging the error is sufficient
