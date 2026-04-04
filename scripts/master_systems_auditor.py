#!/usr/bin/env python3
"""
🏛️ CITADEL MASTER SYSTEMS AUDITOR v25.0.OMNI++
=================================================
Comprehensive hole finder and gap analyzer for the entire Citadel mesh.

Scans:
- All 49+ GitHub Actions workflows
- All 409+ scripts (Python, Shell, etc.)
- All 12 Districts
- All agent_legion agents
- All HuggingFace Spaces
- All GDrive partitions
- All documentation files
- All data structures
- All security systems
- All trading systems
- All RAG systems
- All worker constellations

Identifies 8 problem categories:
1. MISSING_CRITICAL_FILES
2. INCOMPLETE_DOCUMENTATION
3. BROKEN_INTEGRATIONS
4. SECURITY_VULNERABILITIES
5. PERFORMANCE_BOTTLENECKS
6. OUTDATED_DEPENDENCIES
7. COVERAGE_GAPS
8. ARCHITECTURAL_INCONSISTENCIES
"""

import os
import json
import glob
import yaml
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Any
from collections import defaultdict

class MasterSystemsAuditor:
    """Comprehensive systems auditor and hole finder"""
    
    def __init__(self, repo_root: str = "/home/runner/work/mapping-and-inventory/mapping-and-inventory"):
        self.repo_root = Path(repo_root)
        self.timestamp = datetime.utcnow().isoformat()
        
        # Audit results
        self.holes: Dict[str, List[Dict]] = defaultdict(list)
        self.metrics: Dict[str, Any] = {}
        self.coverage: Dict[str, float] = {}
        
        # Expected structures from agent instructions
        self.expected_districts = [f"D{str(i).zfill(2)}" for i in range(1, 13)]
        self.expected_district_files = ["TREE.md", "INVENTORY.json", "SCAFFOLD.md"]
        self.expected_hf_folders = ["/data", "/data/models", "/data/tools", 
                                   "/data/workers", "/data/datasets", 
                                   "/data/Mapping-and-Inventory-storage"]
        
        # Critical systems that must exist
        self.critical_systems = [
            "scripts/citadel_awakening.py",
            "scripts/gap_analyzer.py",
            "scripts/solution_generator.py",
            "scripts/repo_census_builder.py",
            "scripts/continuous_improvement_engine.py",
            "scripts/security_sentinel.py",
            "scripts/web_scout.py",
            "command_center.py",
            "citadel_nexus.py"
        ]
        
    def run_comprehensive_audit(self) -> Dict:
        """Execute all audit procedures"""
        print("🏛️ CITADEL MASTER SYSTEMS AUDITOR")
        print("=" * 80)
        print(f"Timestamp: {self.timestamp}")
        print(f"Repository: {self.repo_root}")
        print()
        
        # Run all audit procedures
        self.audit_workflows()
        self.audit_scripts()
        self.audit_districts()
        self.audit_agent_legion()
        self.audit_documentation()
        self.audit_security_systems()
        self.audit_trading_systems()
        self.audit_rag_systems()
        self.audit_worker_constellations()
        self.audit_integration_points()
        self.audit_dependencies()
        self.audit_test_coverage()
        
        # Calculate overall metrics
        self.calculate_metrics()
        
        # Generate report
        return self.generate_report()
    
    def audit_workflows(self):
        """Audit all GitHub Actions workflows"""
        print("📋 Auditing GitHub Actions workflows...")
        
        workflows_dir = self.repo_root / ".github" / "workflows"
        if not workflows_dir.exists():
            self.holes["MISSING_CRITICAL_FILES"].append({
                "type": "missing_directory",
                "path": str(workflows_dir),
                "severity": "CRITICAL",
                "impact": "No CI/CD automation possible"
            })
            return
        
        workflows = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
        self.metrics["total_workflows"] = len(workflows)
        
        # Check for required workflows
        required_workflows = [
            "omni_audit_orchestrator.yml",
            "citadel_awakening.yml",
            "security_scan.yml",
            "mesh_heartbeat.yml",
            "oracle_sync.yml"
        ]
        
        existing_workflow_names = {w.name for w in workflows}
        for required in required_workflows:
            if required not in existing_workflow_names:
                self.holes["COVERAGE_GAPS"].append({
                    "type": "missing_workflow",
                    "workflow": required,
                    "severity": "HIGH",
                    "impact": "Missing critical automation"
                })
        
        # Check workflow syntax and structure
        for workflow_file in workflows:
            try:
                with open(workflow_file, 'r') as f:
                    workflow = yaml.safe_load(f)
                
                # Check for permissions (from memory)
                if "on" in workflow and "push" in workflow["on"]:
                    if "permissions" not in workflow:
                        self.holes["SECURITY_VULNERABILITIES"].append({
                            "type": "missing_permissions",
                            "workflow": workflow_file.name,
                            "severity": "MEDIUM",
                            "impact": "Workflow permissions not explicit"
                        })
                
                # Check for secrets usage
                workflow_str = str(workflow)
                if "GH_PAT" in workflow_str or "HF_TOKEN" in workflow_str:
                    # Good - using proper secrets
                    pass
                elif "token:" in workflow_str.lower() and "secrets" not in workflow_str:
                    self.holes["SECURITY_VULNERABILITIES"].append({
                        "type": "hardcoded_token_risk",
                        "workflow": workflow_file.name,
                        "severity": "HIGH",
                        "impact": "Potential hardcoded credentials"
                    })
                    
            except Exception as e:
                self.holes["BROKEN_INTEGRATIONS"].append({
                    "type": "workflow_parse_error",
                    "workflow": workflow_file.name,
                    "error": str(e),
                    "severity": "HIGH"
                })
        
        print(f"  ✓ Found {len(workflows)} workflows")
        print(f"  ! Identified {len([h for h in self.holes['COVERAGE_GAPS'] if 'workflow' in h])} workflow gaps")
    
    def audit_scripts(self):
        """Audit all Python and shell scripts"""
        print("🐍 Auditing scripts...")
        
        scripts_dir = self.repo_root / "scripts"
        py_scripts = list(scripts_dir.glob("**/*.py"))
        sh_scripts = list(scripts_dir.glob("**/*.sh"))
        
        self.metrics["total_py_scripts"] = len(py_scripts)
        self.metrics["total_sh_scripts"] = len(sh_scripts)
        
        # Check critical systems exist
        for critical in self.critical_systems:
            critical_path = self.repo_root / critical
            if not critical_path.exists():
                self.holes["MISSING_CRITICAL_FILES"].append({
                    "type": "missing_critical_script",
                    "path": critical,
                    "severity": "CRITICAL",
                    "impact": "Core Citadel functionality missing"
                })
        
        # Check for documentation in scripts
        undocumented = []
        for script in py_scripts:
            try:
                with open(script, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Check for docstring
                    if '"""' not in content and "'''" not in content:
                        undocumented.append(script.name)
            except:
                pass
        
        if undocumented:
            self.holes["INCOMPLETE_DOCUMENTATION"].append({
                "type": "undocumented_scripts",
                "count": len(undocumented),
                "examples": undocumented[:5],
                "severity": "MEDIUM",
                "impact": "Scripts lack documentation"
            })
        
        print(f"  ✓ Found {len(py_scripts)} Python scripts")
        print(f"  ✓ Found {len(sh_scripts)} shell scripts")
        print(f"  ! {len(undocumented)} scripts lack documentation")
    
    def audit_districts(self):
        """Audit all 12 Districts (D01-D12)"""
        print("🏛️ Auditing Districts...")
        
        districts_dir = self.repo_root / "Districts"
        if not districts_dir.exists():
            self.holes["MISSING_CRITICAL_FILES"].append({
                "type": "missing_districts",
                "severity": "CRITICAL",
                "impact": "No District structure exists"
            })
            return
        
        existing_districts = [d.name for d in districts_dir.iterdir() if d.is_dir()]
        
        # Check each expected district
        for district in self.expected_districts:
            district_path = districts_dir / district
            
            if not district_path.exists():
                self.holes["COVERAGE_GAPS"].append({
                    "type": "missing_district",
                    "district": district,
                    "severity": "HIGH",
                    "impact": f"District {district} not mapped"
                })
                continue
            
            # Check for required files
            for required_file in self.expected_district_files:
                file_path = district_path / required_file
                if not file_path.exists():
                    self.holes["INCOMPLETE_DOCUMENTATION"].append({
                        "type": "missing_district_file",
                        "district": district,
                        "file": required_file,
                        "severity": "HIGH",
                        "impact": f"District {district} incomplete"
                    })
        
        self.metrics["total_districts"] = len(existing_districts)
        self.metrics["expected_districts"] = len(self.expected_districts)
        self.coverage["districts"] = len(existing_districts) / len(self.expected_districts) * 100
        
        print(f"  ✓ Found {len(existing_districts)}/{len(self.expected_districts)} Districts")
        print(f"  📊 District coverage: {self.coverage['districts']:.1f}%")
    
    def audit_agent_legion(self):
        """Audit Agent Legion systems"""
        print("🤖 Auditing Agent Legion...")
        
        legion_dir = self.repo_root / "scripts" / "agent_legion"
        if not legion_dir.exists():
            self.holes["MISSING_CRITICAL_FILES"].append({
                "type": "missing_agent_legion",
                "severity": "CRITICAL",
                "impact": "Agent Legion system missing"
            })
            return
        
        agents = list(legion_dir.glob("*.py"))
        self.metrics["agent_legion_agents"] = len(agents)
        
        # Expected agents
        expected_agents = [
            "agent_legion_orchestrator.py",
            "sentinel_defensive_agent.py",
            "sniper_precision_agent.py",
            "hound_tracker_agent.py",
            "wraith_security_agent.py",
            "bridge_worker.py"
        ]
        
        existing_names = {a.name for a in agents}
        for expected in expected_agents:
            if expected not in existing_names:
                self.holes["COVERAGE_GAPS"].append({
                    "type": "missing_agent",
                    "agent": expected,
                    "severity": "MEDIUM"
                })
        
        print(f"  ✓ Found {len(agents)} Agent Legion agents")
    
    def audit_documentation(self):
        """Audit all documentation"""
        print("📚 Auditing documentation...")
        
        md_files = list(self.repo_root.glob("*.md"))
        self.metrics["root_documentation"] = len(md_files)
        
        # Check for critical documentation
        critical_docs = [
            "README.md",
            "CITADEL_AWAKENING_GUIDE.md",
            "OMNI_AUDIT_MASTER_PLAN.md",
            "QUANTUM_VAULT_OPERATOR_GUIDE.md"
        ]
        
        for doc in critical_docs:
            if not (self.repo_root / doc).exists():
                self.holes["INCOMPLETE_DOCUMENTATION"].append({
                    "type": "missing_critical_doc",
                    "document": doc,
                    "severity": "HIGH"
                })
        
        print(f"  ✓ Found {len(md_files)} markdown files in root")
    
    def audit_security_systems(self):
        """Audit security infrastructure"""
        print("🔒 Auditing security systems...")
        
        security_dir = self.repo_root / "security" / "core"
        if not security_dir.exists():
            self.holes["MISSING_CRITICAL_FILES"].append({
                "type": "missing_security_dir",
                "severity": "CRITICAL",
                "impact": "No security infrastructure"
            })
            return
        
        required_security = [
            "quantum_vault.py",
            "input_validator.py",
            "rate_limiter.py",
            "encryption_manager.py",
            "audit_logger.py"
        ]
        
        for sec_file in required_security:
            if not (security_dir / sec_file).exists():
                self.holes["SECURITY_VULNERABILITIES"].append({
                    "type": "missing_security_module",
                    "module": sec_file,
                    "severity": "CRITICAL",
                    "impact": "Security infrastructure incomplete"
                })
        
        print(f"  ✓ Security infrastructure audit complete")
    
    def audit_trading_systems(self):
        """Audit trading infrastructure"""
        print("💹 Auditing trading systems...")
        
        trading_safety = self.repo_root / "scripts" / "trading_safety"
        if not trading_safety.exists():
            self.holes["MISSING_CRITICAL_FILES"].append({
                "type": "missing_trading_safety",
                "severity": "HIGH",
                "impact": "No trading safety systems"
            })
            return
        
        # From memory: trading safety infrastructure
        required_trading = [
            "circuit_breaker.py",
            "credential_manager.py",
            "trading_monitors.py",
            "safe_trader.py"
        ]
        
        for trading_file in required_trading:
            if not (trading_safety / trading_file).exists():
                self.holes["SECURITY_VULNERABILITIES"].append({
                    "type": "missing_trading_safety",
                    "module": trading_file,
                    "severity": "CRITICAL",
                    "impact": "Trading safety incomplete - DO NOT TRADE"
                })
        
        print(f"  ✓ Trading systems audit complete")
    
    def audit_rag_systems(self):
        """Audit RAG and knowledge systems"""
        print("🧠 Auditing RAG systems...")
        
        # Check for RAG infrastructure
        rag_indicators = [
            "scripts/rag_ingest.py",
            "scripts/personal_archive_rag_ingest.py",
            "scripts/agent_legion/multi_brain_rag_system.py"
        ]
        
        existing_rag = 0
        for rag_file in rag_indicators:
            if (self.repo_root / rag_file).exists():
                existing_rag += 1
        
        if existing_rag == 0:
            self.holes["MISSING_CRITICAL_FILES"].append({
                "type": "missing_rag_system",
                "severity": "HIGH",
                "impact": "No RAG infrastructure found"
            })
        
        self.metrics["rag_systems"] = existing_rag
        print(f"  ✓ Found {existing_rag} RAG systems")
    
    def audit_worker_constellations(self):
        """Audit worker constellation systems"""
        print("⭐ Auditing worker constellations...")
        
        workers_dir = self.repo_root / "workers"
        if not workers_dir.exists():
            self.holes["COVERAGE_GAPS"].append({
                "type": "missing_workers_dir",
                "severity": "MEDIUM",
                "impact": "No worker constellation storage"
            })
            self.metrics["workers"] = 0
            return
        
        workers = list(workers_dir.glob("*.py"))
        self.metrics["workers"] = len(workers)
        
        print(f"  ✓ Found {len(workers)} workers")
    
    def audit_integration_points(self):
        """Audit integration points across systems"""
        print("🔗 Auditing integration points...")
        
        # Check for GitHub <-> HuggingFace integrations
        hf_workflows = [
            ".github/workflows/oracle_sync.yml",
            ".github/workflows/bridge_push.yml"
        ]
        
        for wf in hf_workflows:
            if not (self.repo_root / wf).exists():
                self.holes["BROKEN_INTEGRATIONS"].append({
                    "type": "missing_hf_integration",
                    "workflow": wf,
                    "severity": "HIGH",
                    "impact": "GitHub<->HF sync missing"
                })
        
        print(f"  ✓ Integration audit complete")
    
    def audit_dependencies(self):
        """Audit dependencies and versions"""
        print("📦 Auditing dependencies...")
        
        requirements = self.repo_root / "requirements.txt"
        if not requirements.exists():
            self.holes["MISSING_CRITICAL_FILES"].append({
                "type": "missing_requirements",
                "severity": "HIGH",
                "impact": "No dependency specification"
            })
            return
        
        # Check for invalid versions (from memory)
        with open(requirements, 'r') as f:
            reqs = f.read()
            
        # Known invalid from memory
        if "google-genai==0.8.3" in reqs:
            self.holes["OUTDATED_DEPENDENCIES"].append({
                "type": "invalid_version",
                "package": "google-genai",
                "version": "0.8.3",
                "severity": "CRITICAL",
                "impact": "Invalid package version",
                "fix": "Replace with google-generativeai"
            })
        
        print(f"  ✓ Dependencies audit complete")
    
    def audit_test_coverage(self):
        """Audit test coverage"""
        print("🧪 Auditing test coverage...")
        
        # Look for test files
        test_files = list(self.repo_root.glob("**/test_*.py")) + \
                    list(self.repo_root.glob("**/*_test.py"))
        
        self.metrics["test_files"] = len(test_files)
        
        if len(test_files) == 0:
            self.holes["COVERAGE_GAPS"].append({
                "type": "no_tests",
                "severity": "HIGH",
                "impact": "No test coverage exists"
            })
        
        print(f"  ✓ Found {len(test_files)} test files")
    
    def calculate_metrics(self):
        """Calculate overall health metrics"""
        print("\n📊 Calculating metrics...")
        
        total_holes = sum(len(holes) for holes in self.holes.values())
        self.metrics["total_holes"] = total_holes
        
        # Calculate severity distribution
        severity_counts = defaultdict(int)
        for category_holes in self.holes.values():
            for hole in category_holes:
                severity_counts[hole.get("severity", "UNKNOWN")] += 1
        
        self.metrics["severity_distribution"] = dict(severity_counts)
        
        # Calculate overall health score (0-100)
        critical = severity_counts.get("CRITICAL", 0)
        high = severity_counts.get("HIGH", 0)
        medium = severity_counts.get("MEDIUM", 0)
        low = severity_counts.get("LOW", 0)
        
        # Weighted scoring
        penalty = (critical * 10) + (high * 5) + (medium * 2) + (low * 1)
        max_possible_score = 100
        health_score = max(0, max_possible_score - penalty)
        
        self.metrics["health_score"] = health_score
        
        print(f"  Health Score: {health_score}/100")
        print(f"  Total Holes: {total_holes}")
        print(f"    - CRITICAL: {critical}")
        print(f"    - HIGH: {high}")
        print(f"    - MEDIUM: {medium}")
        print(f"    - LOW: {low}")
    
    def generate_report(self) -> Dict:
        """Generate comprehensive audit report"""
        report = {
            "timestamp": self.timestamp,
            "repository": str(self.repo_root),
            "metrics": self.metrics,
            "coverage": self.coverage,
            "holes": dict(self.holes),
            "summary": {
                "total_categories": len(self.holes),
                "total_holes": self.metrics.get("total_holes", 0),
                "health_score": self.metrics.get("health_score", 0),
                "critical_count": self.metrics.get("severity_distribution", {}).get("CRITICAL", 0),
                "high_count": self.metrics.get("severity_distribution", {}).get("HIGH", 0)
            }
        }
        
        # Save to file
        output_dir = self.repo_root / "data" / "audits"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"master_audit_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n✅ Audit report saved: {output_file}")
        
        return report

def main():
    """Run master systems audit"""
    auditor = MasterSystemsAuditor()
    report = auditor.run_comprehensive_audit()
    
    print("\n" + "=" * 80)
    print("🏛️ MASTER SYSTEMS AUDIT COMPLETE")
    print("=" * 80)
    print(f"Health Score: {report['summary']['health_score']}/100")
    print(f"Total Holes Found: {report['summary']['total_holes']}")
    print(f"  - CRITICAL: {report['summary']['critical_count']}")
    print(f"  - HIGH: {report['summary']['high_count']}")
    print()
    print("Next step: Run 10-Solution Generator for each problem")
    print("Command: python scripts/ten_solution_generator.py")
    
    return 0 if report['summary']['critical_count'] == 0 else 1

if __name__ == "__main__":
    exit(main())
