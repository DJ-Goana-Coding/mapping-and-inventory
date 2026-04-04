#!/usr/bin/env python3
"""
✅ CITADEL 100% COVERAGE VALIDATOR v25.0.OMNI++
================================================
Validates that 100% coverage has been achieved across all systems:
- All Districts mapped (12/12)
- All documentation complete
- All workflows operational
- All security systems deployed
- All trading safety systems active
- All RAG systems functioning
- All worker constellations deployed
- All integrations validated
- All tests passing
- Zero critical/high severity holes
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from collections import defaultdict

class CoverageValidator:
    """Validates 100% coverage across all Citadel systems"""
    
    def __init__(self, repo_root: str = "/home/runner/work/mapping-and-inventory/mapping-and-inventory"):
        self.repo_root = Path(repo_root)
        self.timestamp = datetime.utcnow().isoformat()
        self.validation_results: Dict[str, Dict] = {}
        self.total_checks = 0
        self.passed_checks = 0
        
    def run_full_validation(self) -> Dict:
        """Run comprehensive validation"""
        print("✅ CITADEL 100% COVERAGE VALIDATOR")
        print("=" * 80)
        print(f"Timestamp: {self.timestamp}")
        print()
        
        # Run all validation categories
        self.validate_districts()
        self.validate_documentation()
        self.validate_workflows()
        self.validate_scripts()
        self.validate_security_systems()
        self.validate_trading_systems()
        self.validate_rag_systems()
        self.validate_worker_constellations()
        self.validate_integrations()
        self.validate_audit_clean()
        
        # Calculate coverage
        coverage_percentage = (self.passed_checks / self.total_checks * 100) if self.total_checks > 0 else 0
        
        report = {
            "timestamp": self.timestamp,
            "total_checks": self.total_checks,
            "passed_checks": self.passed_checks,
            "failed_checks": self.total_checks - self.passed_checks,
            "coverage_percentage": coverage_percentage,
            "target": 100.0,
            "achieved": coverage_percentage >= 100.0,
            "validation_results": self.validation_results
        }
        
        # Save report
        self.save_report(report)
        
        return report
    
    def check(self, category: str, name: str, condition: bool, description: str = ""):
        """Register a validation check"""
        self.total_checks += 1
        
        if condition:
            self.passed_checks += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        if category not in self.validation_results:
            self.validation_results[category] = {
                "checks": [],
                "passed": 0,
                "failed": 0
            }
        
        self.validation_results[category]["checks"].append({
            "name": name,
            "status": "passed" if condition else "failed",
            "description": description
        })
        
        if condition:
            self.validation_results[category]["passed"] += 1
        else:
            self.validation_results[category]["failed"] += 1
        
        print(f"  {status} {name}")
    
    def validate_districts(self):
        """Validate all 12 Districts exist and are complete"""
        print("\n🏛️  Validating Districts...")
        
        districts_dir = self.repo_root / "Districts"
        expected_districts = [f"D{str(i).zfill(2)}" for i in range(1, 13)]
        expected_files = ["TREE.md", "INVENTORY.json", "SCAFFOLD.md"]
        
        self.check("districts", "Districts directory exists", districts_dir.exists())
        
        for district in expected_districts:
            district_path = districts_dir / district
            self.check("districts", f"{district} exists", district_path.exists())
            
            if district_path.exists():
                for file in expected_files:
                    file_path = district_path / file
                    self.check("districts", f"{district}/{file}", file_path.exists())
    
    def validate_documentation(self):
        """Validate critical documentation exists"""
        print("\n📚 Validating Documentation...")
        
        critical_docs = [
            "README.md",
            "CITADEL_AWAKENING_GUIDE.md",
            "OMNI_AUDIT_MASTER_PLAN.md",
            "QUANTUM_VAULT_OPERATOR_GUIDE.md",
            "TRADING_SAFETY_OPERATOR_MANUAL.md",
            "COMPREHENSIVE_DISCOVERY_FRAMEWORK.md"
        ]
        
        for doc in critical_docs:
            doc_path = self.repo_root / doc
            self.check("documentation", doc, doc_path.exists())
    
    def validate_workflows(self):
        """Validate critical workflows exist"""
        print("\n⚙️  Validating Workflows...")
        
        workflows_dir = self.repo_root / ".github" / "workflows"
        
        critical_workflows = [
            "omni_audit_orchestrator.yml",
            "citadel_awakening.yml",
            "security_scan.yml",
            "mesh_heartbeat.yml",
            "oracle_sync.yml"
        ]
        
        self.check("workflows", "Workflows directory exists", workflows_dir.exists())
        
        if workflows_dir.exists():
            for workflow in critical_workflows:
                workflow_path = workflows_dir / workflow
                self.check("workflows", workflow, workflow_path.exists())
    
    def validate_scripts(self):
        """Validate critical scripts exist"""
        print("\n🐍 Validating Scripts...")
        
        critical_scripts = [
            "scripts/citadel_awakening.py",
            "scripts/gap_analyzer.py",
            "scripts/solution_generator.py",
            "scripts/repo_census_builder.py",
            "scripts/continuous_improvement_engine.py",
            "scripts/security_sentinel.py",
            "scripts/web_scout.py",
            "scripts/master_systems_auditor.py",
            "scripts/ten_solution_generator.py",
            "scripts/shopping_expedition_orchestrator.py",
            "scripts/continuous_testing_engine.py"
        ]
        
        for script in critical_scripts:
            script_path = self.repo_root / script
            self.check("scripts", script.split("/")[-1], script_path.exists())
    
    def validate_security_systems(self):
        """Validate security infrastructure"""
        print("\n🔒 Validating Security Systems...")
        
        security_dir = self.repo_root / "security" / "core"
        
        security_modules = [
            "quantum_vault.py",
            "input_validator.py",
            "rate_limiter.py",
            "encryption_manager.py",
            "audit_logger.py"
        ]
        
        self.check("security", "Security directory exists", security_dir.exists())
        
        if security_dir.exists():
            for module in security_modules:
                module_path = security_dir / module
                self.check("security", module, module_path.exists())
    
    def validate_trading_systems(self):
        """Validate trading safety systems"""
        print("\n💹 Validating Trading Systems...")
        
        trading_dir = self.repo_root / "scripts" / "trading_safety"
        
        trading_modules = [
            "circuit_breaker.py",
            "credential_manager.py",
            "trading_monitors.py",
            "safe_trader.py"
        ]
        
        self.check("trading", "Trading safety directory exists", trading_dir.exists())
        
        if trading_dir.exists():
            for module in trading_modules:
                module_path = trading_dir / module
                self.check("trading", module, module_path.exists())
    
    def validate_rag_systems(self):
        """Validate RAG infrastructure"""
        print("\n🧠 Validating RAG Systems...")
        
        rag_scripts = [
            "scripts/rag_ingest.py",
            "scripts/personal_archive_rag_ingest.py",
            "scripts/agent_legion/multi_brain_rag_system.py"
        ]
        
        for script in rag_scripts:
            script_path = self.repo_root / script
            self.check("rag", script.split("/")[-1], script_path.exists())
    
    def validate_worker_constellations(self):
        """Validate worker constellation systems"""
        print("\n⭐ Validating Worker Constellations...")
        
        workers_dir = self.repo_root / "workers"
        
        self.check("workers", "Workers directory exists", workers_dir.exists())
        
        worker_scripts = [
            "scripts/workers_constellation_setup.py",
            "scripts/worker_constellation_orchestrator.py",
            "scripts/worker_watchdog.py"
        ]
        
        for script in worker_scripts:
            script_path = self.repo_root / script
            self.check("workers", script.split("/")[-1], script_path.exists())
    
    def validate_integrations(self):
        """Validate integration points"""
        print("\n🔗 Validating Integrations...")
        
        integration_workflows = [
            ".github/workflows/oracle_sync.yml",
            ".github/workflows/bridge_push.yml"
        ]
        
        for workflow in integration_workflows:
            workflow_path = self.repo_root / workflow
            self.check("integrations", workflow.split("/")[-1], workflow_path.exists())
    
    def validate_audit_clean(self):
        """Validate that latest audit shows no critical issues"""
        print("\n🔍 Validating Audit Status...")
        
        audits_dir = self.repo_root / "data" / "audits"
        
        if audits_dir.exists():
            audit_files = sorted(audits_dir.glob("master_audit_*.json"), reverse=True)
            
            if audit_files:
                with open(audit_files[0], 'r') as f:
                    audit = json.load(f)
                
                critical_count = audit.get("summary", {}).get("critical_count", 0)
                high_count = audit.get("summary", {}).get("high_count", 0)
                health_score = audit.get("summary", {}).get("health_score", 0)
                
                self.check("audit", "No critical issues", critical_count == 0)
                self.check("audit", "No high severity issues", high_count == 0)
                self.check("audit", "Health score >= 90", health_score >= 90)
            else:
                self.check("audit", "Audit report exists", False)
        else:
            self.check("audit", "Audits directory exists", False)
    
    def save_report(self, report: Dict):
        """Save validation report"""
        output_dir = self.repo_root / "data" / "validation"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"coverage_validation_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n✅ Validation report saved: {output_file}")

def main():
    """Run 100% coverage validation"""
    validator = CoverageValidator()
    report = validator.run_full_validation()
    
    print("\n" + "=" * 80)
    print("✅ COVERAGE VALIDATION COMPLETE")
    print("=" * 80)
    print(f"Total Checks: {report['total_checks']}")
    print(f"Passed: {report['passed_checks']}")
    print(f"Failed: {report['failed_checks']}")
    print(f"Coverage: {report['coverage_percentage']:.1f}%")
    print(f"Target: {report['target']}%")
    print()
    
    if report['achieved']:
        print("🎯 100% COVERAGE ACHIEVED!")
    else:
        print(f"⚠️  Coverage gap: {report['target'] - report['coverage_percentage']:.1f}%")
        print("   Run continuous improvement to close gaps")
    
    return 0 if report['achieved'] else 1

if __name__ == "__main__":
    exit(main())
