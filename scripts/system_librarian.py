#!/usr/bin/env python3
"""
📚 SYSTEM LIBRARIAN
Comprehensive system profiling, indexing, and upgrade recommendations

Catalogs:
- Hardware specifications (CPU, RAM, GPU, disk)
- Software capabilities (languages, frameworks, tools)
- Resources available (free disk, memory, performance)
- Utilization potential (what can run on this system)
- Upgrade recommendations (what to improve)

Usage:
    python scripts/system_librarian.py
    python scripts/system_librarian.py --output system_profile.json
"""

import os
import sys
import json
import platform
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import argparse


class SystemLibrarian:
    """System profiler and upgrade advisor"""
    
    def __init__(self):
        self.repo_root = Path(__file__).parent.parent
        self.output_dir = self.repo_root / "data" / "laptop_inventory"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.profile = {
            "scan_timestamp": datetime.utcnow().isoformat() + "Z",
            "hostname": platform.node(),
            "os": {},
            "hardware": {},
            "software": {},
            "capabilities": {},
            "resources": {},
            "recommendations": {}
        }
    
    def get_os_info(self):
        """Catalog operating system information"""
        print("\n🖥️  Cataloging Operating System...")
        
        self.profile["os"] = {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "architecture": platform.architecture()[0]
        }
        
        # Additional OS-specific info
        if platform.system() == "Windows":
            try:
                result = subprocess.run(['systeminfo'], capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    # Parse Windows version
                    for line in result.stdout.split('\n'):
                        if 'OS Name' in line:
                            self.profile["os"]["full_name"] = line.split(':', 1)[1].strip()
                        elif 'OS Version' in line:
                            self.profile["os"]["build"] = line.split(':', 1)[1].strip()
            except:
                pass
        
        elif platform.system() in ["Linux", "Darwin"]:
            try:
                result = subprocess.run(['uname', '-a'], capture_output=True, text=True)
                self.profile["os"]["kernel"] = result.stdout.strip()
            except:
                pass
        
        print(f"   ✅ OS: {self.profile['os']['system']} {self.profile['os']['release']}")
        print(f"   ✅ Architecture: {self.profile['os']['architecture']}")
    
    def get_hardware_info(self):
        """Catalog hardware specifications"""
        print("\n🔧 Cataloging Hardware...")
        
        hardware = {
            "cpu": {},
            "memory": {},
            "disk": {},
            "gpu": []
        }
        
        # CPU Information
        try:
            import multiprocessing
            hardware["cpu"]["cores"] = multiprocessing.cpu_count()
            hardware["cpu"]["processor"] = platform.processor()
            
            if platform.system() == "Windows":
                try:
                    result = subprocess.run(['wmic', 'cpu', 'get', 'name'], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        if len(lines) > 1:
                            hardware["cpu"]["model"] = lines[1].strip()
                except:
                    pass
            
            elif platform.system() == "Linux":
                try:
                    with open('/proc/cpuinfo', 'r') as f:
                        for line in f:
                            if 'model name' in line:
                                hardware["cpu"]["model"] = line.split(':', 1)[1].strip()
                                break
                except:
                    pass
            
            elif platform.system() == "Darwin":  # macOS
                try:
                    result = subprocess.run(['sysctl', '-n', 'machdep.cpu.brand_string'],
                                          capture_output=True, text=True)
                    hardware["cpu"]["model"] = result.stdout.strip()
                except:
                    pass
        except:
            pass
        
        # Memory Information
        try:
            if platform.system() == "Windows":
                result = subprocess.run(['wmic', 'computersystem', 'get', 'totalphysicalmemory'],
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:
                        total_bytes = int(lines[1].strip())
                        hardware["memory"]["total_bytes"] = total_bytes
                        hardware["memory"]["total_gb"] = round(total_bytes / (1024**3), 2)
            
            elif platform.system() == "Linux":
                with open('/proc/meminfo', 'r') as f:
                    for line in f:
                        if 'MemTotal' in line:
                            kb = int(line.split()[1])
                            hardware["memory"]["total_bytes"] = kb * 1024
                            hardware["memory"]["total_gb"] = round(kb / (1024**2), 2)
                            break
            
            elif platform.system() == "Darwin":
                result = subprocess.run(['sysctl', '-n', 'hw.memsize'],
                                      capture_output=True, text=True)
                total_bytes = int(result.stdout.strip())
                hardware["memory"]["total_gb"] = round(total_bytes / (1024**3), 2)
                hardware["memory"]["total_bytes"] = total_bytes
        except:
            pass
        
        # Disk Information
        try:
            if shutil.disk_usage:
                usage = shutil.disk_usage('/')
                hardware["disk"]["total_bytes"] = usage.total
                hardware["disk"]["total_gb"] = round(usage.total / (1024**3), 2)
                hardware["disk"]["free_bytes"] = usage.free
                hardware["disk"]["free_gb"] = round(usage.free / (1024**3), 2)
                hardware["disk"]["used_bytes"] = usage.used
                hardware["disk"]["used_gb"] = round(usage.used / (1024**3), 2)
                hardware["disk"]["percent_used"] = round((usage.used / usage.total) * 100, 2)
        except:
            pass
        
        # GPU Information
        try:
            if platform.system() == "Windows":
                result = subprocess.run(['wmic', 'path', 'win32_VideoController', 'get', 'name'],
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')[1:]
                    hardware["gpu"] = [line.strip() for line in lines if line.strip()]
            
            elif platform.system() == "Linux":
                try:
                    result = subprocess.run(['lspci'], capture_output=True, text=True)
                    for line in result.stdout.split('\n'):
                        if 'VGA' in line or 'Display' in line or '3D' in line:
                            hardware["gpu"].append(line.split(':', 1)[1].strip() if ':' in line else line)
                except:
                    pass
        except:
            pass
        
        self.profile["hardware"] = hardware
        
        print(f"   ✅ CPU: {hardware['cpu'].get('model', 'Unknown')} ({hardware['cpu'].get('cores', 0)} cores)")
        print(f"   ✅ RAM: {hardware['memory'].get('total_gb', 0)} GB")
        print(f"   ✅ Disk: {hardware['disk'].get('total_gb', 0)} GB total, {hardware['disk'].get('free_gb', 0)} GB free")
        if hardware["gpu"]:
            print(f"   ✅ GPU: {', '.join(hardware['gpu'][:2])}")
    
    def get_software_capabilities(self):
        """Catalog installed software and capabilities"""
        print("\n💻 Cataloging Software Capabilities...")
        
        software = {
            "languages": {},
            "frameworks": {},
            "tools": {},
            "package_managers": {}
        }
        
        # Programming Languages
        languages_to_check = {
            "python": ["python", "--version"],
            "python3": ["python3", "--version"],
            "node": ["node", "--version"],
            "npm": ["npm", "--version"],
            "java": ["java", "-version"],
            "go": ["go", "version"],
            "rust": ["rustc", "--version"],
            "ruby": ["ruby", "--version"],
            "php": ["php", "--version"],
            "dotnet": ["dotnet", "--version"],
            "gcc": ["gcc", "--version"],
            "g++": ["g++", "--version"]
        }
        
        for lang, cmd in languages_to_check.items():
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    version = result.stdout.strip().split('\n')[0] if result.stdout else result.stderr.strip().split('\n')[0]
                    software["languages"][lang] = {
                        "installed": True,
                        "version": version,
                        "path": shutil.which(cmd[0])
                    }
                    print(f"   ✅ {lang}: {version[:60]}")
            except:
                software["languages"][lang] = {"installed": False}
        
        # Package Managers
        package_managers = {
            "pip": ["pip", "--version"],
            "conda": ["conda", "--version"],
            "brew": ["brew", "--version"],
            "apt": ["apt", "--version"],
            "chocolatey": ["choco", "--version"],
            "yarn": ["yarn", "--version"]
        }
        
        for pm, cmd in package_managers.items():
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    software["package_managers"][pm] = {"installed": True}
            except:
                software["package_managers"][pm] = {"installed": False}
        
        # Development Tools
        dev_tools = {
            "git": ["git", "--version"],
            "docker": ["docker", "--version"],
            "kubectl": ["kubectl", "version", "--client"],
            "terraform": ["terraform", "--version"],
            "ansible": ["ansible", "--version"],
            "make": ["make", "--version"],
            "cmake": ["cmake", "--version"]
        }
        
        for tool, cmd in dev_tools.items():
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    software["tools"][tool] = {"installed": True}
            except:
                software["tools"][tool] = {"installed": False}
        
        # ML/AI Frameworks (Python-based)
        if software["languages"].get("python", {}).get("installed") or software["languages"].get("python3", {}).get("installed"):
            ml_frameworks = ["torch", "tensorflow", "transformers", "numpy", "pandas", "scikit-learn"]
            for fw in ml_frameworks:
                try:
                    python_cmd = "python3" if software["languages"].get("python3", {}).get("installed") else "python"
                    result = subprocess.run([python_cmd, "-c", f"import {fw}; print({fw}.__version__)"],
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        software["frameworks"][fw] = {
                            "installed": True,
                            "version": result.stdout.strip()
                        }
                except:
                    software["frameworks"][fw] = {"installed": False}
        
        self.profile["software"] = software
    
    def analyze_capabilities(self):
        """Analyze what the system can do"""
        print("\n🎯 Analyzing System Capabilities...")
        
        capabilities = {
            "can_code": False,
            "can_ml_training": False,
            "can_run_models": False,
            "can_build_apps": False,
            "can_containerize": False,
            "has_gpu": False,
            "languages_available": [],
            "frameworks_available": [],
            "recommended_use_cases": []
        }
        
        # Check coding capability
        installed_langs = [lang for lang, info in self.profile["software"]["languages"].items() 
                          if info.get("installed")]
        capabilities["languages_available"] = installed_langs
        capabilities["can_code"] = len(installed_langs) > 0
        
        # Check ML capability
        ml_frameworks = [fw for fw, info in self.profile["software"]["frameworks"].items()
                        if info.get("installed")]
        capabilities["frameworks_available"] = ml_frameworks
        
        ram_gb = self.profile["hardware"]["memory"].get("total_gb", 0)
        capabilities["can_ml_training"] = len(ml_frameworks) > 0 and ram_gb >= 8
        capabilities["can_run_models"] = len(ml_frameworks) > 0 and ram_gb >= 4
        
        # Check GPU
        capabilities["has_gpu"] = len(self.profile["hardware"].get("gpu", [])) > 0
        
        # Check build capability
        has_build_tools = any([
            self.profile["software"]["tools"].get("docker", {}).get("installed"),
            self.profile["software"]["tools"].get("make", {}).get("installed"),
            self.profile["software"]["package_managers"].get("npm", {}).get("installed")
        ])
        capabilities["can_build_apps"] = has_build_tools
        capabilities["can_containerize"] = self.profile["software"]["tools"].get("docker", {}).get("installed", False)
        
        # Recommend use cases
        use_cases = []
        
        if "python" in installed_langs or "python3" in installed_langs:
            use_cases.append("Python development")
            if ml_frameworks:
                use_cases.append("ML/AI development")
                use_cases.append("Data science")
        
        if "node" in installed_langs:
            use_cases.append("Web development (Node.js)")
        
        if capabilities["can_containerize"]:
            use_cases.append("Containerized applications")
        
        if capabilities["has_gpu"]:
            use_cases.append("GPU-accelerated computing")
            use_cases.append("ML model training")
        
        if ram_gb >= 16:
            use_cases.append("Large-scale data processing")
            use_cases.append("Multi-container orchestration")
        
        capabilities["recommended_use_cases"] = use_cases
        self.profile["capabilities"] = capabilities
        
        print(f"   ✅ Can Code: {capabilities['can_code']}")
        print(f"   ✅ Can Train ML Models: {capabilities['can_ml_training']}")
        print(f"   ✅ Has GPU: {capabilities['has_gpu']}")
        print(f"   ✅ Languages: {', '.join(installed_langs[:5])}")
    
    def analyze_resources(self):
        """Analyze available resources"""
        print("\n📊 Analyzing Resources...")
        
        resources = {
            "memory": {},
            "disk": {},
            "performance_tier": "unknown"
        }
        
        ram_gb = self.profile["hardware"]["memory"].get("total_gb", 0)
        disk_free_gb = self.profile["hardware"]["disk"].get("free_gb", 0)
        cpu_cores = self.profile["hardware"]["cpu"].get("cores", 0)
        
        # Memory analysis
        if ram_gb > 0:
            resources["memory"] = {
                "total_gb": ram_gb,
                "tier": "high" if ram_gb >= 32 else "medium" if ram_gb >= 16 else "low",
                "suitable_for": []
            }
            
            if ram_gb >= 32:
                resources["memory"]["suitable_for"] = ["Large ML training", "Multiple VMs", "Heavy development"]
            elif ram_gb >= 16:
                resources["memory"]["suitable_for"] = ["ML training", "Web services", "Development"]
            elif ram_gb >= 8:
                resources["memory"]["suitable_for"] = ["Small ML models", "Web development", "Scripting"]
            else:
                resources["memory"]["suitable_for"] = ["Scripting", "Light development"]
        
        # Disk analysis
        if disk_free_gb > 0:
            resources["disk"] = {
                "free_gb": disk_free_gb,
                "tier": "high" if disk_free_gb >= 500 else "medium" if disk_free_gb >= 100 else "low",
                "can_store": []
            }
            
            if disk_free_gb >= 500:
                resources["disk"]["can_store"] = ["Large datasets", "Multiple models", "Docker images"]
            elif disk_free_gb >= 100:
                resources["disk"]["can_store"] = ["Datasets", "Models", "Source code"]
            else:
                resources["disk"]["can_store"] = ["Source code", "Small datasets"]
        
        # Performance tier
        if ram_gb >= 32 and cpu_cores >= 8:
            resources["performance_tier"] = "high_performance"
        elif ram_gb >= 16 and cpu_cores >= 4:
            resources["performance_tier"] = "medium_performance"
        else:
            resources["performance_tier"] = "basic_performance"
        
        self.profile["resources"] = resources
        
        print(f"   ✅ RAM: {ram_gb} GB ({resources['memory'].get('tier', 'unknown')} tier)")
        print(f"   ✅ Free Disk: {disk_free_gb} GB ({resources['disk'].get('tier', 'unknown')} tier)")
        print(f"   ✅ Performance: {resources['performance_tier']}")
    
    def generate_recommendations(self):
        """Generate upgrade and utilization recommendations"""
        print("\n💡 Generating Recommendations...")
        
        recommendations = {
            "immediate_actions": [],
            "short_term_upgrades": [],
            "long_term_upgrades": [],
            "utilization_suggestions": [],
            "cost_estimates": {}
        }
        
        ram_gb = self.profile["hardware"]["memory"].get("total_gb", 0)
        disk_free_gb = self.profile["hardware"]["disk"].get("free_gb", 0)
        has_gpu = self.profile["capabilities"]["has_gpu"]
        
        # Immediate actions
        if disk_free_gb < 50:
            recommendations["immediate_actions"].append({
                "action": "Free up disk space",
                "reason": f"Only {disk_free_gb} GB free - risk of running out",
                "priority": "critical"
            })
        
        if not self.profile["software"]["languages"].get("python", {}).get("installed"):
            recommendations["immediate_actions"].append({
                "action": "Install Python 3.11+",
                "reason": "Required for ML/AI development and automation",
                "priority": "high"
            })
        
        if not self.profile["software"]["tools"].get("git", {}).get("installed"):
            recommendations["immediate_actions"].append({
                "action": "Install Git",
                "reason": "Essential for version control and collaboration",
                "priority": "high"
            })
        
        # Short-term upgrades
        if ram_gb < 16:
            recommendations["short_term_upgrades"].append({
                "upgrade": f"Upgrade RAM to 16GB (currently {ram_gb} GB)",
                "reason": "Enable ML training and multi-tasking",
                "estimated_cost_usd": 50,
                "impact": "high"
            })
            recommendations["cost_estimates"]["ram_upgrade"] = 50
        
        if not has_gpu:
            recommendations["short_term_upgrades"].append({
                "upgrade": "Consider cloud GPU (e.g., Google Colab, Kaggle)",
                "reason": "Free GPU access for ML training without hardware purchase",
                "estimated_cost_usd": 0,
                "impact": "high"
            })
        
        if disk_free_gb < 100:
            recommendations["short_term_upgrades"].append({
                "upgrade": "Add external SSD (500GB+)",
                "reason": "Insufficient space for datasets and models",
                "estimated_cost_usd": 50,
                "impact": "medium"
            })
            recommendations["cost_estimates"]["ssd_upgrade"] = 50
        
        # Long-term upgrades
        if ram_gb < 32 and ram_gb >= 16:
            recommendations["long_term_upgrades"].append({
                "upgrade": f"Upgrade RAM to 32GB (currently {ram_gb} GB)",
                "reason": "Enable large-scale ML training and complex workloads",
                "estimated_cost_usd": 100,
                "impact": "medium"
            })
        
        if not has_gpu:
            recommendations["long_term_upgrades"].append({
                "upgrade": "Add dedicated GPU (RTX 3060 or better)",
                "reason": "Significant ML training speedup",
                "estimated_cost_usd": 300,
                "impact": "high"
            })
            recommendations["cost_estimates"]["gpu_upgrade"] = 300
        
        # Utilization suggestions
        python_installed = self.profile["software"]["languages"].get("python", {}).get("installed") or \
                          self.profile["software"]["languages"].get("python3", {}).get("installed")
        
        if python_installed:
            recommendations["utilization_suggestions"].append({
                "suggestion": "Deploy TIA-ARCHITECT-CORE locally",
                "benefit": "Run AI agents on your laptop",
                "requirements": "Python 3.11+, 4GB+ RAM"
            })
            
            recommendations["utilization_suggestions"].append({
                "suggestion": "Run local LLM with Ollama",
                "benefit": "Private AI inference without cloud",
                "requirements": "8GB+ RAM, CPU or GPU"
            })
        
        if ram_gb >= 8:
            recommendations["utilization_suggestions"].append({
                "suggestion": "Run lightweight Docker containers",
                "benefit": "Deploy microservices and APIs locally",
                "requirements": "Docker installed, 8GB+ RAM"
            })
        
        if has_gpu:
            recommendations["utilization_suggestions"].append({
                "suggestion": "Fine-tune small language models",
                "benefit": "Create custom AI models for specific tasks",
                "requirements": "GPU, 16GB+ RAM, PyTorch/TensorFlow"
            })
        
        recommendations["utilization_suggestions"].append({
            "suggestion": "Use laptop as bridge node in Citadel Mesh",
            "benefit": "Contribute to distributed intelligence network",
            "requirements": "Internet connection, Python 3.11+"
        })
        
        self.profile["recommendations"] = recommendations
        
        print(f"   ✅ Generated {len(recommendations['immediate_actions'])} immediate actions")
        print(f"   ✅ Generated {len(recommendations['short_term_upgrades'])} short-term upgrades")
        print(f"   ✅ Generated {len(recommendations['utilization_suggestions'])} utilization suggestions")
    
    def generate_report(self, output_file=None):
        """Generate comprehensive report"""
        print("\n📄 Generating Report...")
        
        if not output_file:
            output_file = self.output_dir / f"system_profile_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Save JSON profile
        with open(output_file, 'w') as f:
            json.dump(self.profile, f, indent=2)
        
        print(f"\n✅ Profile saved: {output_file}")
        
        # Create symlink to latest
        latest_link = self.output_dir / "system_profile_latest.json"
        if latest_link.exists():
            latest_link.unlink()
        latest_link.symlink_to(output_file.name)
        
        # Generate markdown report
        md_file = output_file.with_suffix('.md')
        self.generate_markdown_report(md_file)
        
        return output_file
    
    def generate_markdown_report(self, md_file):
        """Generate human-readable markdown report"""
        
        with open(md_file, 'w') as f:
            f.write("# 📚 System Profile & Upgrade Recommendations\n\n")
            f.write(f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n")
            f.write(f"**Hostname:** {self.profile['hostname']}\n\n")
            
            f.write("---\n\n")
            
            # Operating System
            f.write("## 🖥️ Operating System\n\n")
            os_info = self.profile["os"]
            f.write(f"- **System:** {os_info.get('system')} {os_info.get('release')}\n")
            f.write(f"- **Architecture:** {os_info.get('architecture')}\n")
            f.write(f"- **Python:** {os_info.get('python_version')}\n\n")
            
            # Hardware
            f.write("## 🔧 Hardware\n\n")
            hw = self.profile["hardware"]
            f.write(f"- **CPU:** {hw['cpu'].get('model', 'Unknown')} ({hw['cpu'].get('cores', 0)} cores)\n")
            f.write(f"- **RAM:** {hw['memory'].get('total_gb', 0)} GB\n")
            f.write(f"- **Disk:** {hw['disk'].get('total_gb', 0)} GB total, {hw['disk'].get('free_gb', 0)} GB free ({hw['disk'].get('percent_used', 0)}% used)\n")
            if hw.get("gpu"):
                f.write(f"- **GPU:** {', '.join(hw['gpu'])}\n")
            f.write("\n")
            
            # Software
            f.write("## 💻 Software Capabilities\n\n")
            sw = self.profile["software"]
            
            installed_langs = [lang for lang, info in sw["languages"].items() if info.get("installed")]
            if installed_langs:
                f.write("### Programming Languages\n\n")
                for lang in installed_langs:
                    version = sw["languages"][lang].get("version", "")
                    f.write(f"- ✅ **{lang.title()}:** {version}\n")
                f.write("\n")
            
            installed_frameworks = [fw for fw, info in sw["frameworks"].items() if info.get("installed")]
            if installed_frameworks:
                f.write("### ML/AI Frameworks\n\n")
                for fw in installed_frameworks:
                    version = sw["frameworks"][fw].get("version", "")
                    f.write(f"- ✅ **{fw}:** {version}\n")
                f.write("\n")
            
            # Capabilities
            f.write("## 🎯 System Capabilities\n\n")
            cap = self.profile["capabilities"]
            f.write(f"- **Can Code:** {'✅ Yes' if cap['can_code'] else '❌ No'}\n")
            f.write(f"- **Can Train ML Models:** {'✅ Yes' if cap['can_ml_training'] else '❌ No'}\n")
            f.write(f"- **Can Run Models:** {'✅ Yes' if cap['can_run_models'] else '❌ No'}\n")
            f.write(f"- **Has GPU:** {'✅ Yes' if cap['has_gpu'] else '❌ No'}\n")
            f.write(f"- **Can Containerize:** {'✅ Yes' if cap['can_containerize'] else '❌ No'}\n\n")
            
            if cap.get("recommended_use_cases"):
                f.write("### Recommended Use Cases\n\n")
                for use_case in cap["recommended_use_cases"]:
                    f.write(f"- {use_case}\n")
                f.write("\n")
            
            # Resources
            f.write("## 📊 Resource Analysis\n\n")
            res = self.profile["resources"]
            f.write(f"- **Performance Tier:** {res.get('performance_tier', 'unknown').replace('_', ' ').title()}\n")
            if res.get("memory", {}).get("suitable_for"):
                f.write(f"- **Memory Use Cases:** {', '.join(res['memory']['suitable_for'])}\n")
            if res.get("disk", {}).get("can_store"):
                f.write(f"- **Storage Use Cases:** {', '.join(res['disk']['can_store'])}\n")
            f.write("\n")
            
            # Recommendations
            f.write("## 💡 Recommendations\n\n")
            rec = self.profile["recommendations"]
            
            if rec.get("immediate_actions"):
                f.write("### ⚠️ Immediate Actions\n\n")
                for action in rec["immediate_actions"]:
                    f.write(f"- **{action['action']}**\n")
                    f.write(f"  - Reason: {action['reason']}\n")
                    f.write(f"  - Priority: {action['priority']}\n\n")
            
            if rec.get("short_term_upgrades"):
                f.write("### 🔧 Short-Term Upgrades (0-3 months)\n\n")
                for upgrade in rec["short_term_upgrades"]:
                    f.write(f"- **{upgrade['upgrade']}**\n")
                    f.write(f"  - Reason: {upgrade['reason']}\n")
                    f.write(f"  - Estimated Cost: ${upgrade['estimated_cost_usd']}\n")
                    f.write(f"  - Impact: {upgrade['impact']}\n\n")
            
            if rec.get("long_term_upgrades"):
                f.write("### 🚀 Long-Term Upgrades (3-12 months)\n\n")
                for upgrade in rec["long_term_upgrades"]:
                    f.write(f"- **{upgrade['upgrade']}**\n")
                    f.write(f"  - Reason: {upgrade['reason']}\n")
                    f.write(f"  - Estimated Cost: ${upgrade['estimated_cost_usd']}\n")
                    f.write(f"  - Impact: {upgrade['impact']}\n\n")
            
            if rec.get("utilization_suggestions"):
                f.write("### 🎯 How to Utilize This System Now\n\n")
                for suggestion in rec["utilization_suggestions"]:
                    f.write(f"- **{suggestion['suggestion']}**\n")
                    f.write(f"  - Benefit: {suggestion['benefit']}\n")
                    f.write(f"  - Requirements: {suggestion['requirements']}\n\n")
            
            if rec.get("cost_estimates"):
                f.write("### 💰 Total Upgrade Cost Estimate\n\n")
                total = sum(rec["cost_estimates"].values())
                for upgrade, cost in rec["cost_estimates"].items():
                    f.write(f"- {upgrade.replace('_', ' ').title()}: ${cost}\n")
                f.write(f"\n**Total:** ${total}\n\n")
            
            f.write("---\n\n")
            f.write("*Generated by System Librarian - Citadel Mesh Intelligence*\n")
        
        print(f"✅ Markdown report saved: {md_file}")


def main():
    parser = argparse.ArgumentParser(description="System Librarian - Profile and optimize your laptop")
    parser.add_argument("--output", help="Output JSON file path")
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("📚 SYSTEM LIBRARIAN")
    print("   Comprehensive System Profiling & Upgrade Recommendations")
    print("="*70)
    
    librarian = SystemLibrarian()
    
    librarian.get_os_info()
    librarian.get_hardware_info()
    librarian.get_software_capabilities()
    librarian.analyze_capabilities()
    librarian.analyze_resources()
    librarian.generate_recommendations()
    
    output_file = librarian.generate_report(args.output)
    
    print("\n" + "="*70)
    print("✅ SYSTEM PROFILING COMPLETE")
    print("="*70)
    
    print(f"\n📁 Output Files:")
    print(f"   JSON: {output_file}")
    print(f"   Markdown: {output_file.with_suffix('.md')}")
    print(f"   Latest: {output_file.parent / 'system_profile_latest.json'}")
    
    print(f"\n🎯 Next Steps:")
    print(f"   1. Review the markdown report for recommendations")
    print(f"   2. Implement immediate actions")
    print(f"   3. Plan short-term upgrades")
    print(f"   4. Integrate into laptop sync workflow")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()
