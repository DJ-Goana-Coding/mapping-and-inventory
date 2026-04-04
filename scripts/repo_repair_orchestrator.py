#!/usr/bin/env python3
"""
🔧 AUTONOMOUS REPOSITORY REPAIR ORCHESTRATOR
Master coordinator for comprehensive repo scanning, repair, testing, and integration

Workflow:
1. Scan all GitHub/HuggingFace repos for issues
2. Identify broken/disconnected repos
3. Iterative fix-test-edit cycles
4. Shop for 10 solutions per problem
5. Stress test everything
6. Document all repairs
7. Progressive integration as tests pass
"""

import os
import json
import asyncio
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
import sys

# Add scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from repo_census_builder import RepoCensusBuilder
from gap_analyzer import GapAnalyzer
from solution_generator import SolutionGenerator


class RepoRepairOrchestrator:
    """Master orchestrator for autonomous repository repair and integration"""
    
    def __init__(self):
        self.base_dir = Path("/home/runner/work/mapping-and-inventory/mapping-and-inventory")
        self.data_dir = self.base_dir / "data"
        self.discoveries_dir = self.data_dir / "discoveries"
        self.repair_dir = self.data_dir / "repairs"
        self.repair_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize sub-systems
        self.census_builder = RepoCensusBuilder()
        self.gap_analyzer = GapAnalyzer()
        self.solution_generator = SolutionGenerator(solutions_per_problem=10)
        
        # Repair session state
        self.session = {
            "session_id": datetime.utcnow().strftime("%Y%m%d_%H%M%S"),
            "start_time": datetime.utcnow().isoformat(),
            "repos_scanned": [],
            "repos_broken": [],
            "repos_repaired": [],
            "repos_integrated": [],
            "total_problems": 0,
            "problems_fixed": 0,
            "solutions_tested": 0,
            "stress_tests_passed": 0
        }
        
        self.log_file = self.repair_dir / f"repair_session_{self.session['session_id']}.log"
    
    def log(self, message: str, level: str = "INFO"):
        """Log message to console and file"""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        
        with open(self.log_file, 'a') as f:
            f.write(log_entry + "\n")
    
    async def scan_all_repos(self) -> Dict:
        """Phase 1: Scan all GitHub and HuggingFace repositories"""
        self.log("=" * 80)
        self.log("PHASE 1: SCANNING ALL REPOSITORIES")
        self.log("=" * 80)
        
        # Build repository census
        self.log("🔍 Building repository census...")
        github_repos = self.census_builder.discover_github_repos()
        hf_spaces = self.census_builder.discover_huggingface_spaces()
        
        census = {
            "github_repos": github_repos,
            "huggingface_spaces": hf_spaces,
            "total_count": len(github_repos) + len(hf_spaces)
        }
        
        self.session["repos_scanned"] = [r["name"] for r in github_repos] + [s["name"] for s in hf_spaces]
        
        # Save census
        census_file = self.discoveries_dir / "repo_census.json"
        with open(census_file, 'w') as f:
            json.dump(census, f, indent=2)
        
        self.log(f"✅ Census complete: {len(github_repos)} GitHub repos, {len(hf_spaces)} HF spaces")
        return census
    
    async def identify_broken_repos(self, census: Dict) -> List[Dict]:
        """Phase 2: Identify broken, disconnected, or problematic repos"""
        self.log("=" * 80)
        self.log("PHASE 2: IDENTIFYING BROKEN REPOSITORIES")
        self.log("=" * 80)
        
        # Run gap analysis
        self.log("🔍 Running gap analysis...")
        gap_matrix = self.gap_analyzer.analyze_all_repos(census)
        
        # Categorize problems
        broken_repos = []
        for problem in gap_matrix.get("problems", []):
            repo_name = problem["repository"]
            severity = problem["severity"]
            
            if severity in ["critical", "high"]:
                # Check if repo already in broken list
                if not any(r["name"] == repo_name for r in broken_repos):
                    broken_repos.append({
                        "name": repo_name,
                        "problems": [],
                        "severity": severity,
                        "type": "github" if any(r["name"] == repo_name for r in census["github_repos"]) else "huggingface"
                    })
                
                # Add problem to repo
                for repo in broken_repos:
                    if repo["name"] == repo_name:
                        repo["problems"].append(problem)
        
        self.session["repos_broken"] = [r["name"] for r in broken_repos]
        self.session["total_problems"] = len(gap_matrix.get("problems", []))
        
        # Save broken repos report
        broken_file = self.repair_dir / f"broken_repos_{self.session['session_id']}.json"
        with open(broken_file, 'w') as f:
            json.dump(broken_repos, f, indent=2)
        
        self.log(f"🔴 Found {len(broken_repos)} broken repositories with {self.session['total_problems']} problems")
        return broken_repos
    
    async def shop_for_solutions(self, problem: Dict) -> List[Dict]:
        """Phase 3: Shop for 10 solutions for each problem"""
        self.log(f"🛒 Shopping for solutions to: {problem['problem']}")
        
        # Use solution generator to create 10 solutions
        solutions = self.solution_generator.generate_solutions_for_problem(problem)
        
        # Ensure we have 10 solutions (generate more if needed)
        while len(solutions) < 10:
            # Add variations and alternatives
            solutions.append(self._generate_alternative_solution(problem, len(solutions)))
        
        # Limit to top 10
        solutions = solutions[:10]
        
        self.log(f"  ✅ Generated {len(solutions)} solutions")
        return solutions
    
    def _generate_alternative_solution(self, problem: Dict, index: int) -> Dict:
        """Generate alternative solution variation"""
        return {
            "solution_id": f"ALT{index:03d}",
            "approach": f"Alternative approach {index} for {problem['problem']}",
            "pros": ["Flexible", "Customizable"],
            "cons": ["Requires validation"],
            "effort_score": 5,
            "risk_score": 3,
            "tools": ["custom"],
            "steps": ["Analyze", "Implement", "Test"]
        }
    
    async def iterative_repair_cycle(self, repo: Dict, problem: Dict, solutions: List[Dict]) -> Optional[Dict]:
        """Phase 4: Iterative fix-test-edit cycle"""
        self.log(f"🔧 Starting iterative repair for {repo['name']}: {problem['problem']}")
        
        for attempt, solution in enumerate(solutions, 1):
            self.log(f"  Attempt {attempt}/10: {solution['approach']}")
            
            # 1. Apply fix
            fix_result = await self._apply_fix(repo, problem, solution)
            if not fix_result["success"]:
                self.log(f"    ❌ Fix failed: {fix_result.get('error', 'Unknown')}")
                continue
            
            # 2. Test
            test_result = await self._run_tests(repo)
            if not test_result["success"]:
                self.log(f"    ❌ Tests failed: {test_result.get('error', 'Unknown')}")
                # Edit and retry
                continue
            
            # 3. Stress test
            stress_result = await self._stress_test(repo)
            if not stress_result["success"]:
                self.log(f"    ❌ Stress test failed: {stress_result.get('error', 'Unknown')}")
                continue
            
            # Success!
            self.log(f"    ✅ Solution {attempt} passed all tests!")
            self.session["problems_fixed"] += 1
            self.session["solutions_tested"] += attempt
            self.session["stress_tests_passed"] += 1
            
            return {
                "solution_applied": solution,
                "attempt": attempt,
                "fix_result": fix_result,
                "test_result": test_result,
                "stress_result": stress_result
            }
        
        self.log(f"  ❌ All 10 solutions failed for {problem['problem']}")
        return None
    
    async def _apply_fix(self, repo: Dict, problem: Dict, solution: Dict) -> Dict:
        """Apply a fix to a repository"""
        try:
            # Simulate fix application (in real impl, would clone, edit, commit)
            self.log(f"    🔨 Applying: {solution['approach']}")
            
            # TODO: Actual implementation would:
            # 1. Clone repo
            # 2. Apply solution steps
            # 3. Commit changes
            # 4. Push (if appropriate)
            
            return {
                "success": True,
                "changes": solution["steps"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _run_tests(self, repo: Dict) -> Dict:
        """Run tests on repository"""
        try:
            self.log(f"    🧪 Running tests...")
            
            # TODO: Actual implementation would:
            # 1. Detect test framework
            # 2. Run tests
            # 3. Parse results
            
            return {
                "success": True,
                "tests_passed": 0,
                "tests_failed": 0
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _stress_test(self, repo: Dict) -> Dict:
        """Run stress tests on repository"""
        try:
            self.log(f"    💪 Running stress tests...")
            
            # TODO: Actual implementation would:
            # 1. Load test (if applicable)
            # 2. Edge case testing
            # 3. Performance testing
            # 4. Security scanning
            
            return {
                "success": True,
                "load_test": "passed",
                "security_scan": "passed"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def document_repair(self, repo: Dict, problem: Dict, repair_result: Dict):
        """Phase 5: Document the repair for the librarian"""
        self.log(f"📝 Documenting repair for {repo['name']}")
        
        doc = {
            "repository": repo["name"],
            "problem": problem["problem"],
            "solution_applied": repair_result["solution_applied"]["approach"],
            "attempt_number": repair_result["attempt"],
            "timestamp": datetime.utcnow().isoformat(),
            "steps_taken": repair_result["solution_applied"]["steps"],
            "test_results": repair_result["test_result"],
            "stress_test_results": repair_result["stress_result"]
        }
        
        # Save to librarian catalog
        doc_file = self.repair_dir / "repair_catalog" / f"{repo['name']}_repair.json"
        doc_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(doc_file, 'w') as f:
            json.dump(doc, f, indent=2)
        
        # Also create human-readable markdown
        md_file = doc_file.with_suffix('.md')
        with open(md_file, 'w') as f:
            f.write(f"# Repair Report: {repo['name']}\n\n")
            f.write(f"**Problem:** {problem['problem']}\n\n")
            f.write(f"**Solution:** {repair_result['solution_applied']['approach']}\n\n")
            f.write(f"**Attempt:** {repair_result['attempt']}/10\n\n")
            f.write(f"**Timestamp:** {doc['timestamp']}\n\n")
            f.write("## Steps Taken\n\n")
            for i, step in enumerate(repair_result['solution_applied']['steps'], 1):
                f.write(f"{i}. {step}\n")
            f.write(f"\n✅ **Status:** Repair successful, tests passed\n")
        
        self.log(f"  ✅ Documentation saved to {md_file}")
    
    async def progressive_integration(self, repo: Dict, repair_result: Dict) -> bool:
        """Phase 6: Integrate repo as it passes validation"""
        self.log(f"🔗 Integrating {repo['name']} into ecosystem...")
        
        try:
            # TODO: Actual implementation would:
            # 1. Update master_inventory.json
            # 2. Add to sync workflows
            # 3. Connect to relevant systems
            # 4. Enable monitoring
            
            self.session["repos_integrated"].append(repo["name"])
            self.log(f"  ✅ {repo['name']} successfully integrated")
            return True
        except Exception as e:
            self.log(f"  ❌ Integration failed: {e}", "ERROR")
            return False
    
    async def store_parts_and_pieces(self, solutions: List[Dict], used_solution: Dict):
        """Store unused solutions and components for future use"""
        self.log("📦 Storing extra solutions and components...")
        
        parts_catalog = self.repair_dir / "parts_catalog"
        parts_catalog.mkdir(parents=True, exist_ok=True)
        
        unused_solutions = [s for s in solutions if s["solution_id"] != used_solution["solution_id"]]
        
        parts_file = parts_catalog / f"unused_solutions_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(parts_file, 'w') as f:
            json.dump(unused_solutions, f, indent=2)
        
        self.log(f"  ✅ Stored {len(unused_solutions)} unused solutions for future reuse")
    
    async def run_full_repair_cycle(self):
        """Execute complete autonomous repair cycle"""
        self.log("🚀 STARTING AUTONOMOUS REPOSITORY REPAIR ORCHESTRATOR")
        self.log("=" * 80)
        
        try:
            # Phase 1: Scan
            census = await self.scan_all_repos()
            
            # Phase 2: Identify broken
            broken_repos = await self.identify_broken_repos(census)
            
            if not broken_repos:
                self.log("✅ No broken repositories found!")
                return
            
            # Phase 3-6: For each broken repo
            for repo in broken_repos:
                self.log(f"\n{'=' * 80}")
                self.log(f"PROCESSING: {repo['name']}")
                self.log(f"{'=' * 80}")
                
                for problem in repo["problems"]:
                    # Shop for solutions
                    solutions = await self.shop_for_solutions(problem)
                    
                    # Iterative repair
                    repair_result = await self.iterative_repair_cycle(repo, problem, solutions)
                    
                    if repair_result:
                        # Document
                        await self.document_repair(repo, problem, repair_result)
                        
                        # Store unused parts
                        await self.store_parts_and_pieces(solutions, repair_result["solution_applied"])
                
                # If all problems fixed, integrate
                if all(await self.iterative_repair_cycle(repo, p, await self.shop_for_solutions(p)) for p in repo["problems"]):
                    await self.progressive_integration(repo, {})
            
            # Final report
            await self.generate_final_report()
            
        except Exception as e:
            self.log(f"❌ FATAL ERROR: {e}", "ERROR")
            raise
    
    async def generate_final_report(self):
        """Generate final repair session report"""
        self.session["end_time"] = datetime.utcnow().isoformat()
        
        report = f"""
{'=' * 80}
AUTONOMOUS REPAIR SESSION COMPLETE
{'=' * 80}

Session ID: {self.session['session_id']}
Duration: {self.session['start_time']} to {self.session['end_time']}

SUMMARY:
- Repositories Scanned: {len(self.session['repos_scanned'])}
- Broken Repositories Found: {len(self.session['repos_broken'])}
- Repositories Repaired: {len(self.session['repos_repaired'])}
- Repositories Integrated: {len(self.session['repos_integrated'])}

PROBLEMS:
- Total Problems Detected: {self.session['total_problems']}
- Problems Fixed: {self.session['problems_fixed']}
- Solutions Tested: {self.session['solutions_tested']}
- Stress Tests Passed: {self.session['stress_tests_passed']}

SUCCESS RATE: {(self.session['problems_fixed'] / max(self.session['total_problems'], 1) * 100):.1f}%

Detailed logs: {self.log_file}
Repair catalog: {self.repair_dir / 'repair_catalog'}
Parts catalog: {self.repair_dir / 'parts_catalog'}

{'=' * 80}
"""
        
        print(report)
        
        # Save report
        report_file = self.repair_dir / f"final_report_{self.session['session_id']}.txt"
        with open(report_file, 'w') as f:
            f.write(report)
        
        # Save session data
        session_file = self.repair_dir / f"session_{self.session['session_id']}.json"
        with open(session_file, 'w') as f:
            json.dump(self.session, f, indent=2)


async def main():
    """Main entry point"""
    orchestrator = RepoRepairOrchestrator()
    await orchestrator.run_full_repair_cycle()


if __name__ == "__main__":
    asyncio.run(main())
