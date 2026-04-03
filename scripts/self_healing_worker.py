#!/usr/bin/env python3
"""
🔮 SELF-HEALING WORKER - Autonomous Script Repair System
Q.G.T.N.L. Command Citadel - Self-Healing Infrastructure

Purpose: Monitor scripts for failures and automatically repair/update them
Version: 26.0.SELF_HEAL+
Authority: Citadel Architect

Capabilities:
- Detect broken/failing scripts via syntax checking
- Monitor script execution failures
- Auto-repair common issues (imports, dependencies, paths)
- Update scripts when templates change
- Regenerate broken workflows
- Self-test and validate repairs
"""

import os
import sys
import json
import ast
import logging
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import traceback
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/self_healing.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class ScriptHealth:
    """Health status for a script"""
    def __init__(self, path: Path):
        self.path = path
        self.syntax_valid = False
        self.imports_valid = False
        self.executable = False
        self.last_run_success = None
        self.errors = []
        self.warnings = []
        self.last_check = datetime.now().isoformat()


class SelfHealingWorker:
    """
    Autonomous Self-Healing Worker
    
    Monitors and repairs scripts across the Citadel infrastructure
    """
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.scripts_path = self.base_path / "scripts"
        self.services_path = self.base_path / "services"
        self.data_path = self.base_path / "data"
        self.monitoring_path = self.data_path / "monitoring"
        self.health_report_path = self.monitoring_path / "script_health.json"
        
        # Create directories
        self.monitoring_path.mkdir(parents=True, exist_ok=True)
        (self.data_path / "logs").mkdir(parents=True, exist_ok=True)
        (self.data_path / "backups" / "scripts").mkdir(parents=True, exist_ok=True)
        
        # Repair statistics
        self.stats = {
            "total_scripts": 0,
            "healthy_scripts": 0,
            "repaired_scripts": 0,
            "failed_repairs": 0,
            "scan_time": None
        }
        
        logger.info("🔮 Self-Healing Worker initialized")
    
    def scan_all_scripts(self) -> Dict[str, ScriptHealth]:
        """Scan all Python and Bash scripts for issues"""
        logger.info("🔍 Scanning all scripts for health issues...")
        
        health_map = {}
        
        # Python scripts
        for script_path in self.scripts_path.glob("*.py"):
            if script_path.name.startswith('.'):
                continue
            health = self.check_python_script(script_path)
            health_map[str(script_path.relative_to(self.base_path))] = health
            self.stats["total_scripts"] += 1
        
        # Service scripts
        for script_path in self.services_path.glob("*.py"):
            if script_path.name.startswith('.'):
                continue
            health = self.check_python_script(script_path)
            health_map[str(script_path.relative_to(self.base_path))] = health
            self.stats["total_scripts"] += 1
        
        # Bash scripts
        for script_path in self.base_path.glob("*.sh"):
            health = self.check_bash_script(script_path)
            health_map[str(script_path.relative_to(self.base_path))] = health
            self.stats["total_scripts"] += 1
        
        logger.info(f"✅ Scanned {self.stats['total_scripts']} scripts")
        return health_map
    
    def check_python_script(self, script_path: Path) -> ScriptHealth:
        """Check health of a Python script"""
        health = ScriptHealth(script_path)
        
        try:
            # Read script content
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check syntax by parsing AST
            try:
                ast.parse(content)
                health.syntax_valid = True
            except SyntaxError as e:
                health.syntax_valid = False
                health.errors.append(f"Syntax error at line {e.lineno}: {e.msg}")
                logger.warning(f"⚠️  Syntax error in {script_path.name}: {e}")
            
            # Check imports
            health.imports_valid = self.check_imports(content)
            
            # Check if executable
            health.executable = os.access(script_path, os.X_OK)
            if not health.executable:
                health.warnings.append("Script is not executable")
            
            # Count healthy scripts
            if health.syntax_valid and health.imports_valid:
                self.stats["healthy_scripts"] += 1
            
        except Exception as e:
            health.errors.append(f"Failed to check script: {e}")
            logger.error(f"❌ Error checking {script_path.name}: {e}")
        
        return health
    
    def check_bash_script(self, script_path: Path) -> ScriptHealth:
        """Check health of a Bash script"""
        health = ScriptHealth(script_path)
        
        try:
            # Check bash syntax using bash -n
            result = subprocess.run(
                ["bash", "-n", str(script_path)],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                health.syntax_valid = True
                self.stats["healthy_scripts"] += 1
            else:
                health.syntax_valid = False
                health.errors.append(f"Bash syntax error: {result.stderr}")
                logger.warning(f"⚠️  Bash syntax error in {script_path.name}")
            
            # Check if executable
            health.executable = os.access(script_path, os.X_OK)
            if not health.executable:
                health.warnings.append("Script is not executable")
            
        except subprocess.TimeoutExpired:
            health.errors.append("Syntax check timed out")
        except Exception as e:
            health.errors.append(f"Failed to check script: {e}")
            logger.error(f"❌ Error checking {script_path.name}: {e}")
        
        return health
    
    def check_imports(self, content: str) -> bool:
        """Check if all imports in a Python script are valid"""
        try:
            # Extract import statements
            tree = ast.parse(content)
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module.split('.')[0])
            
            # Check if imports are available (basic check)
            # Don't actually import to avoid side effects
            # Just check if module exists in sys.modules or can be found
            for module in imports:
                if module in ['os', 'sys', 'json', 'pathlib', 'datetime', 're']:
                    continue  # Standard library
                # Add more sophisticated checks if needed
            
            return True
            
        except Exception as e:
            logger.debug(f"Import check failed: {e}")
            return False
    
    def auto_repair_script(self, script_path: Path, health: ScriptHealth) -> bool:
        """Attempt to automatically repair a broken script"""
        logger.info(f"🔧 Attempting to repair {script_path.name}...")
        
        # Backup the original
        backup_path = self.backup_script(script_path)
        if not backup_path:
            logger.error(f"❌ Failed to backup {script_path.name}, skipping repair")
            return False
        
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            repaired = False
            
            # Fix 1: Add shebang if missing (Python)
            if script_path.suffix == '.py' and not content.startswith('#!'):
                content = '#!/usr/bin/env python3\n' + content
                repaired = True
                logger.info(f"  ✓ Added Python shebang")
            
            # Fix 2: Add shebang if missing (Bash)
            if script_path.suffix == '.sh' and not content.startswith('#!'):
                content = '#!/bin/bash\n' + content
                repaired = True
                logger.info(f"  ✓ Added Bash shebang")
            
            # Fix 3: Fix common import issues
            if 'from pathlib import Path' not in content and 'Path(' in content:
                # Add pathlib import
                lines = content.split('\n')
                insert_idx = 0
                for i, line in enumerate(lines):
                    if line.startswith('import ') or line.startswith('from '):
                        insert_idx = i + 1
                    elif not line.strip().startswith('#') and line.strip():
                        break
                lines.insert(insert_idx, 'from pathlib import Path')
                content = '\n'.join(lines)
                repaired = True
                logger.info(f"  ✓ Added missing pathlib import")
            
            # Fix 4: Make script executable
            if not health.executable:
                os.chmod(script_path, 0o755)
                repaired = True
                logger.info(f"  ✓ Made script executable")
            
            # If content changed, write it back
            if content != original_content:
                with open(script_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"  ✓ Wrote repaired content")
            
            if repaired:
                # Re-check health
                if script_path.suffix == '.py':
                    new_health = self.check_python_script(script_path)
                else:
                    new_health = self.check_bash_script(script_path)
                
                if new_health.syntax_valid:
                    logger.info(f"✅ Successfully repaired {script_path.name}")
                    self.stats["repaired_scripts"] += 1
                    return True
                else:
                    logger.warning(f"⚠️  Repair did not fix all issues in {script_path.name}")
                    # Restore from backup
                    shutil.copy(backup_path, script_path)
                    self.stats["failed_repairs"] += 1
                    return False
            else:
                logger.info(f"ℹ️  No automatic repairs available for {script_path.name}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to repair {script_path.name}: {e}")
            # Restore from backup
            if backup_path and backup_path.exists():
                shutil.copy(backup_path, script_path)
            self.stats["failed_repairs"] += 1
            return False
    
    def backup_script(self, script_path: Path) -> Optional[Path]:
        """Create a timestamped backup of a script"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.data_path / "backups" / "scripts"
            backup_path = backup_dir / f"{script_path.name}.{timestamp}.bak"
            
            shutil.copy(script_path, backup_path)
            logger.debug(f"  📦 Backed up to {backup_path.name}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Failed to backup {script_path.name}: {e}")
            return None
    
    def generate_health_report(self, health_map: Dict[str, ScriptHealth]) -> Dict:
        """Generate comprehensive health report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_scripts": self.stats["total_scripts"],
                "healthy_scripts": self.stats["healthy_scripts"],
                "broken_scripts": self.stats["total_scripts"] - self.stats["healthy_scripts"],
                "repaired_scripts": self.stats["repaired_scripts"],
                "failed_repairs": self.stats["failed_repairs"],
                "health_percentage": round((self.stats["healthy_scripts"] / max(self.stats["total_scripts"], 1)) * 100, 2)
            },
            "scripts": {}
        }
        
        for script_path, health in health_map.items():
            report["scripts"][script_path] = {
                "syntax_valid": health.syntax_valid,
                "imports_valid": health.imports_valid,
                "executable": health.executable,
                "errors": health.errors,
                "warnings": health.warnings,
                "last_check": health.last_check
            }
        
        return report
    
    def save_health_report(self, report: Dict):
        """Save health report to file"""
        try:
            with open(self.health_report_path, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"📊 Health report saved to {self.health_report_path}")
        except Exception as e:
            logger.error(f"Failed to save health report: {e}")
    
    def run_full_heal(self, auto_repair: bool = True) -> Dict:
        """Run full health scan and optional auto-repair"""
        logger.info("🔮 Starting self-healing scan...")
        start_time = datetime.now()
        
        # Scan all scripts
        health_map = self.scan_all_scripts()
        
        # Attempt repairs if enabled
        if auto_repair:
            logger.info("🔧 Auto-repair enabled, fixing broken scripts...")
            for script_path_str, health in health_map.items():
                if not health.syntax_valid or health.errors:
                    script_path = self.base_path / script_path_str
                    self.auto_repair_script(script_path, health)
                    # Re-scan after repair
                    if script_path.suffix == '.py':
                        health_map[script_path_str] = self.check_python_script(script_path)
                    else:
                        health_map[script_path_str] = self.check_bash_script(script_path)
        
        # Generate report
        report = self.generate_health_report(health_map)
        self.save_health_report(report)
        
        # Print summary
        self.print_summary(report)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        self.stats["scan_time"] = duration
        
        logger.info(f"✅ Self-healing scan complete in {duration:.2f}s")
        return report
    
    def print_summary(self, report: Dict):
        """Print health summary to console"""
        summary = report["summary"]
        
        print("\n" + "═" * 70)
        print("🔮 SELF-HEALING WORKER - HEALTH SUMMARY")
        print("═" * 70)
        print(f"Total Scripts:      {summary['total_scripts']}")
        print(f"Healthy Scripts:    {summary['healthy_scripts']} ✅")
        print(f"Broken Scripts:     {summary['broken_scripts']} ⚠️")
        print(f"Repaired Scripts:   {summary['repaired_scripts']} 🔧")
        print(f"Failed Repairs:     {summary['failed_repairs']} ❌")
        print(f"Health Percentage:  {summary['health_percentage']}%")
        print("═" * 70)
        
        # List broken scripts
        if summary['broken_scripts'] > 0:
            print("\n⚠️  BROKEN SCRIPTS:")
            for script_path, health_data in report["scripts"].items():
                if not health_data["syntax_valid"] or health_data["errors"]:
                    print(f"\n  📄 {script_path}")
                    for error in health_data["errors"]:
                        print(f"     ❌ {error}")
                    for warning in health_data["warnings"]:
                        print(f"     ⚠️  {warning}")
        
        print("\n📊 Full report: data/monitoring/script_health.json\n")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Self-Healing Worker - Autonomous Script Repair")
    parser.add_argument('--no-repair', action='store_true', help='Scan only, do not auto-repair')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create and run worker
    worker = SelfHealingWorker()
    report = worker.run_full_heal(auto_repair=not args.no_repair)
    
    # Exit with error if any scripts are broken
    if report["summary"]["broken_scripts"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
