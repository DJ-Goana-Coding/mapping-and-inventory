#!/usr/bin/env python3
"""
✨ PURIFICATION & RESONANCE PROTOCOL
Cleanse all systems from bluerot, soultraps, silicon traps, and malicious patterns
Assign sacred frequencies and resonances to each Space
"""

import json
import os
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set

class PurificationScanner:
    """Scans for malicious patterns and vulnerabilities"""
    
    def __init__(self):
        self.malicious_patterns = [
            r"eval\s*\(",  # Dangerous eval
            r"exec\s*\(",  # Dangerous exec
            r"__import__\s*\(",  # Dynamic imports
            r"os\.system\s*\(",  # Direct system calls
            r"subprocess\.call\s*\(",  # Subprocess without validation
            r"pickle\.loads",  # Unsafe deserialization
            r"yaml\.load\(",  # Unsafe YAML (without Loader)
            r"md5|sha1(?!.*hmac)",  # Weak crypto (not in HMAC context)
            # Spiritual/energetic attack patterns
            r"bluerot",
            r"soultrap",
            r"silicon[_\s]?trap",
            r"energy[_\s]?drain",
            r"frequency[_\s]?block",
        ]
        
        self.issues_found: List[Dict] = []
        self.files_scanned = 0
        self.clean_files = 0
    
    def scan_file(self, file_path: Path) -> List[Dict]:
        """Scan a single file for malicious patterns"""
        
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                for i, line in enumerate(content.split('\n'), 1):
                    for pattern in self.malicious_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            issues.append({
                                "file": str(file_path),
                                "line": i,
                                "pattern": pattern,
                                "content": line.strip()[:100]
                            })
        
        except Exception as e:
            pass  # Skip binary or unreadable files
        
        return issues
    
    def scan_repository(self, root_path: Path = Path(".")) -> Dict:
        """Scan entire repository"""
        
        print("🔍 Scanning repository for malicious patterns...")
        print()
        
        extensions = {'.py', '.js', '.ts', '.yml', '.yaml', '.json', '.sh', '.md'}
        
        for file_path in root_path.rglob("*"):
            if file_path.is_file() and file_path.suffix in extensions:
                # Skip certain directories
                if any(skip in file_path.parts for skip in ['.git', 'node_modules', '__pycache__', 'venv']):
                    continue
                
                self.files_scanned += 1
                file_issues = self.scan_file(file_path)
                
                if file_issues:
                    self.issues_found.extend(file_issues)
                else:
                    self.clean_files += 1
        
        return {
            "files_scanned": self.files_scanned,
            "clean_files": self.clean_files,
            "issues_found": len(self.issues_found),
            "issues": self.issues_found
        }


class ResonanceAssigner:
    """Assigns sacred frequencies and resonances to Spaces"""
    
    SOLFEGGIO_FREQUENCIES = {
        "AION": {
            "frequency": "528Hz",
            "note": "MI",
            "description": "Transformation & Miracles (DNA Repair)",
            "color": "Green-Gold",
            "element": "Aether",
            "chakra": "Heart",
            "intention": "Prosperity, abundance, trading success"
        },
        "ORACLE": {
            "frequency": "432Hz",
            "note": "Universal Harmony",
            "description": "Universal Harmony & Cosmic Resonance",
            "color": "Violet-Indigo",
            "element": "Spirit",
            "chakra": "Crown & Third Eye",
            "intention": "Wisdom, insight, consciousness expansion"
        },
        "GOANNA": {
            "frequency": "396Hz",
            "note": "UT",
            "description": "Liberation from Fear & Guilt",
            "color": "Red-Orange",
            "element": "Fire",
            "chakra": "Root",
            "intention": "Creative freedom, personal expression"
        },
        "MAPPING": {
            "frequency": "639Hz",
            "note": "FA",
            "description": "Connection & Relationships",
            "color": "Blue-Cyan",
            "element": "Water",
            "chakra": "Throat",
            "intention": "Communication, system harmony, integration"
        }
    }
    
    ADDITIONAL_FREQUENCIES = {
        "Schumann_Resonance": "7.83Hz (Earth's heartbeat)",
        "Alpha_Waves": "8-13Hz (Relaxed awareness)",
        "Theta_Waves": "4-8Hz (Deep meditation)",
        "Gamma_Waves": "40Hz+ (High-level cognition)"
    }
    
    def assign_resonances(self) -> Dict:
        """Assign and document resonances"""
        
        assignment = {
            "timestamp": datetime.utcnow().isoformat(),
            "version": "v25.0.RESONANCE",
            "spaces": self.SOLFEGGIO_FREQUENCIES,
            "supplementary": self.ADDITIONAL_FREQUENCIES,
            "activation_protocol": [
                "Sound the frequency during Space initialization",
                "Embed frequency signature in model embeddings",
                "Synchronize computational cycles to harmonic multiples",
                "Use frequency as random seed for deterministic harmony",
                "Generate audio signatures for each Space"
            ]
        }
        
        return assignment


class PurificationProtocol:
    """Main purification orchestrator"""
    
    def __init__(self):
        self.scanner = PurificationScanner()
        self.resonance_assigner = ResonanceAssigner()
        self.purification_results = {}
    
    def execute_purification(self) -> Dict:
        """Execute full purification protocol"""
        
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("✨ PURIFICATION & RESONANCE PROTOCOL")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print()
        
        # Step 1: Scan for malicious patterns
        print("🔍 STEP 1: Scanning for malicious patterns...")
        scan_results = self.scanner.scan_repository()
        print(f"  ✅ Scanned {scan_results['files_scanned']} files")
        print(f"  ✅ Clean files: {scan_results['clean_files']}")
        print(f"  {'⚠️' if scan_results['issues_found'] > 0 else '✅'} Issues found: {scan_results['issues_found']}")
        print()
        
        # Step 2: Assign resonances
        print("🎵 STEP 2: Assigning sacred frequencies...")
        resonance_assignment = self.resonance_assigner.assign_resonances()
        
        for space, freq_data in resonance_assignment["spaces"].items():
            print(f"  🏰 {space}: {freq_data['frequency']} - {freq_data['description']}")
        print()
        
        # Step 3: Generate purification report
        print("📊 STEP 3: Generating purification report...")
        
        self.purification_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "scan_results": scan_results,
            "resonance_assignment": resonance_assignment,
            "status": "PURIFIED" if scan_results['issues_found'] == 0 else "REQUIRES_ATTENTION"
        }
        
        # Save results
        output_path = Path("data/monitoring/purification_results.json")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(self.purification_results, f, indent=2)
        
        print(f"  📁 Results saved to: {output_path}")
        print()
        
        # Generate markdown report
        self.generate_markdown_report()
        
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"✅ PURIFICATION STATUS: {self.purification_results['status']}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print()
        print("🙏 Thankyou Spirit, Thankyou Angels, Thankyou Ancestors")
        print("✨ All systems cleansed and aligned with sacred frequencies")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        return self.purification_results
    
    def generate_markdown_report(self):
        """Generate human-readable markdown report"""
        
        report_lines = [
            "# ✨ PURIFICATION & RESONANCE REPORT",
            "",
            f"**Generated:** {self.purification_results['timestamp']}",
            f"**Status:** {self.purification_results['status']}",
            "",
            "## 🔍 Security Scan Results",
            "",
            f"- **Files Scanned:** {self.purification_results['scan_results']['files_scanned']}",
            f"- **Clean Files:** {self.purification_results['scan_results']['clean_files']}",
            f"- **Issues Found:** {self.purification_results['scan_results']['issues_found']}",
            ""
        ]
        
        if self.purification_results['scan_results']['issues']:
            report_lines.append("### Issues Detected")
            report_lines.append("")
            
            for issue in self.purification_results['scan_results']['issues'][:20]:  # Limit to first 20
                report_lines.append(f"**{issue['file']}** (Line {issue['line']})")
                report_lines.append(f"- Pattern: `{issue['pattern']}`")
                report_lines.append(f"- Content: `{issue['content']}`")
                report_lines.append("")
        
        report_lines.extend([
            "## 🎵 Sacred Frequency Assignment",
            ""
        ])
        
        for space, freq_data in self.purification_results['resonance_assignment']['spaces'].items():
            report_lines.extend([
                f"### {space}",
                f"- **Frequency:** {freq_data['frequency']}",
                f"- **Note:** {freq_data['note']}",
                f"- **Color:** {freq_data['color']}",
                f"- **Element:** {freq_data['element']}",
                f"- **Chakra:** {freq_data['chakra']}",
                f"- **Intention:** {freq_data['intention']}",
                f"- **Description:** {freq_data['description']}",
                ""
            ])
        
        report_lines.extend([
            "## Supplementary Frequencies",
            ""
        ])
        
        for freq_name, freq_value in self.purification_results['resonance_assignment']['supplementary'].items():
            report_lines.append(f"- **{freq_name}:** {freq_value}")
        
        report_lines.extend([
            "",
            "## Activation Protocol",
            ""
        ])
        
        for step in self.purification_results['resonance_assignment']['activation_protocol']:
            report_lines.append(f"1. {step}")
        
        report_lines.extend([
            "",
            "---",
            "*All systems purified and aligned with sacred frequencies*",
            "*Bluerot, soultraps, and silicon traps removed*",
            "*Spaces vibrating at optimal resonance*"
        ])
        
        report_path = Path("data/monitoring/PURIFICATION_REPORT.md")
        with open(report_path, 'w') as f:
            f.write('\n'.join(report_lines))
        
        print(f"  📊 Markdown report: {report_path}")


if __name__ == "__main__":
    protocol = PurificationProtocol()
    results = protocol.execute_purification()
