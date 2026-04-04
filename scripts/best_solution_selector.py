#!/usr/bin/env python3
"""
🏛️ CITADEL OMNI-PERFECTION: Best Solution Selector
Phase 1.4 - Automated ranking and selection of best solutions

Analyzes validation results and selects optimal solutions based on multiple criteria.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import sys

class BestSolutionSelector:
    """Selects best solutions using multi-criteria decision making"""
    
    def __init__(self):
        self.data_dir = Path("/home/runner/work/mapping-and-inventory/mapping-and-inventory/data")
        self.validation_dir = self.data_dir / "experiments" / "validation_results"
        self.experiments_dir = self.data_dir / "experiments"
        
        # Weight factors for ranking (total = 1.0)
        self.weights = {
            "validation_status": 0.30,  # Passing validation is critical
            "effort_score": 0.25,       # Lower effort preferred
            "risk_score": 0.25,         # Lower risk preferred
            "tool_availability": 0.10,  # Tools already available
            "community_support": 0.10   # Popular/well-supported tools
        }
        
        self.selections = {
            "timestamp": datetime.utcnow().isoformat(),
            "selected_solutions": [],
            "summary": {
                "total_problems": 0,
                "solutions_selected": 0,
                "avg_confidence": 0.0
            }
        }
    
    def calculate_solution_score(self, solution: Dict, validation: Dict = None) -> float:
        """Calculate weighted score for a solution"""
        score = 0.0
        
        # Validation status score (0-10)
        if validation:
            validation_score = 0
            if validation.get("status") == "passed":
                validation_score = 10
            elif validation.get("status") == "warning":
                validation_score = 6
            elif validation.get("status") == "skipped":
                validation_score = 5
            else:  # failed
                validation_score = 2
            
            score += (validation_score / 10) * self.weights["validation_status"]
        else:
            # No validation data, use default
            score += 0.5 * self.weights["validation_status"]
        
        # Effort score (1-10, lower is better, so invert)
        effort = solution.get("effort_score", 5)
        effort_normalized = (11 - effort) / 10  # Invert scale
        score += effort_normalized * self.weights["effort_score"]
        
        # Risk score (1-10, lower is better, so invert)
        risk = solution.get("risk_score", 5)
        risk_normalized = (11 - risk) / 10  # Invert scale
        score += risk_normalized * self.weights["risk_score"]
        
        # Tool availability (assume 0.7 if tools listed, 0.5 otherwise)
        tools = solution.get("tools", [])
        tool_score = 0.7 if tools else 0.5
        score += tool_score * self.weights["tool_availability"]
        
        # Community support (based on tool popularity heuristics)
        community_score = self._assess_community_support(solution)
        score += community_score * self.weights["community_support"]
        
        return round(score, 3)
    
    def _assess_community_support(self, solution: Dict) -> float:
        """Assess community support based on tools and approach"""
        popular_tools = {
            "pytest", "docker", "kubernetes", "github", "aws", "gcp",
            "prometheus", "grafana", "terraform", "ansible", "jenkins",
            "unittest", "mypy", "black", "flake8", "pylint", "bandit"
        }
        
        tools = [t.lower() for t in solution.get("tools", [])]
        approach = solution.get("approach", "").lower()
        
        # Check if using popular tools
        popular_count = sum(1 for tool in tools if any(pop in tool for pop in popular_tools))
        
        # Check if approach mentions popular technologies
        approach_popular = sum(1 for pop in popular_tools if pop in approach)
        
        # Normalize to 0-1 scale
        total_mentions = popular_count + approach_popular
        return min(1.0, total_mentions / 3)  # Cap at 1.0
    
    def select_best_solution(self, problem_id: str, solutions: List[Dict], 
                            validations: List[Dict] = None) -> Dict:
        """Select best solution for a problem"""
        if not solutions:
            return None
        
        # Create validation lookup
        validation_map = {}
        if validations:
            for val in validations:
                validation_map[val.get("solution_id")] = val
        
        # Score all solutions
        scored_solutions = []
        for solution in solutions:
            solution_id = solution.get("solution_id")
            validation = validation_map.get(solution_id)
            
            score = self.calculate_solution_score(solution, validation)
            
            scored_solutions.append({
                "solution": solution,
                "validation": validation,
                "score": score
            })
        
        # Sort by score descending
        scored_solutions.sort(key=lambda x: x["score"], reverse=True)
        
        # Select top solution
        best = scored_solutions[0]
        
        selection = {
            "problem_id": problem_id,
            "selected_solution_id": best["solution"]["solution_id"],
            "approach": best["solution"]["approach"],
            "score": best["score"],
            "confidence": self._calculate_confidence(best["score"], scored_solutions),
            "reasoning": self._generate_reasoning(best, scored_solutions),
            "tools": best["solution"].get("tools", []),
            "steps": best["solution"].get("steps", []),
            "alternatives": [
                {
                    "solution_id": s["solution"]["solution_id"],
                    "approach": s["solution"]["approach"],
                    "score": s["score"]
                }
                for s in scored_solutions[1:4]  # Top 3 alternatives
            ]
        }
        
        return selection
    
    def _calculate_confidence(self, best_score: float, all_scored: List[Dict]) -> float:
        """Calculate confidence in selection based on score separation"""
        if len(all_scored) < 2:
            return 1.0
        
        second_best_score = all_scored[1]["score"]
        
        # Confidence based on gap between best and second-best
        gap = best_score - second_best_score
        
        # Higher gap = higher confidence
        confidence = min(1.0, 0.5 + (gap * 2))
        
        return round(confidence, 2)
    
    def _generate_reasoning(self, best: Dict, all_scored: List[Dict]) -> str:
        """Generate human-readable reasoning for selection"""
        reasons = []
        
        solution = best["solution"]
        validation = best["validation"]
        
        # Validation status
        if validation:
            if validation.get("status") == "passed":
                reasons.append("Passed validation tests")
            elif validation.get("status") == "warning":
                reasons.append("Passed with warnings")
        
        # Effort
        effort = solution.get("effort_score", 5)
        if effort <= 3:
            reasons.append("Low implementation effort")
        elif effort >= 7:
            reasons.append("Requires significant effort but worth it")
        
        # Risk
        risk = solution.get("risk_score", 5)
        if risk <= 3:
            reasons.append("Low risk approach")
        elif risk >= 7:
            reasons.append("Higher risk but validated")
        
        # Tools
        tools = solution.get("tools", [])
        if tools:
            reasons.append(f"Uses {len(tools)} well-supported tool(s)")
        
        # Score comparison
        if len(all_scored) >= 2:
            gap = best["score"] - all_scored[1]["score"]
            if gap > 0.15:
                reasons.append("Significantly outperforms alternatives")
            elif gap < 0.05:
                reasons.append("Close competition with alternatives")
        
        return "; ".join(reasons) if reasons else "Best available option"
    
    def process_all_problems(self) -> None:
        """Process all validated problems and select best solutions"""
        print("🏛️ CITADEL BEST SOLUTION SELECTOR")
        print("=" * 60)
        print("🎯 Analyzing validated solutions and selecting optimal approaches...\n")
        
        # Find all validation results
        validation_files = list(self.validation_dir.glob("P*_validation.json"))
        
        if not validation_files:
            print("⚠️  No validation results found. Run experimental_validator.py first.")
            return
        
        print(f"📊 Found {len(validation_files)} validated problems\n")
        
        for val_file in sorted(validation_files):
            try:
                with open(val_file, 'r') as f:
                    validation_data = json.load(f)
                
                problem_id = validation_data.get("problem_id")
                problem = validation_data.get("problem", {})
                
                # Load solution catalog
                catalog_dir = self.experiments_dir / "solution_catalog"
                catalog_files = list(catalog_dir.glob(f"{problem_id}_*.json"))
                
                if not catalog_files:
                    print(f"  ⚠️  No solution catalog for {problem_id}")
                    continue
                
                with open(catalog_files[0], 'r') as f:
                    catalog = json.load(f)
                
                solutions = catalog.get("solutions", [])
                validations = validation_data.get("validated_solutions", [])
                
                print(f"🔍 Problem {problem_id}: {problem.get('problem', 'Unknown')[:60]}")
                
                # Select best solution
                selection = self.select_best_solution(problem_id, solutions, validations)
                
                if selection:
                    self.selections["selected_solutions"].append(selection)
                    self.selections["summary"]["solutions_selected"] += 1
                    
                    print(f"  ✅ Selected: {selection['approach'][:70]}")
                    print(f"     Score: {selection['score']:.3f} | Confidence: {selection['confidence']:.0%}")
                    print(f"     Tools: {', '.join(selection['tools'][:3])}")
                    print(f"     Reasoning: {selection['reasoning']}\n")
                
                self.selections["summary"]["total_problems"] += 1
            
            except Exception as e:
                print(f"  ❌ Error processing {val_file.name}: {e}\n")
        
        # Calculate average confidence
        if self.selections["selected_solutions"]:
            avg_conf = sum(s["confidence"] for s in self.selections["selected_solutions"]) / len(self.selections["selected_solutions"])
            self.selections["summary"]["avg_confidence"] = round(avg_conf, 2)
        
        # Save selections
        selections_file = self.experiments_dir / "selected_solutions.json"
        with open(selections_file, 'w') as f:
            json.dump(self.selections, f, indent=2)
        
        # Print summary
        print("=" * 60)
        print("📊 SOLUTION SELECTION SUMMARY")
        print("=" * 60)
        print(f"Problems Analyzed: {self.selections['summary']['total_problems']}")
        print(f"Solutions Selected: {self.selections['summary']['solutions_selected']}")
        print(f"Average Confidence: {self.selections['summary']['avg_confidence']:.0%}")
        print(f"\n💾 Selections saved: {selections_file}")

def main():
    """Main execution"""
    selector = BestSolutionSelector()
    selector.process_all_problems()

if __name__ == "__main__":
    main()
