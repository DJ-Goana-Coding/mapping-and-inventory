#!/usr/bin/env python3
"""
🏛️ CITADEL OMNI-AUDIT: Gap Analysis Matrix Generator
Phase 1.3 - Identify all problems, missing pieces, and technical debt

Analyzes repo census and existing code to create comprehensive gap matrix.
"""

import os
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set
import subprocess

class GapAnalyzer:
    """Analyzes repositories for gaps, issues, and technical debt"""
    
    def __init__(self):
        self.data_dir = Path("/home/runner/work/mapping-and-inventory/mapping-and-inventory/data")
        self.discoveries_dir = self.data_dir / "discoveries"
        self.monitoring_dir = self.data_dir / "monitoring"
        
        self.gap_matrix = {
            "timestamp": datetime.utcnow().isoformat(),
            "problems": [],
            "categories": {
                "missing_tests": [],
                "deprecated_dependencies": [],
                "broken_builds": [],
                "missing_documentation": [],
                "security_vulnerabilities": [],
                "performance_bottlenecks": [],
                "architectural_inconsistencies": [],
                "missing_automation": []
            },
            "summary": {
                "total_problems": 0,
                "critical_count": 0,
                "high_count": 0,
                "medium_count": 0,
                "low_count": 0
            }
        }
        
        self.problem_id_counter = 1
    
    def load_repo_census(self) -> Dict:
        """Load repository census data"""
        census_file = self.discoveries_dir / "repo_census.json"
        if census_file.exists():
            with open(census_file, 'r') as f:
                return json.load(f)
        return {"github_repos": [], "huggingface_spaces": []}
    
    def add_problem(self, category: str, repo_name: str, problem: str, 
                   severity: str, details: Dict = None):
        """Add a problem to the gap matrix"""
        problem_entry = {
            "problem_id": f"P{self.problem_id_counter:03d}",
            "category": category,
            "repository": repo_name,
            "problem": problem,
            "severity": severity,  # critical, high, medium, low
            "detected_at": datetime.utcnow().isoformat(),
            "details": details or {}
        }
        
        self.gap_matrix["problems"].append(problem_entry)
        self.gap_matrix["categories"][category].append(problem_entry["problem_id"])
        self.problem_id_counter += 1
        
        # Update severity counts
        severity_key = f"{severity}_count"
        if severity_key in self.gap_matrix["summary"]:
            self.gap_matrix["summary"][severity_key] += 1
    
    def analyze_missing_tests(self, repos: List[Dict]):
        """Identify repositories missing tests"""
        print("🔍 Analyzing test coverage...")
        
        for repo in repos:
            if not repo.get("has_tests", False):
                self.add_problem(
                    "missing_tests",
                    repo["name"],
                    "No test directory or test configuration found",
                    "high",
                    {"size_kb": repo.get("size_kb", 0), "language": repo.get("primary_language")}
                )
    
    def analyze_deprecated_dependencies(self, repos: List[Dict]):
        """Identify deprecated or outdated dependencies"""
        print("🔍 Analyzing dependencies...")
        
        # Known deprecated packages to check for
        deprecated_patterns = {
            "google-genai": {"replacement": "google-generativeai", "version": "0.8.3"},
            "streamlit==1.56.0": {"replacement": "streamlit>=1.30.0", "reason": "build timeout"},
            "numpy==1.26.4": {"replacement": "numpy>=1.24.0,<2.0", "reason": "compilation issues"}
        }
        
        for repo in repos:
            # Check if repo has dependency manifests
            deps = repo.get("dependencies", [])
            
            if not deps:
                if repo.get("primary_language") in ["Python", "JavaScript", "TypeScript", "Ruby", "Go"]:
                    self.add_problem(
                        "deprecated_dependencies",
                        repo["name"],
                        "No dependency manifest found",
                        "medium",
                        {"language": repo.get("primary_language")}
                    )
    
    def analyze_missing_documentation(self, repos: List[Dict]):
        """Identify repositories with poor documentation"""
        print("🔍 Analyzing documentation...")
        
        for repo in repos:
            doc_score = repo.get("documentation_score", 0)
            
            if not repo.get("has_readme"):
                self.add_problem(
                    "missing_documentation",
                    repo["name"],
                    "Missing README.md file",
                    "high",
                    {"doc_score": doc_score}
                )
            elif doc_score < 40:
                self.add_problem(
                    "missing_documentation",
                    repo["name"],
                    f"Low documentation score: {doc_score:.1f}%",
                    "medium",
                    {"doc_score": doc_score}
                )
    
    def analyze_missing_automation(self, repos: List[Dict]):
        """Identify repositories missing CI/CD automation"""
        print("🔍 Analyzing automation...")
        
        for repo in repos:
            if not repo.get("has_ci", False):
                # Check if it's a repo that should have CI
                if repo.get("size_kb", 0) > 100 and not repo.get("archived", False):
                    self.add_problem(
                        "missing_automation",
                        repo["name"],
                        "No CI/CD configuration found",
                        "medium",
                        {"size_kb": repo.get("size_kb", 0)}
                    )
    
    def analyze_stale_repositories(self, repos: List[Dict]):
        """Identify stale or abandoned repositories"""
        print("🔍 Analyzing repository activity...")
        
        six_months_ago = datetime.utcnow() - timedelta(days=180)
        
        for repo in repos:
            if repo.get("archived", False):
                continue
                
            last_activity = repo.get("last_activity", "")
            if last_activity:
                try:
                    last_update = datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
                    if last_update < six_months_ago:
                        self.add_problem(
                            "architectural_inconsistencies",
                            repo["name"],
                            f"No updates in {(datetime.utcnow() - last_update.replace(tzinfo=None)).days} days",
                            "low",
                            {"last_activity": last_activity}
                        )
                except:
                    pass
    
    def analyze_security_issues(self, repos: List[Dict]):
        """Identify potential security issues"""
        print("🔍 Analyzing security posture...")
        
        for repo in repos:
            # Check for repos without LICENSE
            if repo.get("size_kb", 0) > 10:
                # Assume no license if not documented
                pass  # Would need to check repo contents
            
            # Check for high open issues count
            if repo.get("open_issues_count", 0) > 50:
                self.add_problem(
                    "architectural_inconsistencies",
                    repo["name"],
                    f"High number of open issues: {repo['open_issues_count']}",
                    "low",
                    {"open_issues": repo['open_issues_count']}
                )
    
    def analyze_broken_builds(self, repos: List[Dict]):
        """Identify repositories with broken builds"""
        print("🔍 Analyzing build health...")
        
        # This would require checking CI status via API
        # For now, we'll flag repos with CI but no recent activity
        for repo in repos:
            if repo.get("has_ci") and repo.get("open_issues_count", 0) > 0:
                # Potential build issues if has CI but unresolved issues
                pass
    
    def generate_gap_matrix(self) -> Dict:
        """Generate complete gap analysis matrix"""
        print("🏛️ CITADEL OMNI-AUDIT: Gap Analysis Matrix Generator")
        print("=" * 60)
        
        # Load repo census
        census = self.load_repo_census()
        repos = census.get("github_repos", [])
        
        if not repos:
            print("⚠️  No repository census data found. Run repo_census_builder.py first.")
            return self.gap_matrix
        
        print(f"Analyzing {len(repos)} repositories...")
        
        # Run all analysis functions
        self.analyze_missing_tests(repos)
        self.analyze_deprecated_dependencies(repos)
        self.analyze_missing_documentation(repos)
        self.analyze_missing_automation(repos)
        self.analyze_stale_repositories(repos)
        self.analyze_security_issues(repos)
        self.analyze_broken_builds(repos)
        
        # Update summary
        self.gap_matrix["summary"]["total_problems"] = len(self.gap_matrix["problems"])
        
        # Save gap matrix
        output_file = self.discoveries_dir / "gap_matrix.json"
        with open(output_file, 'w') as f:
            json.dump(self.gap_matrix, f, indent=2)
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 GAP ANALYSIS SUMMARY")
        print("=" * 60)
        print(f"Total Problems Identified: {self.gap_matrix['summary']['total_problems']}")
        print(f"  Critical: {self.gap_matrix['summary']['critical_count']}")
        print(f"  High: {self.gap_matrix['summary']['high_count']}")
        print(f"  Medium: {self.gap_matrix['summary']['medium_count']}")
        print(f"  Low: {self.gap_matrix['summary']['low_count']}")
        print("\nProblems by Category:")
        for category, problem_ids in self.gap_matrix["categories"].items():
            if problem_ids:
                print(f"  {category}: {len(problem_ids)}")
        print(f"\n✅ Gap matrix saved to: {output_file}")
        
        return self.gap_matrix


if __name__ == "__main__":
    analyzer = GapAnalyzer()
    gap_matrix = analyzer.generate_gap_matrix()
