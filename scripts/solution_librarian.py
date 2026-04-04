#!/usr/bin/env python3
"""
🏛️ CITADEL OMNI-PERFECTION: Solution Librarian
Phase 1.5 - Archive and preserve unused solutions for future reference

Maintains a searchable library of all solutions, including those not selected.
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import hashlib

class SolutionLibrarian:
    """Maintains solution knowledge base and archives"""
    
    def __init__(self):
        self.data_dir = Path("/home/runner/work/mapping-and-inventory/mapping-and-inventory/data")
        self.experiments_dir = self.data_dir / "experiments"
        self.libraries_dir = self.data_dir / "libraries"
        self.archive_dir = self.libraries_dir / "solution_archive"
        
        # Create archive structure
        self.archive_categories = {
            "dependency_alternatives": self.archive_dir / "dependency_alternatives",
            "architecture_patterns": self.archive_dir / "architecture_patterns",
            "security_fixes": self.archive_dir / "security_fixes",
            "performance_optimizations": self.archive_dir / "performance_optimizations",
            "testing_approaches": self.archive_dir / "testing_approaches",
            "documentation_methods": self.archive_dir / "documentation_methods",
            "automation_tools": self.archive_dir / "automation_tools",
            "build_systems": self.archive_dir / "build_systems"
        }
        
        for category_dir in self.archive_categories.values():
            category_dir.mkdir(parents=True, exist_ok=True)
        
        self.library_index = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_solutions": 0,
            "categories": {},
            "by_tool": {},
            "by_effort": {},
            "by_risk": {}
        }
    
    def categorize_solution(self, problem_category: str) -> str:
        """Map problem category to archive category"""
        mapping = {
            "missing_tests": "testing_approaches",
            "deprecated_dependencies": "dependency_alternatives",
            "missing_documentation": "documentation_methods",
            "missing_automation": "automation_tools",
            "architectural_inconsistencies": "architecture_patterns",
            "security_vulnerabilities": "security_fixes",
            "performance_bottlenecks": "performance_optimizations",
            "broken_builds": "build_systems"
        }
        return mapping.get(problem_category, "automation_tools")
    
    def archive_solution(self, solution: Dict, problem: Dict, selected: bool = False) -> Dict:
        """Archive a solution to the library"""
        # Determine archive category
        problem_category = problem.get("category", "unknown")
        archive_category = self.categorize_solution(problem_category)
        archive_path = self.archive_categories[archive_category]
        
        # Create solution document
        solution_doc = {
            "solution_id": solution["solution_id"],
            "problem_id": problem.get("problem_id", "unknown"),
            "problem_category": problem_category,
            "problem_description": problem.get("problem", ""),
            "approach": solution["approach"],
            "pros": solution.get("pros", []),
            "cons": solution.get("cons", []),
            "tools": solution.get("tools", []),
            "steps": solution.get("steps", []),
            "effort_score": solution.get("effort_score", 5),
            "risk_score": solution.get("risk_score", 5),
            "was_selected": selected,
            "archived_at": datetime.utcnow().isoformat(),
            "tags": self._generate_tags(solution, problem),
            "search_keywords": self._generate_keywords(solution, problem)
        }
        
        # Generate unique filename
        solution_hash = hashlib.md5(
            f"{solution['solution_id']}_{solution['approach']}".encode()
        ).hexdigest()[:8]
        
        filename = f"{problem.get('problem_id', 'unknown')}_{solution['solution_id']}_{solution_hash}.json"
        filepath = archive_path / filename
        
        # Save solution
        with open(filepath, 'w') as f:
            json.dump(solution_doc, f, indent=2)
        
        # Update index
        if archive_category not in self.library_index["categories"]:
            self.library_index["categories"][archive_category] = []
        
        self.library_index["categories"][archive_category].append({
            "file": str(filepath.relative_to(self.libraries_dir)),
            "solution_id": solution["solution_id"],
            "approach": solution["approach"][:80],
            "selected": selected
        })
        
        # Index by tools
        for tool in solution.get("tools", []):
            if tool not in self.library_index["by_tool"]:
                self.library_index["by_tool"][tool] = []
            self.library_index["by_tool"][tool].append(solution["solution_id"])
        
        # Index by effort
        effort = solution.get("effort_score", 5)
        effort_category = f"effort_{effort}"
        if effort_category not in self.library_index["by_effort"]:
            self.library_index["by_effort"][effort_category] = []
        self.library_index["by_effort"][effort_category].append(solution["solution_id"])
        
        # Index by risk
        risk = solution.get("risk_score", 5)
        risk_category = f"risk_{risk}"
        if risk_category not in self.library_index["by_risk"]:
            self.library_index["by_risk"][risk_category] = []
        self.library_index["by_risk"][risk_category].append(solution["solution_id"])
        
        self.library_index["total_solutions"] += 1
        
        return solution_doc
    
    def _generate_tags(self, solution: Dict, problem: Dict) -> List[str]:
        """Generate tags for solution"""
        tags = []
        
        # Add problem category
        tags.append(problem.get("category", "general"))
        
        # Add effort level
        effort = solution.get("effort_score", 5)
        if effort <= 3:
            tags.append("low-effort")
        elif effort <= 6:
            tags.append("medium-effort")
        else:
            tags.append("high-effort")
        
        # Add risk level
        risk = solution.get("risk_score", 5)
        if risk <= 3:
            tags.append("low-risk")
        elif risk <= 6:
            tags.append("medium-risk")
        else:
            tags.append("high-risk")
        
        # Add tools as tags
        for tool in solution.get("tools", []):
            tags.append(f"tool:{tool.lower()}")
        
        return tags
    
    def _generate_keywords(self, solution: Dict, problem: Dict) -> List[str]:
        """Generate search keywords"""
        keywords = set()
        
        # Extract words from approach
        approach_words = solution["approach"].lower().split()
        keywords.update(w for w in approach_words if len(w) > 3)
        
        # Extract from problem
        problem_words = problem.get("problem", "").lower().split()
        keywords.update(w for w in problem_words if len(w) > 3)
        
        # Add tools
        keywords.update(t.lower() for t in solution.get("tools", []))
        
        return sorted(list(keywords))
    
    def process_all_solutions(self) -> None:
        """Archive all solutions from catalogs and selections"""
        print("🏛️ CITADEL SOLUTION LIBRARIAN")
        print("=" * 60)
        print("📚 Archiving solutions to knowledge base...\n")
        
        # Load selected solutions
        selections_file = self.experiments_dir / "selected_solutions.json"
        selected_ids = set()
        
        if selections_file.exists():
            with open(selections_file, 'r') as f:
                selections = json.load(f)
            selected_ids = {s["selected_solution_id"] for s in selections.get("selected_solutions", [])}
            print(f"✅ Loaded {len(selected_ids)} selected solutions\n")
        
        # Find all solution catalogs
        catalog_dir = self.experiments_dir / "solution_catalog"
        catalog_files = list(catalog_dir.glob("P*.json"))
        
        if not catalog_files:
            print("⚠️  No solution catalogs found.")
            return
        
        print(f"📁 Found {len(catalog_files)} problem catalogs\n")
        
        archived_count = 0
        selected_count = 0
        
        for catalog_file in sorted(catalog_files):
            try:
                with open(catalog_file, 'r') as f:
                    catalog = json.load(f)
                
                problem = catalog.get("problem", {})
                solutions = catalog.get("solutions", [])
                
                problem_id = problem.get("problem_id", catalog_file.stem.split('_')[0])
                
                print(f"📦 Archiving {len(solutions)} solutions for {problem_id}...")
                
                for solution in solutions:
                    is_selected = solution["solution_id"] in selected_ids
                    
                    self.archive_solution(solution, problem, selected=is_selected)
                    archived_count += 1
                    
                    if is_selected:
                        selected_count += 1
                
                print(f"   ✅ Archived to library\n")
            
            except Exception as e:
                print(f"   ❌ Error: {e}\n")
        
        # Save library index
        index_file = self.libraries_dir / "SOLUTION_LIBRARY_INDEX.json"
        with open(index_file, 'w') as f:
            json.dump(self.library_index, f, indent=2)
        
        # Generate README
        self._generate_readme()
        
        # Print summary
        print("=" * 60)
        print("📊 ARCHIVAL SUMMARY")
        print("=" * 60)
        print(f"Total Solutions Archived: {archived_count}")
        print(f"Selected Solutions: {selected_count}")
        print(f"Alternative Solutions: {archived_count - selected_count}")
        print(f"\nArchive Categories:")
        for category, solutions in self.library_index["categories"].items():
            print(f"  {category}: {len(solutions)} solutions")
        print(f"\n💾 Library index: {index_file}")
    
    def _generate_readme(self) -> None:
        """Generate README for solution library"""
        readme_content = f"""# 📚 CITADEL SOLUTION LIBRARY

**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}  
**Total Solutions:** {self.library_index['total_solutions']}

## 🎯 Purpose

This library archives ALL solutions generated during the Omni-Perfection Protocol, including both selected and alternative approaches. Every solution is preserved for:

- Future reference when facing similar problems
- Learning from alternative approaches
- Understanding trade-offs between different solutions
- Quick lookup when tools or approaches are needed

## 📁 Archive Structure

```
solution_archive/
├── dependency_alternatives/     # Package & dependency solutions
├── architecture_patterns/       # Code structure & design patterns
├── security_fixes/             # Security vulnerability fixes
├── performance_optimizations/   # Performance improvement approaches
├── testing_approaches/         # Testing frameworks & strategies
├── documentation_methods/      # Documentation generation tools
├── automation_tools/           # Automation & CI/CD solutions
└── build_systems/              # Build & compilation approaches
```

## 🔍 Search by Tool

Top tools in library:

"""
        # Add top tools
        tool_counts = {tool: len(ids) for tool, ids in self.library_index["by_tool"].items()}
        for tool, count in sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)[:15]:
            readme_content += f"- **{tool}**: {count} solutions\n"
        
        readme_content += f"""

## 📊 Solutions by Category

"""
        for category, solutions in self.library_index["categories"].items():
            selected = sum(1 for s in solutions if s.get("selected", False))
            readme_content += f"- **{category.replace('_', ' ').title()}**: {len(solutions)} solutions ({selected} selected)\n"
        
        readme_content += f"""

## 🎓 Usage

### Search by Tool
Check `SOLUTION_LIBRARY_INDEX.json` → `by_tool` section

### Search by Effort/Risk
Check `SOLUTION_LIBRARY_INDEX.json` → `by_effort` or `by_risk` sections

### Browse by Category
Navigate to the appropriate category directory

### View Solution
Open any `.json` file to see complete solution details including:
- Problem it solves
- Approach description
- Pros and cons
- Required tools
- Implementation steps
- Effort and risk scores
- Tags and keywords

## 🔄 Forever Learning

This library grows with every audit cycle. Solutions that weren't selected today might be perfect for tomorrow's challenges.

**Wisdom is preserved. Knowledge compounds. The Citadel remembers.**
"""
        
        readme_file = self.libraries_dir / "SOLUTION_LIBRARY_README.md"
        with open(readme_file, 'w') as f:
            f.write(readme_content)
        
        print(f"📄 Generated README: {readme_file}")

def main():
    """Main execution"""
    librarian = SolutionLibrarian()
    librarian.process_all_solutions()

if __name__ == "__main__":
    main()
