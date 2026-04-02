"""
ARK_CORE // PARTITION_01 // OPPO_NODE.PY
The Librarian's Office - Oppo Node Manager
Main Node Script running on Frequency 7860
"""
import http.server
import socketserver
import json
import os
import sys
import subprocess
from datetime import datetime

PORT = 7860


class OppoNode:
    """Oppo device node manager and orchestrator."""
    
    def __init__(self):
        self.device_id = "OPPO_LIBRARIAN"
        self.frequency = PORT
        self.vault_path = "./Partition_01"
        self.status = "ONLINE"
    
    def sync_from_github(self):
        """Pull latest changes from GitHub repository."""
        print("🔄 Syncing from GitHub Titan...")
        try:
            result = subprocess.run(
                ["git", "pull", "origin", "main"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print("✅ GitHub sync successful")
                return {"status": "success", "output": result.stdout}
            else:
                print(f"⚠️ GitHub sync warning: {result.stderr}")
                return {"status": "warning", "output": result.stderr}
        
        except Exception as e:
            print(f"❌ GitHub sync failed: {e}")
            return {"status": "error", "message": str(e)}
    
    def ingest_intelligence_map(self):
        """Ingest the master intelligence map if it exists."""
        map_path = "./master_intelligence_map.txt"
        
        if os.path.exists(map_path):
            with open(map_path, 'r') as f:
                lines = f.readlines()
            
            file_count = len([l for l in lines if l.strip()])
            print(f"📊 Intelligence map loaded: {file_count} entities")
            
            return {
                "status": "success",
                "entity_count": file_count,
                "path": map_path
            }
        else:
            print("⚠️ Intelligence map not found - run GitHub workflow to generate")
            return {
                "status": "missing",
                "message": "Run TIA_CITADEL_DEEP_SCAN workflow to generate map"
            }
    
    def get_node_status(self):
        """Get current node status."""
        return {
            "device_id": self.device_id,
            "frequency": self.frequency,
            "status": self.status,
            "timestamp": datetime.now().isoformat(),
            "role": "LIBRARIAN",
            "vault_path": self.vault_path,
            "git_status": self._get_git_status()
        }
    
    def _get_git_status(self):
        """Get current Git status."""
        try:
            branch = subprocess.check_output(
                ["git", "branch", "--show-current"],
                text=True
            ).strip()
            
            return {"branch": branch, "available": True}
        except Exception:
            return {"available": False}


class SwarmHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler for Oppo node API."""
    
    node = OppoNode()
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == "/status":
            response = self.node.get_node_status()
        elif self.path == "/sync":
            response = self.node.sync_from_github()
        elif self.path == "/map":
            response = self.node.ingest_intelligence_map()
        else:
            response = {
                "status": "online",
                "role": "OPPO Recon",
                "vote": "HOLDING_FLOOR",
                "device": "LIBRARIAN",
                "frequency": PORT
            }
        
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response, indent=2).encode())
        
        print(f"📡 Handshake Sent: {self.path}")
    
    def log_message(self, format, *args):
        """Override to customize logging."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {format % args}")


def run_server():
    """Start the Oppo node server."""
    print(f"🐝 OPPO Node Initializing...")
    print(f"   Device: OPPO_LIBRARIAN")
    print(f"   Frequency: {PORT}")
    print(f"   Role: Archive & Faceplate Management")
    print("")
    print(f"📡 Available endpoints:")
    print(f"   GET / - Basic handshake")
    print(f"   GET /status - Node status")
    print(f"   GET /sync - Sync from GitHub")
    print(f"   GET /map - Load intelligence map")
    print("")
    
    with socketserver.TCPServer(("0.0.0.0", PORT), SwarmHandler) as httpd:
        print(f"✅ OPPO Node Active. Listening on port {PORT}...")
        print(f"🏰 Press Ctrl+C to stop")
        print("")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 OPPO Node shutting down...")


def main():
    """Main CLI interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="OPPO Librarian Node Manager")
    parser.add_argument("--serve", action="store_true", help="Start HTTP server")
    parser.add_argument("--sync", action="store_true", help="Sync from GitHub")
    parser.add_argument("--status", action="store_true", help="Show node status")
    parser.add_argument("--map", action="store_true", help="Load intelligence map")
    
    args = parser.parse_args()
    
    node = OppoNode()
    
    if args.serve:
        run_server()
    elif args.sync:
        result = node.sync_from_github()
        if result["status"] != "success":
            sys.exit(1)
    elif args.status:
        status = node.get_node_status()
        print(json.dumps(status, indent=2))
    elif args.map:
        result = node.ingest_intelligence_map()
        print(json.dumps(result, indent=2))
    else:
        # Default: run server
        run_server()


if __name__ == "__main__":
    main()
