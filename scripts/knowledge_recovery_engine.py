#!/usr/bin/env python3
"""
🏛️ CITADEL OMNI-PERFECTION: Knowledge Recovery Engine
Phase 1.7 - Mine git history for lost documentation and buried knowledge

Recovers deleted files, old documentation, and hidden wisdom from commit history.
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set
import re

class KnowledgeRecoveryEngine:
    """Mines git history for lost knowledge and documentation"""
    
    def __init__(self):
        self.repo_root = Path("/home/runner/work/mapping-and-inventory/mapping-and-inventory")
        self.data_dir = self.repo_root / "data"
        self.discoveries_dir = self.data_dir / "discoveries"
        self.discoveries_dir.mkdir(parents=True, exist_ok=True)
        
        self.recovered_knowledge = {
            "timestamp": datetime.utcnow().isoformat(),
            "deleted_files": [],
            "lost_documentation": [],
            "commit_insights": [],
            "deleted_branches": [],
            "valuable_comments": [],
            "summary": {
                "total_commits_analyzed": 0,
                "deleted_files_found": 0,
                "documentation_recovered": 0,
                "insights_discovered": 0
            }
        }
    
    def analyze_git_log(self, max_commits: int = 500) -> List[Dict]:
        """Analyze git commit history"""
        print("🔍 Analyzing git commit history...")
        
        try:
            # Get commit log
            result = subprocess.run(
                ["git", "log", f"-{max_commits}", "--pretty=format:%H|%an|%ae|%ad|%s", "--date=iso"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                print(f"  ⚠️  Git log failed: {result.stderr}")
                return []
            
            commits = []
            for line in result.stdout.split('\n'):
                if not line:
                    continue
                
                parts = line.split('|')
                if len(parts) >= 5:
                    commit_hash, author, email, date, message = parts[0], parts[1], parts[2], parts[3], '|'.join(parts[4:])
                    
                    commits.append({
                        "hash": commit_hash,
                        "author": author,
                        "email": email,
                        "date": date,
                        "message": message
                    })
            
            self.recovered_knowledge["summary"]["total_commits_analyzed"] = len(commits)
            print(f"  ✅ Analyzed {len(commits)} commits")
            
            # Extract insights from commit messages
            self._extract_commit_insights(commits)
            
            return commits
        
        except Exception as e:
            print(f"  ❌ Error analyzing git log: {e}")
            return []
    
    def _extract_commit_insights(self, commits: List[Dict]) -> None:
        """Extract valuable insights from commit messages"""
        insight_keywords = [
            "fix", "bug", "issue", "problem", "error", "fail",
            "important", "critical", "urgent", "breaking",
            "deprecate", "remove", "delete", "legacy",
            "security", "vulnerability", "patch",
            "performance", "optimize", "improve"
        ]
        
        for commit in commits:
            message_lower = commit["message"].lower()
            
            # Check for insight keywords
            if any(keyword in message_lower for keyword in insight_keywords):
                insight = {
                    "commit_hash": commit["hash"][:8],
                    "date": commit["date"],
                    "message": commit["message"],
                    "category": self._categorize_commit(message_lower),
                    "importance": "high" if any(kw in message_lower for kw in ["critical", "urgent", "security"]) else "medium"
                }
                self.recovered_knowledge["commit_insights"].append(insight)
                self.recovered_knowledge["summary"]["insights_discovered"] += 1
    
    def _categorize_commit(self, message: str) -> str:
        """Categorize commit by type"""
        if any(kw in message for kw in ["fix", "bug", "issue"]):
            return "bug_fix"
        elif any(kw in message for kw in ["security", "vulnerability"]):
            return "security"
        elif any(kw in message for kw in ["deprecate", "remove", "delete"]):
            return "deprecation"
        elif any(kw in message for kw in ["performance", "optimize"]):
            return "performance"
        elif any(kw in message for kw in ["breaking", "major"]):
            return "breaking_change"
        else:
            return "general"
    
    def find_deleted_files(self) -> List[Dict]:
        """Find files that were deleted in git history"""
        print("\n🔍 Searching for deleted files...")
        
        try:
            # Find deleted files
            result = subprocess.run(
                ["git", "log", "--diff-filter=D", "--summary", "--pretty=format:%H|%ad|%s", "--date=short"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                print(f"  ⚠️  Git deleted files search failed")
                return []
            
            deleted_files = []
            current_commit = None
            current_date = None
            current_message = None
            
            for line in result.stdout.split('\n'):
                if '|' in line and len(line.split('|')) >= 3:
                    # Commit line
                    parts = line.split('|')
                    current_commit = parts[0][:8]
                    current_date = parts[1]
                    current_message = '|'.join(parts[2:])
                elif line.strip().startswith('delete mode'):
                    # Deleted file line
                    filepath = line.split()[-1]
                    
                    # Focus on documentation and important files
                    if any(ext in filepath.lower() for ext in ['.md', '.txt', '.json', '.py', '.js', '.yaml', '.yml']):
                        deleted_file = {
                            "filepath": filepath,
                            "commit_hash": current_commit,
                            "deleted_date": current_date,
                            "commit_message": current_message,
                            "file_type": Path(filepath).suffix,
                            "importance": "high" if any(doc in filepath.lower() for doc in 
                                                       ['readme', 'guide', 'manual', 'doc', 'config']) else "medium"
                        }
                        deleted_files.append(deleted_file)
                        self.recovered_knowledge["deleted_files"].append(deleted_file)
                        
                        if len(deleted_files) <= 10:
                            print(f"  📄 Found deleted: {filepath} (commit {current_commit})")
            
            if len(deleted_files) > 10:
                print(f"  ... and {len(deleted_files) - 10} more deleted files")
            
            self.recovered_knowledge["summary"]["deleted_files_found"] = len(deleted_files)
            return deleted_files
        
        except Exception as e:
            print(f"  ❌ Error finding deleted files: {e}")
            return []
    
    def recover_deleted_documentation(self, deleted_files: List[Dict]) -> None:
        """Attempt to recover content of deleted documentation"""
        print("\n🔍 Recovering deleted documentation...")
        
        doc_extensions = {'.md', '.txt', '.rst', '.adoc'}
        
        for deleted_file in deleted_files:
            if Path(deleted_file["filepath"]).suffix.lower() not in doc_extensions:
                continue
            
            try:
                # Get file content from the commit before deletion
                result = subprocess.run(
                    ["git", "show", f"{deleted_file['commit_hash']}~1:{deleted_file['filepath']}"],
                    cwd=self.repo_root,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0 and result.stdout:
                    content = result.stdout
                    
                    # Extract first 500 chars as preview
                    preview = content[:500] if len(content) > 500 else content
                    
                    recovered_doc = {
                        "filepath": deleted_file["filepath"],
                        "commit_hash": deleted_file["commit_hash"],
                        "size_chars": len(content),
                        "preview": preview,
                        "lines": len(content.split('\n')),
                        "recovered_at": datetime.utcnow().isoformat()
                    }
                    
                    self.recovered_knowledge["lost_documentation"].append(recovered_doc)
                    self.recovered_knowledge["summary"]["documentation_recovered"] += 1
                    
                    if len(self.recovered_knowledge["lost_documentation"]) <= 5:
                        print(f"  📚 Recovered: {deleted_file['filepath']} ({len(content)} chars)")
            
            except Exception as e:
                pass  # Skip files that can't be recovered
        
        if self.recovered_knowledge["summary"]["documentation_recovered"] > 5:
            print(f"  ... and {self.recovered_knowledge['summary']['documentation_recovered'] - 5} more documents")
    
    def find_deleted_branches(self) -> List[Dict]:
        """Find deleted/merged branches that might contain knowledge"""
        print("\n🔍 Searching for deleted branches...")
        
        try:
            # Get reflog for branch operations
            result = subprocess.run(
                ["git", "reflog", "--date=short", "--pretty=format:%gd|%ad|%gs"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return []
            
            deleted_branches = set()
            
            for line in result.stdout.split('\n'):
                if 'branch:' in line.lower() and ('delete' in line.lower() or 'merge' in line.lower()):
                    parts = line.split('|')
                    if len(parts) >= 3:
                        deleted_branch = {
                            "reference": parts[0],
                            "date": parts[1],
                            "operation": parts[2],
                            "detected_at": datetime.utcnow().isoformat()
                        }
                        
                        # Extract branch name
                        branch_match = re.search(r'branch[:\s]+([^\s,]+)', parts[2])
                        if branch_match:
                            deleted_branch["branch_name"] = branch_match.group(1)
                            deleted_branches.add(deleted_branch["branch_name"])
                            self.recovered_knowledge["deleted_branches"].append(deleted_branch)
            
            if deleted_branches:
                print(f"  🌿 Found {len(deleted_branches)} deleted/merged branches")
            
            return list(self.recovered_knowledge["deleted_branches"])
        
        except Exception as e:
            print(f"  ⚠️  Branch search error: {e}")
            return []
    
    def extract_valuable_comments(self) -> None:
        """Extract valuable TODO/FIXME/NOTE comments from codebase"""
        print("\n🔍 Extracting valuable code comments...")
        
        comment_patterns = {
            "todo": re.compile(r'#\s*TODO:?\s*(.+)', re.IGNORECASE),
            "fixme": re.compile(r'#\s*FIXME:?\s*(.+)', re.IGNORECASE),
            "note": re.compile(r'#\s*NOTE:?\s*(.+)', re.IGNORECASE),
            "hack": re.compile(r'#\s*HACK:?\s*(.+)', re.IGNORECASE),
            "warning": re.compile(r'#\s*WARNING:?\s*(.+)', re.IGNORECASE),
        }
        
        python_files = list(self.repo_root.glob("**/*.py"))
        python_files = [f for f in python_files if '.git' not in str(f)]
        
        for filepath in python_files[:100]:  # Limit to 100 files
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                
                for line_num, line in enumerate(lines, 1):
                    for comment_type, pattern in comment_patterns.items():
                        match = pattern.search(line)
                        if match:
                            comment = {
                                "type": comment_type,
                                "file": str(filepath.relative_to(self.repo_root)),
                                "line": line_num,
                                "comment": match.group(1).strip(),
                                "importance": "high" if comment_type in ["fixme", "hack", "warning"] else "medium"
                            }
                            self.recovered_knowledge["valuable_comments"].append(comment)
            
            except Exception as e:
                pass
        
        if self.recovered_knowledge["valuable_comments"]:
            print(f"  💬 Found {len(self.recovered_knowledge['valuable_comments'])} valuable comments")
    
    def generate_recovery_report(self) -> None:
        """Generate knowledge recovery report"""
        report_file = self.discoveries_dir / "knowledge_recovery.json"
        with open(report_file, 'w') as f:
            json.dump(self.recovered_knowledge, f, indent=2)
        
        # Generate markdown report
        md_content = f"""# 📚 KNOWLEDGE RECOVERY REPORT

**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}  
**Commits Analyzed:** {self.recovered_knowledge['summary']['total_commits_analyzed']}

## 🎯 Summary

- **Deleted Files:** {self.recovered_knowledge['summary']['deleted_files_found']}
- **Recovered Documentation:** {self.recovered_knowledge['summary']['documentation_recovered']}
- **Commit Insights:** {self.recovered_knowledge['summary']['insights_discovered']}
- **Deleted Branches:** {len(self.recovered_knowledge['deleted_branches'])}
- **Valuable Comments:** {len(self.recovered_knowledge['valuable_comments'])}

---

## 📄 Top Deleted Files

"""
        for deleted in self.recovered_knowledge["deleted_files"][:15]:
            md_content += f"- **{deleted['filepath']}** - Deleted in commit `{deleted['commit_hash']}` ({deleted['deleted_date']})\n"
            md_content += f"  - Message: *{deleted['commit_message']}*\n"
        
        md_content += f"\n## 💡 Key Commit Insights\n\n"
        
        insights_by_category = {}
        for insight in self.recovered_knowledge["commit_insights"]:
            category = insight["category"]
            if category not in insights_by_category:
                insights_by_category[category] = []
            insights_by_category[category].append(insight)
        
        for category, insights in sorted(insights_by_category.items()):
            md_content += f"### {category.replace('_', ' ').title()} ({len(insights)})\n\n"
            for insight in insights[:5]:
                md_content += f"- `{insight['commit_hash']}` ({insight['date']}): {insight['message']}\n"
            md_content += "\n"
        
        md_content += """
---

**🏛️ Knowledge Recovered. History Preserved. Wisdom Restored.**
"""
        
        md_file = self.discoveries_dir / "KNOWLEDGE_RECOVERY_REPORT.md"
        with open(md_file, 'w') as f:
            f.write(md_content)
        
        print(f"\n💾 Reports saved:")
        print(f"   JSON: {report_file}")
        print(f"   Markdown: {md_file}")
    
    def run_full_recovery(self) -> None:
        """Run complete knowledge recovery process"""
        print("🏛️ CITADEL KNOWLEDGE RECOVERY ENGINE")
        print("=" * 60)
        print("📚 Mining git history for lost knowledge...\n")
        
        commits = self.analyze_git_log(500)
        deleted_files = self.find_deleted_files()
        self.recover_deleted_documentation(deleted_files)
        self.find_deleted_branches()
        self.extract_valuable_comments()
        
        self.generate_recovery_report()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 KNOWLEDGE RECOVERY SUMMARY")
        print("=" * 60)
        print(f"Commits Analyzed: {self.recovered_knowledge['summary']['total_commits_analyzed']}")
        print(f"Deleted Files Found: {self.recovered_knowledge['summary']['deleted_files_found']}")
        print(f"Documentation Recovered: {self.recovered_knowledge['summary']['documentation_recovered']}")
        print(f"Insights Discovered: {self.recovered_knowledge['summary']['insights_discovered']}")
        print(f"Valuable Comments: {len(self.recovered_knowledge['valuable_comments'])}")

def main():
    """Main execution"""
    engine = KnowledgeRecoveryEngine()
    engine.run_full_recovery()

if __name__ == "__main__":
    main()
