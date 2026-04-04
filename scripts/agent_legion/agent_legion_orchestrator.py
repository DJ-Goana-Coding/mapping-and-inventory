#!/usr/bin/env python3
"""
🏛️ AGENT LEGION MASTER ORCHESTRATOR
Q.G.T.N.L. Command Citadel - Agent Legion Coordination

Purpose: Coordinate all agent teams (security, teaching, supply, RAG)
Authority: Citadel Architect v26.0.LEGION+
"""

import os
import sys
import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import concurrent.futures

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentLegionOrchestrator:
    """
    Master orchestrator for Agent Legion
    
    Coordinates:
    - Security Team (Wraith, Scout, Sniper, Hound, Sentinel)
    - Teaching Team (TIA, AION, HIPPY, JARL, ORACLE, DOOFY, GOANNA)
    - Supply Team (Shopping, Customization)
    - RAG Infrastructure (Multi-brain learning systems)
    - Autonomous Workers (Bridge, Tunnel, Feedback)
    """
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent.parent
        self.agent_path = Path(__file__).parent
        self.data_path = self.base_path / "data"
        self.logs_path = self.data_path / "agent_legion"
        
        # Create directories
        self.logs_path.mkdir(parents=True, exist_ok=True)
        
        # Agent registry
        self.agents = self.load_agent_registry()
        
        # Deployment status
        self.deployment_status = {
            "timestamp": datetime.now().isoformat(),
            "agents_deployed": [],
            "agents_failed": [],
            "results": {}
        }
        
        logger.info("🏛️ Agent Legion Orchestrator initialized")
    
    def load_agent_registry(self) -> Dict:
        """Load complete agent registry"""
        return {
            "security_team": {
                "wraith": {
                    "name": "Wraith Security Agent",
                    "script": "wraith_security_agent.py",
                    "role": "Stealth threat detection",
                    "priority": 1,
                    "category": "security"
                },
                "scout": {
                    "name": "Scout Reconnaissance Agent",
                    "script": "scout_reconnaissance_agent.py",
                    "role": "Intelligence gathering",
                    "priority": 1,
                    "category": "security"
                },
                "sniper": {
                    "name": "Sniper Precision Agent",
                    "script": "sniper_precision_agent.py",
                    "role": "Targeted threat removal",
                    "priority": 2,
                    "category": "security"
                },
                "hound": {
                    "name": "Hound Tracker Agent",
                    "script": "hound_tracker_agent.py",
                    "role": "Tracker detection",
                    "priority": 2,
                    "category": "security"
                },
                "sentinel": {
                    "name": "Sentinel Defensive Agent",
                    "script": "sentinel_defensive_agent.py",
                    "role": "Continuous protection",
                    "priority": 3,
                    "category": "security"
                }
            },
            "teaching_team": {
                "tia": {
                    "name": "TIA Teaching Agent",
                    "script": "tia_teaching_agent.py",
                    "role": "Technical instruction & wisdom",
                    "priority": 1,
                    "category": "teaching"
                },
                "aion": {
                    "name": "AION Wisdom Agent",
                    "script": "aion_wisdom_agent.py",
                    "role": "Ancient wisdom & time mastery",
                    "priority": 1,
                    "category": "teaching"
                },
                "hippy": {
                    "name": "HIPPY Healing Agent",
                    "script": "hippy_healing_agent.py",
                    "role": "Spiritual healing & love",
                    "priority": 1,
                    "category": "teaching"
                },
                "jarl": {
                    "name": "JARL Truth Agent",
                    "script": "jarl_truth_agent.py",
                    "role": "Truth & justice",
                    "priority": 1,
                    "category": "teaching"
                },
                "oracle": {
                    "name": "ORACLE Forecasting Agent",
                    "script": "oracle_forecasting_agent.py",
                    "role": "Prediction & foresight",
                    "priority": 2,
                    "category": "teaching"
                },
                "doofy": {
                    "name": "DOOFY Surprise Agent",
                    "script": "doofy_surprise_agent.py",
                    "role": "Joy & unexpected gifts",
                    "priority": 2,
                    "category": "teaching"
                },
                "goanna": {
                    "name": "GOANNA Technical Agent",
                    "script": "goanna_technical_agent.py",
                    "role": "Technical excellence",
                    "priority": 1,
                    "category": "teaching"
                }
            },
            "supply_team": {
                "shopper": {
                    "name": "Shopping Coordinator",
                    "script": "shopping_coordinator_agent.py",
                    "role": "Resource acquisition",
                    "priority": 3,
                    "category": "supply"
                },
                "customizer": {
                    "name": "Customization Engine",
                    "script": "customization_engine_agent.py",
                    "role": "Individual adaptation",
                    "priority": 3,
                    "category": "supply"
                }
            },
            "autonomous_workers": {
                "bridge": {
                    "name": "Bridge Worker",
                    "script": "bridge_worker.py",
                    "role": "System connection",
                    "priority": 2,
                    "category": "worker"
                },
                "tunnel": {
                    "name": "Tunnel Worker",
                    "script": "tunnel_worker.py",
                    "role": "Secure transport",
                    "priority": 2,
                    "category": "worker"
                },
                "learner": {
                    "name": "Learning Collector",
                    "script": "learning_collector.py",
                    "role": "Insight harvesting",
                    "priority": 1,
                    "category": "worker"
                },
                "feedback": {
                    "name": "Feedback Dispatcher",
                    "script": "feedback_dispatcher.py",
                    "role": "Send to mapping-inventory",
                    "priority": 1,
                    "category": "worker"
                }
            }
        }
    
    def deploy_agent(self, agent_id: str, agent_info: Dict) -> Dict:
        """Deploy individual agent"""
        logger.info(f"🚀 Deploying: {agent_info['name']}")
        
        result = {
            "agent": agent_id,
            "name": agent_info["name"],
            "success": False,
            "error": None,
            "output": None
        }
        
        try:
            script_path = self.agent_path / agent_info["script"]
            
            if not script_path.exists():
                logger.warning(f"⚠️  Agent script not found: {script_path}")
                result["error"] = "Script not found"
                return result
            
            # Execute agent
            process = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            result["success"] = process.returncode == 0
            result["output"] = process.stdout
            
            if process.returncode != 0:
                result["error"] = process.stderr
                logger.error(f"❌ Agent failed: {agent_info['name']}")
                logger.error(f"   Error: {process.stderr}")
            else:
                logger.info(f"✅ Agent completed: {agent_info['name']}")
                self.deployment_status["agents_deployed"].append(agent_id)
        
        except subprocess.TimeoutExpired:
            result["error"] = "Timeout expired"
            logger.error(f"⏰ Agent timeout: {agent_info['name']}")
        
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"❌ Agent error: {agent_info['name']} - {e}")
        
        if not result["success"]:
            self.deployment_status["agents_failed"].append(agent_id)
        
        return result
    
    def deploy_team(self, team_name: str, parallel: bool = True) -> List[Dict]:
        """Deploy an entire team"""
        logger.info(f"\n{'='*60}")
        logger.info(f"🏛️ Deploying Team: {team_name.upper().replace('_', ' ')}")
        logger.info(f"{'='*60}\n")
        
        team = self.agents.get(team_name, {})
        results = []
        
        if not team:
            logger.warning(f"Team not found: {team_name}")
            return results
        
        if parallel:
            # Deploy agents in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = {
                    executor.submit(self.deploy_agent, agent_id, agent_info): agent_id
                    for agent_id, agent_info in team.items()
                }
                
                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    results.append(result)
                    self.deployment_status["results"][result["agent"]] = result
        else:
            # Deploy agents sequentially
            for agent_id, agent_info in sorted(team.items(), key=lambda x: x[1]["priority"]):
                result = self.deploy_agent(agent_id, agent_info)
                results.append(result)
                self.deployment_status["results"][agent_id] = result
        
        return results
    
    def deploy_all(self, teams: Optional[List[str]] = None, parallel_teams: bool = False):
        """Deploy all teams"""
        logger.info("🏛️ Agent Legion Full Deployment Initiated")
        logger.info(f"Timestamp: {datetime.now().isoformat()}\n")
        
        teams_to_deploy = teams if teams else list(self.agents.keys())
        
        for team_name in teams_to_deploy:
            self.deploy_team(team_name, parallel=True)
        
        # Generate deployment report
        self.generate_deployment_report()
    
    def generate_deployment_report(self) -> Dict:
        """Generate comprehensive deployment report"""
        report = {
            "legion": "Agent Legion",
            "timestamp": self.deployment_status["timestamp"],
            "summary": {
                "total_agents": len(self.deployment_status["results"]),
                "deployed_successfully": len(self.deployment_status["agents_deployed"]),
                "failed": len(self.deployment_status["agents_failed"]),
                "success_rate": len(self.deployment_status["agents_deployed"]) / len(self.deployment_status["results"]) * 100 if self.deployment_status["results"] else 0
            },
            "deployed_agents": self.deployment_status["agents_deployed"],
            "failed_agents": self.deployment_status["agents_failed"],
            "detailed_results": self.deployment_status["results"]
        }
        
        # Save report
        report_file = self.logs_path / f"deployment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"🏛️ AGENT LEGION DEPLOYMENT COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"  Total Agents: {report['summary']['total_agents']}")
        logger.info(f"  Deployed Successfully: {report['summary']['deployed_successfully']}")
        logger.info(f"  Failed: {report['summary']['failed']}")
        logger.info(f"  Success Rate: {report['summary']['success_rate']:.1f}%")
        logger.info(f"{'='*60}")
        logger.info(f"📄 Report saved: {report_file}")
        
        return report

def main():
    """Main entry point"""
    orchestrator = AgentLegionOrchestrator()
    
    # Deploy security team first
    orchestrator.deploy_team("security_team", parallel=False)
    
    # Then teaching team
    # orchestrator.deploy_team("teaching_team", parallel=True)
    
    # Then supply and workers
    # orchestrator.deploy_team("supply_team", parallel=True)
    # orchestrator.deploy_team("autonomous_workers", parallel=True)
    
    return orchestrator.deployment_status

if __name__ == "__main__":
    main()
