#!/usr/bin/env python3
"""
🏛️ CITADEL OMNI-PERFECTION: Automation Tool Evaluator
Phase 1.8 - Discover and evaluate automation tools for deployment

Finds available automation tools, CI/CD platforms, and deployment solutions.
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import sys

class AutomationToolEvaluator:
    """Evaluates available automation tools and platforms"""
    
    def __init__(self):
        self.data_dir = Path("/home/runner/work/mapping-and-inventory/mapping-and-inventory/data")
        self.discoveries_dir = self.data_dir / "discoveries"
        self.discoveries_dir.mkdir(parents=True, exist_ok=True)
        
        self.evaluation = {
            "timestamp": datetime.utcnow().isoformat(),
            "cli_tools": [],
            "python_packages": [],
            "github_actions": [],
            "ci_cd_platforms": [],
            "deployment_tools": [],
            "summary": {
                "total_tools": 0,
                "available": 0,
                "recommended": 0
            }
        }
        
        # Tools to check
        self.cli_tools_to_check = [
            {"name": "git", "command": ["git", "--version"], "category": "version_control"},
            {"name": "docker", "command": ["docker", "--version"], "category": "containerization"},
            {"name": "gh", "command": ["gh", "--version"], "category": "github_cli"},
            {"name": "curl", "command": ["curl", "--version"], "category": "http_client"},
            {"name": "wget", "command": ["wget", "--version"], "category": "http_client"},
            {"name": "jq", "command": ["jq", "--version"], "category": "json_processor"},
            {"name": "yq", "command": ["yq", "--version"], "category": "yaml_processor"},
            {"name": "terraform", "command": ["terraform", "--version"], "category": "iac"},
            {"name": "ansible", "command": ["ansible", "--version"], "category": "config_management"},
            {"name": "kubectl", "command": ["kubectl", "version", "--client"], "category": "kubernetes"},
            {"name": "helm", "command": ["helm", "version"], "category": "kubernetes"},
        ]
        
        self.python_packages_to_check = [
            {"name": "pytest", "import_name": "pytest", "category": "testing"},
            {"name": "black", "import_name": "black", "category": "code_quality"},
            {"name": "pylint", "import_name": "pylint", "category": "code_quality"},
            {"name": "flake8", "import_name": "flake8", "category": "code_quality"},
            {"name": "mypy", "import_name": "mypy", "category": "type_checking"},
            {"name": "bandit", "import_name": "bandit", "category": "security"},
            {"name": "safety", "import_name": "safety", "category": "security"},
            {"name": "requests", "import_name": "requests", "category": "http_client"},
            {"name": "click", "import_name": "click", "category": "cli_framework"},
            {"name": "streamlit", "import_name": "streamlit", "category": "web_framework"},
            {"name": "fastapi", "import_name": "fastapi", "category": "web_framework"},
            {"name": "pandas", "import_name": "pandas", "category": "data_processing"},
            {"name": "numpy", "import_name": "numpy", "category": "data_processing"},
        ]
        
        self.ci_cd_platforms = [
            {
                "name": "GitHub Actions",
                "available": True,
                "cost": "Free for public repos",
                "features": ["CI/CD", "Workflows", "Secrets", "Artifacts"],
                "recommendation": "Use as primary CI/CD"
            },
            {
                "name": "GitLab CI",
                "available": False,
                "cost": "Free tier available",
                "features": ["CI/CD", "Auto DevOps", "Container Registry"],
                "recommendation": "Alternative if migrating from GitLab"
            },
            {
                "name": "CircleCI",
                "available": False,
                "cost": "Free tier available",
                "features": ["CI/CD", "Orbs", "Insights"],
                "recommendation": "Good for complex pipelines"
            },
            {
                "name": "Travis CI",
                "available": False,
                "cost": "Free for open source",
                "features": ["CI/CD", "Build matrix"],
                "recommendation": "Legacy option"
            },
        ]
    
    def check_cli_tool(self, tool: Dict) -> Dict:
        """Check if a CLI tool is available"""
        result = {
            "name": tool["name"],
            "category": tool["category"],
            "available": False,
            "version": None,
            "command": " ".join(tool["command"])
        }
        
        try:
            proc = subprocess.run(
                tool["command"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if proc.returncode == 0:
                result["available"] = True
                # Try to extract version from output
                version_line = proc.stdout.split('\n')[0] if proc.stdout else ""
                result["version"] = version_line[:100]  # Truncate long output
        
        except FileNotFoundError:
            result["available"] = False
        except subprocess.TimeoutExpired:
            result["available"] = False
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def check_python_package(self, package: Dict) -> Dict:
        """Check if a Python package is available"""
        result = {
            "name": package["name"],
            "category": package["category"],
            "available": False,
            "version": None
        }
        
        try:
            # Try importing the package
            module = __import__(package["import_name"])
            result["available"] = True
            
            # Try to get version
            if hasattr(module, "__version__"):
                result["version"] = module.__version__
            elif hasattr(module, "VERSION"):
                result["version"] = str(module.VERSION)
        
        except ImportError:
            result["available"] = False
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def evaluate_all_tools(self) -> None:
        """Evaluate all automation tools"""
        print("🏛️ CITADEL AUTOMATION TOOL EVALUATOR")
        print("=" * 60)
        print("🔧 Discovering available automation tools...\n")
        
        # Check CLI tools
        print("📦 Checking CLI tools...")
        for tool in self.cli_tools_to_check:
            result = self.check_cli_tool(tool)
            self.evaluation["cli_tools"].append(result)
            
            if result["available"]:
                print(f"  ✅ {result['name']}: {result['version']}")
                self.evaluation["summary"]["available"] += 1
            else:
                print(f"  ❌ {result['name']}: Not available")
            
            self.evaluation["summary"]["total_tools"] += 1
        
        # Check Python packages
        print("\n🐍 Checking Python packages...")
        for package in self.python_packages_to_check:
            result = self.check_python_package(package)
            self.evaluation["python_packages"].append(result)
            
            if result["available"]:
                print(f"  ✅ {result['name']}: {result.get('version', 'installed')}")
                self.evaluation["summary"]["available"] += 1
            else:
                print(f"  ❌ {result['name']}: Not installed")
            
            self.evaluation["summary"]["total_tools"] += 1
        
        # Add CI/CD platforms info
        print("\n☁️  CI/CD Platforms...")
        for platform in self.ci_cd_platforms:
            self.evaluation["ci_cd_platforms"].append(platform)
            if platform["available"]:
                print(f"  ✅ {platform['name']}: {platform['recommendation']}")
                self.evaluation["summary"]["recommended"] += 1
            else:
                print(f"  📋 {platform['name']}: {platform['cost']}")
        
        # Add deployment tools info
        self._add_deployment_tools()
        
        self._generate_report()
    
    def _add_deployment_tools(self) -> None:
        """Add deployment tool recommendations"""
        deployment_tools = [
            {
                "name": "Vercel",
                "type": "frontend_hosting",
                "cost": "Free tier",
                "features": ["Static sites", "Serverless functions", "Auto deploys"],
                "recommendation": "Best for Next.js/React"
            },
            {
                "name": "Netlify",
                "type": "frontend_hosting",
                "cost": "Free tier",
                "features": ["Static sites", "Forms", "Functions"],
                "recommendation": "Great for JAMstack"
            },
            {
                "name": "Railway",
                "type": "backend_hosting",
                "cost": "Free tier ($5 credit/month)",
                "features": ["Databases", "Docker", "Auto deploy"],
                "recommendation": "Easy full-stack hosting"
            },
            {
                "name": "Render",
                "type": "backend_hosting",
                "cost": "Free tier",
                "features": ["Web services", "Databases", "Cron jobs"],
                "recommendation": "Good Heroku alternative"
            },
            {
                "name": "Fly.io",
                "type": "backend_hosting",
                "cost": "Free tier",
                "features": ["Global deployment", "Auto-scaling", "Postgres"],
                "recommendation": "Low-latency apps"
            },
            {
                "name": "HuggingFace Spaces",
                "type": "ml_hosting",
                "cost": "Free",
                "features": ["Gradio", "Streamlit", "Docker", "GPU"],
                "recommendation": "AI/ML applications"
            },
        ]
        
        self.evaluation["deployment_tools"] = deployment_tools
        self.evaluation["summary"]["recommended"] += len(deployment_tools)
    
    def _generate_report(self) -> None:
        """Generate evaluation report"""
        # Save JSON
        report_file = self.discoveries_dir / "automation_tools.json"
        with open(report_file, 'w') as f:
            json.dump(self.evaluation, f, indent=2)
        
        # Generate markdown
        md_content = f"""# 🔧 AUTOMATION TOOLS EVALUATION

**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}  
**Tools Evaluated:** {self.evaluation['summary']['total_tools']}  
**Available Now:** {self.evaluation['summary']['available']}

---

## 📦 CLI Tools

| Tool | Category | Status | Version |
|------|----------|--------|---------|
"""
        
        for tool in self.evaluation["cli_tools"]:
            status = "✅ Available" if tool["available"] else "❌ Not Found"
            version = tool.get("version", "N/A") if tool["available"] else "-"
            md_content += f"| {tool['name']} | {tool['category']} | {status} | {version} |\n"
        
        md_content += "\n## 🐍 Python Packages\n\n| Package | Category | Status | Version |\n|---------|----------|--------|---------|  \n"
        
        for pkg in self.evaluation["python_packages"]:
            status = "✅ Installed" if pkg["available"] else "❌ Not Installed"
            version = pkg.get("version", "Unknown") if pkg["available"] else "-"
            md_content += f"| {pkg['name']} | {pkg['category']} | {status} | {version} |\n"
        
        md_content += "\n## ☁️  CI/CD Platforms\n\n"
        
        for platform in self.evaluation["ci_cd_platforms"]:
            md_content += f"### {platform['name']}\n\n"
            md_content += f"- **Cost:** {platform['cost']}\n"
            md_content += f"- **Features:** {', '.join(platform['features'])}\n"
            md_content += f"- **Recommendation:** {platform['recommendation']}\n\n"
        
        md_content += "## 🚀 Deployment Tools\n\n"
        
        for tool in self.evaluation["deployment_tools"]:
            md_content += f"### {tool['name']} ({tool['type']})\n\n"
            md_content += f"- **Cost:** {tool['cost']}\n"
            md_content += f"- **Features:** {', '.join(tool['features'])}\n"
            md_content += f"- **Recommendation:** {tool['recommendation']}\n\n"
        
        md_content += """
---

## 📋 Recommendations

### Immediate Use
- **GitHub Actions** - Already available, use for all CI/CD
- **Python ecosystem tools** - Install missing packages as needed
- **HuggingFace Spaces** - Free ML/AI hosting

### Consider Adding
- **Docker** - Containerization for consistent deployments
- **gh CLI** - GitHub operations automation
- **jq/yq** - JSON/YAML processing in scripts

### Future Exploration
- **Terraform/Ansible** - Infrastructure as Code
- **Kubernetes** - Container orchestration at scale
- **Railway/Render** - Backend hosting alternatives

---

**🏛️ Tools Evaluated. Arsenal Cataloged. Automation Ready.**
"""
        
        md_file = self.discoveries_dir / "AUTOMATION_TOOLS_REPORT.md"
        with open(md_file, 'w') as f:
            f.write(md_content)
        
        print(f"\n💾 Reports saved:")
        print(f"   JSON: {report_file}")
        print(f"   Markdown: {md_file}")
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 EVALUATION SUMMARY")
        print("=" * 60)
        print(f"Total Tools Evaluated: {self.evaluation['summary']['total_tools']}")
        print(f"Currently Available: {self.evaluation['summary']['available']}")
        print(f"Recommended Options: {self.evaluation['summary']['recommended']}")

def main():
    """Main execution"""
    evaluator = AutomationToolEvaluator()
    evaluator.evaluate_all_tools()

if __name__ == "__main__":
    main()
