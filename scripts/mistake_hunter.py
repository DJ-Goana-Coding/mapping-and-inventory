#!/usr/bin/env python3
"""
🏛️ CITADEL OMNI-PERFECTION: Mistake Hunter
Phase 1.3 - Deep error analysis and code quality scanner

Hunts for bugs, security issues, code smells, and technical debt across all repositories.
"""

import os
import json
import ast
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set
import sys

class MistakeHunter:
    """Deep code analysis and error detection"""
    
    def __init__(self):
        self.repo_root = Path("/home/runner/work/mapping-and-inventory/mapping-and-inventory")
        self.data_dir = self.repo_root / "data"
        self.monitoring_dir = self.data_dir / "monitoring"
        self.monitoring_dir.mkdir(parents=True, exist_ok=True)
        
        self.mistakes = {
            "timestamp": datetime.utcnow().isoformat(),
            "categories": {
                "syntax_errors": [],
                "import_errors": [],
                "undefined_variables": [],
                "security_issues": [],
                "code_smells": [],
                "deprecated_usage": [],
                "hardcoded_secrets": [],
                "performance_issues": []
            },
            "summary": {
                "total_files_scanned": 0,
                "total_mistakes": 0,
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            }
        }
        
        # Patterns for common security issues
        self.security_patterns = {
            "hardcoded_password": re.compile(r"password\s*=\s*['\"][^'\"]+['\"]", re.IGNORECASE),
            "hardcoded_token": re.compile(r"(token|api_key|secret)\s*=\s*['\"][a-zA-Z0-9]{20,}['\"]", re.IGNORECASE),
            "sql_injection": re.compile(r"execute\(['\"].*%s.*['\"]\s*%", re.IGNORECASE),
            "eval_usage": re.compile(r"\beval\s*\("),
            "exec_usage": re.compile(r"\bexec\s*\("),
            "pickle_usage": re.compile(r"pickle\.loads?\("),
        }
        
        # Patterns for code smells
        self.code_smell_patterns = {
            "long_function": 50,  # lines
            "many_arguments": 6,  # parameters
            "deep_nesting": 4,  # levels
            "magic_numbers": re.compile(r"\b[0-9]{4,}\b"),  # 4+ digit numbers
        }
        
        # Deprecated package patterns
        self.deprecated_packages = {
            "google-genai": "google-generativeai",
            "pkg_resources": "importlib.resources",
            "imp": "importlib",
        }
    
    def scan_python_file(self, file_path: Path) -> List[Dict]:
        """Scan a Python file for mistakes"""
        mistakes = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Check for syntax errors
            try:
                tree = ast.parse(content)
                
                # Analyze AST for various issues
                mistakes.extend(self._analyze_ast(tree, file_path, lines))
            
            except SyntaxError as e:
                mistakes.append({
                    "file": str(file_path.relative_to(self.repo_root)),
                    "line": e.lineno,
                    "type": "syntax_error",
                    "severity": "critical",
                    "message": f"Syntax error: {e.msg}",
                    "context": lines[e.lineno - 1] if e.lineno and e.lineno <= len(lines) else ""
                })
            
            # Security pattern scanning
            mistakes.extend(self._scan_security_patterns(content, file_path, lines))
            
            # Check for deprecated packages
            mistakes.extend(self._scan_deprecated_imports(content, file_path, lines))
            
        except Exception as e:
            mistakes.append({
                "file": str(file_path.relative_to(self.repo_root)),
                "line": 0,
                "type": "scan_error",
                "severity": "low",
                "message": f"Failed to scan file: {str(e)}"
            })
        
        return mistakes
    
    def _analyze_ast(self, tree: ast.AST, file_path: Path, lines: List[str]) -> List[Dict]:
        """Analyze AST for code quality issues"""
        mistakes = []
        
        for node in ast.walk(tree):
            # Check for undefined variables (simplified)
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                # This is a basic check - full analysis would require scope tracking
                pass
            
            # Check function definitions
            if isinstance(node, ast.FunctionDef):
                # Check function length
                func_lines = 0
                if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
                    func_lines = node.end_lineno - node.lineno
                    
                    if func_lines > self.code_smell_patterns["long_function"]:
                        mistakes.append({
                            "file": str(file_path.relative_to(self.repo_root)),
                            "line": node.lineno,
                            "type": "code_smell",
                            "severity": "medium",
                            "message": f"Function '{node.name}' is too long ({func_lines} lines)",
                            "suggestion": "Consider breaking into smaller functions"
                        })
                
                # Check argument count
                arg_count = len(node.args.args)
                if arg_count > self.code_smell_patterns["many_arguments"]:
                    mistakes.append({
                        "file": str(file_path.relative_to(self.repo_root)),
                        "line": node.lineno,
                        "type": "code_smell",
                        "severity": "medium",
                        "message": f"Function '{node.name}' has too many arguments ({arg_count})",
                        "suggestion": "Consider using a config object or kwargs"
                    })
            
            # Check for dangerous operations
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['eval', 'exec']:
                        mistakes.append({
                            "file": str(file_path.relative_to(self.repo_root)),
                            "line": node.lineno,
                            "type": "security_issue",
                            "severity": "high",
                            "message": f"Dangerous use of {node.func.id}()",
                            "suggestion": "Avoid eval/exec - use safer alternatives"
                        })
        
        return mistakes
    
    def _scan_security_patterns(self, content: str, file_path: Path, lines: List[str]) -> List[Dict]:
        """Scan for security pattern matches"""
        mistakes = []
        
        for line_num, line in enumerate(lines, 1):
            # Skip comments and docstrings
            stripped = line.strip()
            if stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
                continue
            
            # Check each security pattern
            for pattern_name, pattern in self.security_patterns.items():
                if pattern.search(line):
                    # Don't flag test files or templates
                    if "test" in file_path.name.lower() or "template" in file_path.name.lower():
                        continue
                    
                    # Don't flag example/placeholder values
                    if any(placeholder in line.lower() for placeholder in 
                           ["example", "placeholder", "your_", "xxx", "..."]):
                        continue
                    
                    mistakes.append({
                        "file": str(file_path.relative_to(self.repo_root)),
                        "line": line_num,
                        "type": "security_issue",
                        "severity": "high" if "secret" in pattern_name else "medium",
                        "message": f"Potential {pattern_name.replace('_', ' ')}",
                        "context": line.strip()[:100],
                        "suggestion": "Use environment variables or secure vaults"
                    })
        
        return mistakes
    
    def _scan_deprecated_imports(self, content: str, file_path: Path, lines: List[str]) -> List[Dict]:
        """Scan for deprecated package usage"""
        mistakes = []
        
        for line_num, line in enumerate(lines, 1):
            for deprecated, replacement in self.deprecated_packages.items():
                if f"import {deprecated}" in line or f"from {deprecated}" in line:
                    mistakes.append({
                        "file": str(file_path.relative_to(self.repo_root)),
                        "line": line_num,
                        "type": "deprecated_usage",
                        "severity": "medium",
                        "message": f"Deprecated package: {deprecated}",
                        "context": line.strip(),
                        "suggestion": f"Use {replacement} instead"
                    })
        
        return mistakes
    
    def scan_repository(self) -> None:
        """Scan entire repository for mistakes"""
        print("🏛️ CITADEL MISTAKE HUNTER")
        print("=" * 60)
        print("🔍 Scanning for bugs, security issues, and code smells...\n")
        
        # Find all Python files
        python_files = list(self.repo_root.glob("**/*.py"))
        
        # Exclude certain directories
        exclude_dirs = {'.git', 'venv', '__pycache__', '.pytest_cache', 'node_modules'}
        python_files = [
            f for f in python_files 
            if not any(excluded in f.parts for excluded in exclude_dirs)
        ]
        
        print(f"📊 Found {len(python_files)} Python files to scan\n")
        
        for i, file_path in enumerate(python_files, 1):
            if i % 20 == 0:
                print(f"  Progress: {i}/{len(python_files)} files scanned...")
            
            file_mistakes = self.scan_python_file(file_path)
            
            # Categorize mistakes
            for mistake in file_mistakes:
                mistake_type = mistake.get("type", "unknown")
                
                if mistake_type in self.mistakes["categories"]:
                    self.mistakes["categories"][mistake_type].append(mistake)
                
                # Update severity counts
                severity = mistake.get("severity", "low")
                if severity in self.mistakes["summary"]:
                    self.mistakes["summary"][severity] += 1
                
                self.mistakes["summary"]["total_mistakes"] += 1
            
            self.mistakes["summary"]["total_files_scanned"] += 1
        
        # Additional checks using external tools if available
        self._run_additional_checks()
        
        # Save results
        results_file = self.monitoring_dir / "mistake_inventory.json"
        with open(results_file, 'w') as f:
            json.dump(self.mistakes, f, indent=2)
        
        # Generate report
        self._generate_report(results_file)
    
    def _run_additional_checks(self) -> None:
        """Run additional checks with external tools"""
        print("\n🔧 Running additional code quality checks...")
        
        # Try running pylint if available
        try:
            result = subprocess.run(
                ["python", "-m", "pylint", "--version"],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                print("  ✅ Pylint available (not running full scan in this version)")
        except:
            print("  ⏭️  Pylint not available")
        
        # Try running bandit if available
        try:
            result = subprocess.run(
                ["python", "-m", "bandit", "--version"],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                print("  ✅ Bandit available (not running full scan in this version)")
        except:
            print("  ⏭️  Bandit not available")
    
    def _generate_report(self, results_file: Path) -> None:
        """Generate human-readable report"""
        print("\n" + "=" * 60)
        print("📊 MISTAKE HUNTING SUMMARY")
        print("=" * 60)
        print(f"Files Scanned: {self.mistakes['summary']['total_files_scanned']}")
        print(f"Total Issues Found: {self.mistakes['summary']['total_mistakes']}\n")
        
        print("Severity Breakdown:")
        print(f"  🔴 Critical: {self.mistakes['summary']['critical']}")
        print(f"  🟠 High: {self.mistakes['summary']['high']}")
        print(f"  🟡 Medium: {self.mistakes['summary']['medium']}")
        print(f"  🟢 Low: {self.mistakes['summary']['low']}\n")
        
        print("Category Breakdown:")
        for category, issues in self.mistakes["categories"].items():
            if issues:
                print(f"  {category.replace('_', ' ').title()}: {len(issues)}")
        
        print(f"\n💾 Detailed results saved: {results_file}")
        
        # Show top 5 critical/high issues
        critical_high = []
        for category, issues in self.mistakes["categories"].items():
            for issue in issues:
                if issue.get("severity") in ["critical", "high"]:
                    critical_high.append(issue)
        
        if critical_high:
            print("\n🚨 Top Priority Issues:")
            for issue in critical_high[:5]:
                print(f"  [{issue.get('severity', 'unknown').upper()}] {issue.get('file', 'unknown')}:{issue.get('line', 0)}")
                print(f"     {issue.get('message', 'No message')}")

def main():
    """Main execution"""
    hunter = MistakeHunter()
    hunter.scan_repository()

if __name__ == "__main__":
    main()
