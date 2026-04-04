#!/usr/bin/env python3
"""
🏛️ CITADEL OMNI-PERFECTION: Automation Integration Engine
Phase 1.9 - Deploy and integrate selected automation tools

Installs, configures, and integrates automation tools from evaluation results.
"""

import os
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

class AutomationIntegrationEngine:
    """Integrates automation tools into the workflow"""
    
    def __init__(self):
        self.repo_root = Path("/home/runner/work/mapping-and-inventory/mapping-and-inventory")
        self.data_dir = self.repo_root / "data"
        self.workflows_dir = self.data_dir / "workflows"
        self.workflows_dir.mkdir(parents=True, exist_ok=True)
        
        self.integration_log = {
            "timestamp": datetime.utcnow().isoformat(),
            "installations": [],
            "configurations": [],
            "integrations": [],
            "summary": {
                "attempted": 0,
                "successful": 0,
                "failed": 0
            }
        }
        
        # Priority tools to install (safe, commonly needed)
        self.priority_tools = [
            {"name": "pytest", "type": "python", "category": "testing"},
            {"name": "pytest-cov", "type": "python", "category": "testing"},
            {"name": "black", "type": "python", "category": "code_quality"},
            {"name": "flake8", "type": "python", "category": "code_quality"},
            {"name": "bandit", "type": "python", "category": "security"},
            {"name": "safety", "type": "python", "category": "security"},
        ]
    
    def install_python_package(self, package_name: str) -> Dict:
        """Install a Python package"""
        result = {
            "package": package_name,
            "type": "python",
            "status": "pending",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            print(f"  📦 Installing {package_name}...")
            
            # Try to install
            proc = subprocess.run(
                [sys.executable, "-m", "pip", "install", package_name, "--quiet"],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if proc.returncode == 0:
                result["status"] = "success"
                result["message"] = f"Successfully installed {package_name}"
                print(f"    ✅ Installed {package_name}")
                self.integration_log["summary"]["successful"] += 1
            else:
                result["status"] = "failed"
                result["error"] = proc.stderr[:200]
                print(f"    ❌ Failed to install {package_name}")
                self.integration_log["summary"]["failed"] += 1
        
        except subprocess.TimeoutExpired:
            result["status"] = "failed"
            result["error"] = "Installation timeout"
            print(f"    ❌ Timeout installing {package_name}")
            self.integration_log["summary"]["failed"] += 1
        
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            print(f"    ❌ Error installing {package_name}: {e}")
            self.integration_log["summary"]["failed"] += 1
        
        return result
    
    def configure_pytest(self) -> Dict:
        """Configure pytest with pytest.ini"""
        config = {
            "tool": "pytest",
            "status": "pending",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        pytest_ini = """[pytest]
# Pytest configuration for Citadel Omni-Perfection
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --cov=scripts
    --cov-report=term-missing
    --cov-report=html
    --cov-report=json

markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
"""
        
        try:
            config_file = self.repo_root / "pytest.ini"
            
            if not config_file.exists():
                config_file.write_text(pytest_ini)
                config["status"] = "success"
                config["file"] = "pytest.ini"
                print("  ✅ Created pytest.ini configuration")
            else:
                config["status"] = "skipped"
                config["message"] = "pytest.ini already exists"
                print("  ⏭️  pytest.ini already exists")
        
        except Exception as e:
            config["status"] = "failed"
            config["error"] = str(e)
            print(f"  ❌ Failed to configure pytest: {e}")
        
        return config
    
    def configure_black(self) -> Dict:
        """Configure Black code formatter"""
        config = {
            "tool": "black",
            "status": "pending",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        black_config = """[tool.black]
line-length = 100
target-version = ['py38', 'py39', 'py310', 'py311']
include = '\\.pyi?$'
exclude = '''
/(
    \\.git
  | \\.venv
  | venv
  | __pycache__
  | \\.pytest_cache
  | node_modules
  | build
  | dist
)/
'''
"""
        
        try:
            pyproject_file = self.repo_root / "pyproject.toml"
            
            if not pyproject_file.exists():
                pyproject_file.write_text(black_config)
                config["status"] = "success"
                config["file"] = "pyproject.toml"
                print("  ✅ Created pyproject.toml with Black config")
            else:
                # Could append to existing file, but skip for safety
                config["status"] = "skipped"
                config["message"] = "pyproject.toml already exists"
                print("  ⏭️  pyproject.toml already exists (not modifying)")
        
        except Exception as e:
            config["status"] = "failed"
            config["error"] = str(e)
            print(f"  ❌ Failed to configure Black: {e}")
        
        return config
    
    def create_test_directory(self) -> Dict:
        """Create tests directory structure"""
        config = {
            "action": "create_test_directory",
            "status": "pending",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            tests_dir = self.repo_root / "tests"
            tests_dir.mkdir(exist_ok=True)
            
            # Create __init__.py
            init_file = tests_dir / "__init__.py"
            if not init_file.exists():
                init_file.write_text('"""Citadel Omni-Perfection Test Suite"""\n')
            
            # Create example test
            example_test = tests_dir / "test_example.py"
            if not example_test.exists():
                example_test.write_text('''"""Example test file for Citadel validation"""

def test_example_pass():
    """Example passing test"""
    assert 1 + 1 == 2

def test_example_calculation():
    """Example calculation test"""
    result = sum([1, 2, 3, 4, 5])
    assert result == 15
''')
            
            config["status"] = "success"
            config["directory"] = "tests/"
            print("  ✅ Created tests/ directory with example tests")
        
        except Exception as e:
            config["status"] = "failed"
            config["error"] = str(e)
            print(f"  ❌ Failed to create test directory: {e}")
        
        return config
    
    def integrate_tools(self) -> None:
        """Integrate all automation tools"""
        print("🏛️ CITADEL AUTOMATION INTEGRATION ENGINE")
        print("=" * 60)
        print("🔧 Installing and configuring automation tools...\n")
        
        # Install priority Python packages
        print("📦 Installing Python packages...")
        for tool in self.priority_tools:
            self.integration_log["summary"]["attempted"] += 1
            result = self.install_python_package(tool["name"])
            self.integration_log["installations"].append(result)
        
        # Configure tools
        print("\n⚙️  Configuring tools...")
        configs = [
            self.configure_pytest(),
            self.configure_black(),
            self.create_test_directory()
        ]
        
        for config in configs:
            self.integration_log["configurations"].append(config)
        
        # Save integration log
        self._save_integration_log()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 INTEGRATION SUMMARY")
        print("=" * 60)
        print(f"Installations Attempted: {self.integration_log['summary']['attempted']}")
        print(f"✅ Successful: {self.integration_log['summary']['successful']}")
        print(f"❌ Failed: {self.integration_log['summary']['failed']}")
    
    def _save_integration_log(self) -> None:
        """Save integration log"""
        log_file = self.workflows_dir / "automation_integration_log.json"
        with open(log_file, 'w') as f:
            json.dump(self.integration_log, f, indent=2)
        
        print(f"\n💾 Integration log saved: {log_file}")

def main():
    """Main execution"""
    engine = AutomationIntegrationEngine()
    engine.integrate_tools()

if __name__ == "__main__":
    main()
