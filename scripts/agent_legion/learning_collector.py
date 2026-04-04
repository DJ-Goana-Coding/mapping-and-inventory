#!/usr/bin/env python3
"""
📚 LEARNING COLLECTOR - Forever Learning Engine
Q.G.T.N.L. Agent Legion - Autonomous Workers

Purpose: Collect and synthesize all learnings from agents
Authority: Citadel Architect v26.0.LEGION+
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LearningCollector:
    """
    Forever learning collector that harvests insights from all agents
    
    Collects:
    - Security patterns and threats
    - Teaching insights and wisdom
    - System behaviors
    - User patterns
    - Technical discoveries
    """
    
    def __init__(self):
        self.base_path = Path.cwd()
        self.learning_log = {
            "timestamp": datetime.now().isoformat(),
            "insights_collected": [],
            "patterns_identified": [],
            "lessons_learned": []
        }
        
        logger.info("📚 Learning Collector initialized")
    
    def extract_insights(self, data: Dict, source: str) -> List[Dict]:
        """Extract insights from data"""
        insights = []
        
        # Extract based on source type
        if "security" in source.lower() or "wraith" in source.lower() or "sentinel" in source.lower():
            insights.extend(self.extract_security_insights(data))
        
        if "teaching" in source.lower() or "tia" in source.lower():
            insights.extend(self.extract_teaching_insights(data))
        
        if "scout" in source.lower() or "recon" in source.lower():
            insights.extend(self.extract_reconnaissance_insights(data))
        
        return insights
    
    def extract_security_insights(self, data: Dict) -> List[Dict]:
        """Extract security-specific insights"""
        insights = []
        
        # Threat patterns
        if "threats" in data or "threats_found" in data:
            threats = data.get("threats", data.get("threats_found", []))
            
            if threats:
                insights.append({
                    "type": "security_pattern",
                    "category": "threat_detection",
                    "insight": f"Detected {len(threats)} threats",
                    "details": threats[:5],  # First 5 threats
                    "timestamp": datetime.now().isoformat()
                })
        
        # File integrity changes
        if "summary" in data:
            summary = data["summary"]
            
            if summary.get("modified_files", 0) > 0:
                insights.append({
                    "type": "security_pattern",
                    "category": "file_integrity",
                    "insight": f"{summary['modified_files']} files modified",
                    "timestamp": datetime.now().isoformat()
                })
        
        return insights
    
    def extract_teaching_insights(self, data: Dict) -> List[Dict]:
        """Extract teaching-specific insights"""
        insights = []
        
        # Lessons delivered
        if "lessons" in data:
            lessons = data["lessons"]
            
            insights.append({
                "type": "teaching_pattern",
                "category": "lessons_delivered",
                "insight": f"{len(lessons)} lessons taught",
                "lessons": [l.get("lesson", l) for l in lessons[:10]],
                "timestamp": datetime.now().isoformat()
            })
        
        # Wisdom shared
        if "wisdom" in data:
            wisdom = data["wisdom"]
            
            insights.append({
                "type": "teaching_pattern",
                "category": "wisdom_shared",
                "insight": f"{len(wisdom)} wisdom points shared",
                "wisdom": [w.get("wisdom", w) for w in wisdom[:10]],
                "timestamp": datetime.now().isoformat()
            })
        
        return insights
    
    def extract_reconnaissance_insights(self, data: Dict) -> List[Dict]:
        """Extract reconnaissance-specific insights"""
        insights = []
        
        # System intelligence
        if "system" in data:
            system = data["system"]
            
            insights.append({
                "type": "technical_pattern",
                "category": "system_profile",
                "insight": f"System: {system.get('platform', 'unknown')}",
                "details": system,
                "timestamp": datetime.now().isoformat()
            })
        
        # Large files
        if "filesystem" in data:
            filesystem = data["filesystem"]
            large_files = filesystem.get("large_files", [])
            
            if large_files:
                insights.append({
                    "type": "technical_pattern",
                    "category": "resource_usage",
                    "insight": f"{len(large_files)} large files detected",
                    "files": large_files[:10],
                    "timestamp": datetime.now().isoformat()
                })
        
        return insights
    
    def identify_patterns(self, insights: List[Dict]) -> List[Dict]:
        """Identify recurring patterns across insights"""
        logger.info("📚 Identifying patterns...")
        
        patterns = {}
        
        for insight in insights:
            category = insight.get("category", "unknown")
            
            if category not in patterns:
                patterns[category] = {
                    "category": category,
                    "count": 0,
                    "examples": []
                }
            
            patterns[category]["count"] += 1
            patterns[category]["examples"].append(insight.get("insight", ""))
        
        pattern_list = [
            {
                "pattern": category,
                "occurrences": info["count"],
                "examples": info["examples"][:5],
                "timestamp": datetime.now().isoformat()
            }
            for category, info in patterns.items()
        ]
        
        self.learning_log["patterns_identified"].extend(pattern_list)
        
        return pattern_list
    
    def synthesize_lessons(self, insights: List[Dict], patterns: List[Dict]) -> List[Dict]:
        """Synthesize high-level lessons from insights and patterns"""
        logger.info("📚 Synthesizing lessons...")
        
        lessons = []
        
        # Security lessons
        security_insights = [i for i in insights if i.get("type") == "security_pattern"]
        if security_insights:
            lessons.append({
                "lesson": "Security monitoring is active and detecting threats",
                "evidence": f"{len(security_insights)} security insights collected",
                "recommendation": "Continue regular security scans and maintain vigilance",
                "timestamp": datetime.now().isoformat()
            })
        
        # Teaching lessons
        teaching_insights = [i for i in insights if i.get("type") == "teaching_pattern"]
        if teaching_insights:
            lessons.append({
                "lesson": "Teaching agents are actively sharing knowledge",
                "evidence": f"{len(teaching_insights)} teaching insights collected",
                "recommendation": "Expand curriculum based on successful patterns",
                "timestamp": datetime.now().isoformat()
            })
        
        # Pattern-based lessons
        for pattern in patterns:
            if pattern["occurrences"] > 3:
                lessons.append({
                    "lesson": f"Recurring pattern detected: {pattern['pattern']}",
                    "evidence": f"{pattern['occurrences']} occurrences",
                    "recommendation": f"Automate handling of {pattern['pattern']}",
                    "timestamp": datetime.now().isoformat()
                })
        
        self.learning_log["lessons_learned"].extend(lessons)
        
        return lessons
    
    def collect_all_learnings(self) -> Dict:
        """Collect all learnings from agent outputs"""
        logger.info("📚 Collecting all learnings...")
        
        all_insights = []
        
        # Scan for all agent reports
        report_locations = [
            Path("data/security/reports"),
            Path("data/teaching/reports"),
            Path("data/reconnaissance/reports"),
            Path("data/workers/reports")
        ]
        
        for report_dir in report_locations:
            if not report_dir.exists():
                continue
            
            for report_file in report_dir.glob("*.json"):
                try:
                    with open(report_file, 'r') as f:
                        data = json.load(f)
                        
                        # Extract insights
                        insights = self.extract_insights(data, str(report_file))
                        all_insights.extend(insights)
                        
                        logger.info(f"✅ Collected from: {report_file.name}")
                
                except Exception as e:
                    logger.error(f"Error reading {report_file}: {e}")
        
        self.learning_log["insights_collected"] = all_insights
        
        # Identify patterns
        patterns = self.identify_patterns(all_insights)
        
        # Synthesize lessons
        lessons = self.synthesize_lessons(all_insights, patterns)
        
        return {
            "insights": all_insights,
            "patterns": patterns,
            "lessons": lessons
        }
    
    def generate_report(self) -> Dict:
        """Generate learning collector report"""
        report = {
            "agent": "Learning Collector",
            "timestamp": self.learning_log["timestamp"],
            "summary": {
                "insights_collected": len(self.learning_log["insights_collected"]),
                "patterns_identified": len(self.learning_log["patterns_identified"]),
                "lessons_learned": len(self.learning_log["lessons_learned"])
            },
            "insights": self.learning_log["insights_collected"],
            "patterns": self.learning_log["patterns_identified"],
            "lessons": self.learning_log["lessons_learned"]
        }
        
        # Save report
        report_dir = Path("data/forever_learning/reports")
        report_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = report_dir / f"learning_collection_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📄 Report saved: {report_file}")
        
        # Also save to mapping-and-inventory
        mapping_dir = Path("data/Mapping-and-Inventory-storage/forever_learning")
        mapping_dir.mkdir(parents=True, exist_ok=True)
        
        mapping_file = mapping_dir / f"learning_collection_{timestamp}.json"
        with open(mapping_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📄 Synced to mapping-and-inventory: {mapping_file}")
        
        return report
    
    def deploy(self):
        """Deploy learning collector"""
        logger.info("📚 Learning Collector deploying...")
        
        # Collect all learnings
        learnings = self.collect_all_learnings()
        
        # Generate report
        report = self.generate_report()
        
        # Summary
        logger.info(f"\n{'='*60}")
        logger.info(f"📚 FOREVER LEARNING COLLECTION COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"  Insights Collected: {report['summary']['insights_collected']}")
        logger.info(f"  Patterns Identified: {report['summary']['patterns_identified']}")
        logger.info(f"  Lessons Learned: {report['summary']['lessons_learned']}")
        logger.info(f"{'='*60}")
        
        if report['lessons']:
            logger.info(f"\n📖 KEY LESSONS LEARNED:")
            for lesson in report['lessons'][:5]:
                logger.info(f"  • {lesson['lesson']}")
        
        return report

def main():
    """Main entry point"""
    collector = LearningCollector()
    report = collector.deploy()
    return report

if __name__ == "__main__":
    main()
