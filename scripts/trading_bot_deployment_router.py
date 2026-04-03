#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
TRADING BOT DEPLOYMENT ROUTER: Ingestion → Garage → Live Trading
═══════════════════════════════════════════════════════════════════════════
Purpose: Route ingested trading bots and strategies to garages for deployment
Authority: Citadel Architect v25.5.OMNI
═══════════════════════════════════════════════════════════════════════════
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Set
import re
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════════
# TRADING BOT CLASSIFICATION PATTERNS
# ═══════════════════════════════════════════════════════════════════════════

TRADING_PATTERNS = {
    "active_bots": {
        "description": "Live trading bots ready for deployment",
        "patterns": [
            r"bot.*\.py$", r"trader.*\.py$", r"live.*trade",
            r"mexc", r"binance", r"coinbase", r"kraken",
            r"vanguard.*trade", r"omega.*trade", r"pioneer.*trade"
        ],
        "keywords": ["bot", "trader", "live", "automated", "trading", "mexc", "exchange"],
        "extensions": [".py", ".js", ".ts"],
        "destination": "Trading_Garage_Alpha"
    },
    "strategies": {
        "description": "Trading strategies and algorithms",
        "patterns": [
            r"strateg", r"algorithm", r"signal", r"indicator",
            r"arbitrage", r"dca", r"grid.*trad", r"scalp",
            r"momentum", r"mean.*reversion"
        ],
        "keywords": ["strategy", "algorithm", "signal", "indicator", "arbitrage", "dca"],
        "extensions": [".py", ".js", ".json", ".yaml", ".md"],
        "destination": "Trading_Garage_Alpha"
    },
    "backtesting": {
        "description": "Backtesting engines and analysis tools",
        "patterns": [
            r"backtest", r"simulation", r"monte.*carlo",
            r"analysis", r"research", r"performance"
        ],
        "keywords": ["backtest", "simulation", "analysis", "performance", "research"],
        "extensions": [".py", ".ipynb", ".js"],
        "destination": "Trading_Garage_Beta"
    },
    "apis": {
        "description": "Exchange APIs and connectors",
        "patterns": [
            r"api", r"connector", r"client", r"sdk",
            r"exchange.*api", r"rest.*api", r"websocket"
        ],
        "keywords": ["api", "connector", "rest", "websocket", "client", "sdk"],
        "extensions": [".py", ".js", ".ts"],
        "destination": "Trading_Garage_Omega"
    },
    "configs": {
        "description": "Trading configuration and credentials",
        "patterns": [
            r"config", r"credential", r"api.*key",
            r"secret", r"\.env", r"setting"
        ],
        "keywords": ["config", "credential", "api_key", "secret", "settings"],
        "extensions": [".json", ".yaml", ".yml", ".env", ".ini"],
        "destination": "Trading_Garage_Alpha/configs"
    },
    "data": {
        "description": "Trading data, ledgers, transactions",
        "patterns": [
            r"ledger", r"transaction", r"trade.*log",
            r"balance", r"portfolio", r"position"
        ],
        "keywords": ["ledger", "transaction", "trade", "balance", "portfolio"],
        "extensions": [".csv", ".json", ".xlsx", ".db", ".sqlite"],
        "destination": "Trading_Garage_Alpha/data"
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# DEPLOYMENT ROUTER
# ═══════════════════════════════════════════════════════════════════════════

class TradingBotDeploymentRouter:
    def __init__(self, ingestion_roots: List[str], garage_root: str = "Trading_Garages"):
        self.ingestion_roots = [Path(root) for root in ingestion_roots]
        self.garage_root = Path(garage_root)
        self.stats = {
            "total_files_scanned": 0,
            "trading_files_found": 0,
            "deployed_to_garage": 0,
            "by_category": {}
        }
        
        # Initialize categories
        for category in TRADING_PATTERNS.keys():
            self.stats["by_category"][category] = 0
        
        # Ensure garage structure exists
        self._ensure_garage_structure()
    
    def _ensure_garage_structure(self):
        """Create garage directory structure if not exists"""
        self.garage_root.mkdir(parents=True, exist_ok=True)
        
        # Create standard garages
        for category_name, category_info in TRADING_PATTERNS.items():
            destination = self.garage_root / category_info["destination"]
            destination.mkdir(parents=True, exist_ok=True)
    
    def classify_trading_file(self, file_path: Path) -> Set[str]:
        """Classify file as trading-related and return matching categories"""
        matches = set()
        file_name = file_path.name.lower()
        file_ext = file_path.suffix.lower()
        
        # Read content sample for text files
        content_sample = ""
        text_extensions = [".py", ".js", ".ts", ".json", ".yaml", ".yml", ".md", ".txt"]
        if file_ext in text_extensions:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content_sample = f.read(2000).lower()
            except Exception:
                pass
        
        # Match against trading patterns
        for category, config in TRADING_PATTERNS.items():
            # Check extension
            if file_ext not in config["extensions"]:
                continue
            
            # Check patterns in filename
            for pattern in config["patterns"]:
                if re.search(pattern, file_name, re.IGNORECASE):
                    matches.add(category)
                    break
            
            # Check keywords in content
            if content_sample and not matches:
                for keyword in config["keywords"]:
                    if keyword in content_sample or keyword in file_name:
                        matches.add(category)
                        break
        
        return matches
    
    def deploy_to_garage(self, file_path: Path, category: str):
        """Deploy file to appropriate garage"""
        self.stats["total_files_scanned"] += 1
        
        destination_base = self.garage_root / TRADING_PATTERNS[category]["destination"]
        destination_base.mkdir(parents=True, exist_ok=True)
        
        # Preserve some directory structure for context
        # Get relative path from ingestion root
        rel_path = None
        for ing_root in self.ingestion_roots:
            try:
                rel_path = file_path.relative_to(ing_root)
                break
            except ValueError:
                continue
        
        if rel_path is None:
            rel_path = file_path.name
        
        # Create destination path
        dest_path = destination_base / rel_path
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy file
        try:
            shutil.copy2(file_path, dest_path)
            self.stats["deployed_to_garage"] += 1
            self.stats["by_category"][category] += 1
            print(f"✅ {category}: {rel_path}")
            return True
        except Exception as e:
            print(f"❌ Error deploying {file_path}: {e}")
            return False
    
    def scan_and_deploy(self):
        """Scan ingestion directories and deploy trading files to garages"""
        print("═══════════════════════════════════════════════════════════════════════════")
        print("🚗 TRADING BOT DEPLOYMENT ROUTER: Ingestion → Garage")
        print("═══════════════════════════════════════════════════════════════════════════")
        print(f"Sources: {[str(r) for r in self.ingestion_roots]}")
        print(f"Target: {self.garage_root}")
        print("")
        
        # Scan all ingestion roots
        for ing_root in self.ingestion_roots:
            if not ing_root.exists():
                print(f"⚠️  Skipping non-existent: {ing_root}")
                continue
            
            print(f"🔍 Scanning: {ing_root}")
            
            # Walk all files
            for file_path in ing_root.rglob("*"):
                if not file_path.is_file():
                    continue
                
                # Classify file
                categories = self.classify_trading_file(file_path)
                
                if categories:
                    self.stats["trading_files_found"] += 1
                    # Deploy to first matching category
                    category = list(categories)[0]
                    self.deploy_to_garage(file_path, category)
        
        # Generate deployment manifest
        self._generate_deployment_manifest()
        
        # Print summary
        print("")
        print("═══════════════════════════════════════════════════════════════════════════")
        print("📊 Deployment Summary")
        print("═══════════════════════════════════════════════════════════════════════════")
        print(f"Files Scanned: {self.stats['total_files_scanned']}")
        print(f"Trading Files Found: {self.stats['trading_files_found']}")
        print(f"Deployed to Garage: {self.stats['deployed_to_garage']}")
        print("")
        print("By Category:")
        for category, count in sorted(self.stats["by_category"].items()):
            dest = TRADING_PATTERNS[category]["destination"]
            print(f"  {category:15} ({dest:30}): {count:6} files")
        print("═══════════════════════════════════════════════════════════════════════════")
    
    def _generate_deployment_manifest(self):
        """Generate deployment manifest"""
        manifest = {
            "version": "1.0.0",
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "deployment_stats": self.stats,
            "categories": {}
        }
        
        for category, config in TRADING_PATTERNS.items():
            manifest["categories"][category] = {
                "description": config["description"],
                "destination": config["destination"],
                "file_count": self.stats["by_category"][category]
            }
        
        manifest_path = self.garage_root / "DEPLOYMENT_MANIFEST.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"✅ Deployment manifest: {manifest_path}")

# ═══════════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    
    # Default ingestion roots
    ingestion_roots = [
        "/data/local_ingestion",
        "/data/total_ingestion",
        "/data/datasets/Node_02"  # Pioneer trading data
    ]
    
    # Override from command line if provided
    if len(sys.argv) > 1:
        ingestion_roots = sys.argv[1:]
    
    # Filter to existing roots
    existing_roots = [r for r in ingestion_roots if Path(r).exists()]
    
    if not existing_roots:
        print("❌ No ingestion directories found!")
        print(f"Searched: {ingestion_roots}")
        print("")
        print("Run vacuum scripts first:")
        print("  ./scripts/local_filesystem_vacuum.sh")
        print("  ./scripts/global_vacuum.sh")
        sys.exit(1)
    
    router = TradingBotDeploymentRouter(existing_roots)
    router.scan_and_deploy()
    
    print("")
    print("🎯 Next Steps:")
    print("  1. Review deployed bots in Trading_Garages/")
    print("  2. Configure API keys in Trading_Garage_Alpha/configs/")
    print("  3. Run garage activation: python scripts/activate_trading_garage.py")
    print("  4. Monitor trading activity via dashboards")
    print("")
    print("🦎 Weld. Pulse. Trade.")
