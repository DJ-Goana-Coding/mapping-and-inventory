#!/usr/bin/env python3
"""
🏛️ CITADEL OMNI-PERFECTION: Master Documentation Index Generator
Phase 2.1 - Generate unified index of all documentation

Creates searchable master index linking all 84+ documentation files.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import re

class MasterDocIndexGenerator:
    """Generates comprehensive documentation index"""
    
    def __init__(self):
        self.repo_root = Path("/home/runner/work/mapping-and-inventory/mapping-and-inventory")
        
        self.doc_categories = {
            "Quick References": ["QUICKREF", "QUICKSTART"],
            "Implementation Guides": ["GUIDE", "IMPLEMENTATION", "DEPLOYMENT"],
            "Summaries & Reports": ["SUMMARY", "COMPLETE", "REPORT"],
            "Architecture & Design": ["ARCHITECTURE", "BLUEPRINT", "DESIGN"],
            "Operational Manuals": ["MANUAL", "OPERATOR", "PROTOCOL"],
            "Districts & Partitions": ["District", "Partition"],
            "Specialized Systems": ["OMEGA", "VAMGUARD", "TIA", "CITADEL"],
            "Shopping & Resources": ["SHOPPING", "ARSENAL", "TREASURE"],
            "Security & Compliance": ["SECURITY", "VAULT", "SAFETY"],
        }
        
        self.index = {
            "generated_at": datetime.utcnow().isoformat(),
            "total_documents": 0,
            "by_category": {},
            "by_type": {},
            "all_documents": []
        }
    
    def scan_documentation(self) -> None:
        """Scan repository for all documentation files"""
        print("🏛️ CITADEL MASTER DOCUMENTATION INDEX GENERATOR")
        print("=" * 70)
        print("📚 Scanning repository for documentation files...\n")
        
        # Find all markdown files
        md_files = list(self.repo_root.glob("**/*.md"))
        
        # Exclude certain directories
        exclude_dirs = {'.git', 'node_modules', '__pycache__', '.pytest_cache', 'venv'}
        md_files = [
            f for f in md_files 
            if not any(excluded in f.parts for excluded in exclude_dirs)
        ]
        
        print(f"📄 Found {len(md_files)} markdown files\n")
        
        # Process each file
        for md_file in sorted(md_files):
            doc_info = self._extract_doc_info(md_file)
            if doc_info:
                self.index["all_documents"].append(doc_info)
                self._categorize_document(doc_info)
        
        self.index["total_documents"] = len(self.index["all_documents"])
    
    def _extract_doc_info(self, filepath: Path) -> Dict:
        """Extract information from a documentation file"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Extract title (first H1 heading)
            title = filepath.stem.replace('_', ' ').replace('-', ' ')
            for line in lines[:20]:  # Check first 20 lines
                if line.startswith('# '):
                    title = line.lstrip('# ').strip()
                    break
            
            # Extract description (first paragraph after title)
            description = ""
            in_description = False
            for line in lines:
                if line.startswith('## ') or line.startswith('### '):
                    if in_description:
                        break
                elif line.startswith('# '):
                    in_description = True
                elif in_description and line.strip() and not line.startswith('**') and not line.startswith('---'):
                    description = line.strip()
                    break
            
            # Get file stats
            stat = filepath.stat()
            
            # Determine file type
            file_type = self._determine_type(filepath, title)
            
            return {
                "path": str(filepath.relative_to(self.repo_root)),
                "filename": filepath.name,
                "title": title,
                "description": description[:150] if description else "",
                "type": file_type,
                "size_kb": round(stat.st_size / 1024, 1),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "word_count": len(content.split()),
                "line_count": len(lines)
            }
        
        except Exception as e:
            print(f"  ⚠️  Error processing {filepath.name}: {e}")
            return None
    
    def _determine_type(self, filepath: Path, title: str) -> str:
        """Determine document type"""
        name_upper = filepath.stem.upper()
        title_upper = title.upper()
        
        if "QUICKREF" in name_upper or "QUICKSTART" in name_upper:
            return "Quick Reference"
        elif "GUIDE" in name_upper or "IMPLEMENTATION" in name_upper:
            return "Implementation Guide"
        elif "SUMMARY" in name_upper or "COMPLETE" in name_upper or "REPORT" in name_upper:
            return "Summary/Report"
        elif "ARCHITECTURE" in name_upper or "BLUEPRINT" in name_upper:
            return "Architecture"
        elif "MANUAL" in name_upper or "OPERATOR" in name_upper or "PROTOCOL" in name_upper:
            return "Operational Manual"
        elif "README" in name_upper:
            return "README"
        elif "SHOPPING" in name_upper or "ARSENAL" in name_upper:
            return "Resource List"
        elif "SECURITY" in name_upper or "VAULT" in name_upper or "SAFETY" in name_upper:
            return "Security"
        else:
            return "General Documentation"
    
    def _categorize_document(self, doc_info: Dict) -> None:
        """Categorize document into index structure"""
        # Add to type index
        doc_type = doc_info["type"]
        if doc_type not in self.index["by_type"]:
            self.index["by_type"][doc_type] = []
        self.index["by_type"][doc_type].append(doc_info)
        
        # Add to category index based on keywords
        categorized = False
        for category, keywords in self.doc_categories.items():
            if any(keyword.upper() in doc_info["filename"].upper() or 
                   keyword.upper() in doc_info["title"].upper() 
                   for keyword in keywords):
                if category not in self.index["by_category"]:
                    self.index["by_category"][category] = []
                self.index["by_category"][category].append(doc_info)
                categorized = True
                break
        
        if not categorized:
            if "Uncategorized" not in self.index["by_category"]:
                self.index["by_category"]["Uncategorized"] = []
            self.index["by_category"]["Uncategorized"].append(doc_info)
    
    def generate_master_index_md(self) -> None:
        """Generate master index markdown file"""
        content = f"""# 🏛️ CITADEL MASTER DOCUMENTATION INDEX

**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}  
**Total Documents:** {self.index['total_documents']}  
**Repository:** DJ-Goana-Coding/mapping-and-inventory

---

## 🎯 Purpose

This is the **unified entry point** to all documentation in the Citadel Mesh. Every guide, manual, summary, and reference is indexed here for rapid navigation.

---

## 📑 Table of Contents

1. [Quick Access](#quick-access)
2. [By Category](#by-category)
3. [By Type](#by-type)
4. [Complete Alphabetical Index](#complete-index)

---

## ⚡ Quick Access

### Most Important Documents

"""
        # Add key documents
        key_docs = [
            "README.md",
            "CITADEL_AWAKENING_GUIDE.md",
            "OMNI_AUDIT_MASTER_PLAN.md",
            "CITADEL_GRAND_UNIFICATION_GUIDE.md",
            "SYSTEM_MASTER_INDEX.md"
        ]
        
        for key_doc in key_docs:
            matching = [d for d in self.index["all_documents"] if d["filename"] == key_doc]
            if matching:
                doc = matching[0]
                content += f"- **[{doc['title']}]({doc['path']})** - {doc['description']}\n"
        
        content += "\n### Quick References\n\n"
        quickrefs = [d for d in self.index["all_documents"] if "QUICKREF" in d["filename"] or "QUICKSTART" in d["filename"]]
        for doc in sorted(quickrefs, key=lambda x: x["filename"])[:10]:
            content += f"- [{doc['title']}]({doc['path']})\n"
        
        content += "\n---\n\n## 📂 By Category\n\n"
        
        for category in sorted(self.index["by_category"].keys()):
            docs = self.index["by_category"][category]
            content += f"### {category} ({len(docs)} documents)\n\n"
            
            for doc in sorted(docs, key=lambda x: x["filename"])[:15]:  # Limit to 15 per category
                content += f"- **[{doc['title']}]({doc['path']})**"
                if doc["description"]:
                    content += f" - {doc['description'][:80]}"
                content += f" `({doc['size_kb']} KB)`\n"
            
            if len(docs) > 15:
                content += f"\n*...and {len(docs) - 15} more documents*\n"
            
            content += "\n"
        
        content += "---\n\n## 📋 By Type\n\n"
        
        for doc_type in sorted(self.index["by_type"].keys()):
            docs = self.index["by_type"][doc_type]
            content += f"### {doc_type} ({len(docs)})\n\n"
            
            for doc in sorted(docs, key=lambda x: x["filename"])[:10]:
                content += f"- [{doc['filename']}]({doc['path']})\n"
            
            if len(docs) > 10:
                content += f"\n*...and {len(docs) - 10} more*\n"
            
            content += "\n"
        
        content += f"""---

## 📚 Complete Index

<details>
<summary>Click to expand full alphabetical list ({self.index['total_documents']} documents)</summary>

"""
        
        for doc in sorted(self.index["all_documents"], key=lambda x: x["filename"]):
            content += f"- **{doc['filename']}** - [{doc['title']}]({doc['path']}) ({doc['size_kb']} KB, {doc['word_count']} words)\n"
        
        content += """
</details>

---

## 🔍 Search Tips

1. **By Keyword**: Use browser search (Ctrl+F) to find specific terms
2. **By Category**: Navigate to relevant category section above
3. **By Type**: Check the document type you need (Guide, Manual, etc.)
4. **By System**: Look for system names (OMEGA, TIA, VAMGUARD, etc.)

---

## 📊 Statistics

"""
        
        total_size = sum(d["size_kb"] for d in self.index["all_documents"])
        total_words = sum(d["word_count"] for d in self.index["all_documents"])
        
        content += f"- **Total Size**: {total_size:.1f} KB ({total_size/1024:.2f} MB)\n"
        content += f"- **Total Words**: {total_words:,}\n"
        content += f"- **Average Document Size**: {total_size/self.index['total_documents']:.1f} KB\n"
        content += f"- **Average Word Count**: {total_words//self.index['total_documents']:,} words\n"
        
        content += f"""

---

## 🔄 Maintenance

This index is automatically generated by `scripts/generate_master_doc_index.py`.

**Last Updated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

To regenerate:
```bash
python scripts/generate_master_doc_index.py
```

---

**🏛️ The Citadel Remembers. Knowledge Preserved. Wisdom Accessible.**
"""
        
        # Save master index
        index_file = self.repo_root / "SYSTEM_MASTER_INDEX.md"
        with open(index_file, 'w') as f:
            f.write(content)
        
        print(f"\n✅ Generated master index: {index_file}")
        
        # Also save JSON version
        json_file = self.repo_root / "data" / "system_master_index.json"
        json_file.parent.mkdir(parents=True, exist_ok=True)
        with open(json_file, 'w') as f:
            json.dump(self.index, f, indent=2)
        
        print(f"✅ Generated JSON index: {json_file}")
    
    def print_summary(self) -> None:
        """Print generation summary"""
        print("\n" + "=" * 70)
        print("📊 DOCUMENTATION INDEX SUMMARY")
        print("=" * 70)
        print(f"Total Documents: {self.index['total_documents']}")
        print(f"\nBy Category:")
        for category, docs in sorted(self.index["by_category"].items(), key=lambda x: len(x[1]), reverse=True):
            print(f"  {category}: {len(docs)}")
        
        total_size = sum(d["size_kb"] for d in self.index["all_documents"])
        total_words = sum(d["word_count"] for d in self.index["all_documents"])
        print(f"\nTotal Size: {total_size:.1f} KB ({total_size/1024:.2f} MB)")
        print(f"Total Words: {total_words:,}")

def main():
    """Main execution"""
    generator = MasterDocIndexGenerator()
    generator.scan_documentation()
    generator.generate_master_index_md()
    generator.print_summary()

if __name__ == "__main__":
    main()
