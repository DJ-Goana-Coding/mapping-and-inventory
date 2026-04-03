#!/usr/bin/env python3
"""
🎮 CITADEL COMMAND CENTER - Real-Time Monitoring Dashboard
Q.G.T.N.L. Command Citadel - Central Control Interface

Purpose: Visual command center for monitoring all Citadel operations
Authority: Citadel Architect v26.0.COMMAND_CENTER+
"""

import streamlit as st
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import time
import subprocess
import sys

# Page config
st.set_page_config(
    page_title="🏰 Citadel Command Center",
    page_icon="🏰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Paths
BASE_PATH = Path(__file__).parent.parent
DATA_PATH = BASE_PATH / "data"
LOGS_PATH = DATA_PATH / "logs"
MONITORING_PATH = DATA_PATH / "monitoring"
DISCOVERIES_PATH = DATA_PATH / "discoveries"

class CommandCenter:
    """Citadel Command Center Dashboard"""
    
    def __init__(self):
        self.deployment_results_file = MONITORING_PATH / "deployment_results.json"
        self.worker_status_file = BASE_PATH / "worker_status.json"
        self.districts_file = BASE_PATH / "districts.json"
        self.system_manifest_file = BASE_PATH / "system_manifest.json"
    
    def load_deployment_results(self):
        """Load latest deployment results"""
        if self.deployment_results_file.exists():
            with open(self.deployment_results_file, 'r') as f:
                return json.load(f)
        return None
    
    def load_worker_status(self):
        """Load worker status"""
        if self.worker_status_file.exists():
            with open(self.worker_status_file, 'r') as f:
                return json.load(f)
        return {}
    
    def load_districts(self):
        """Load districts registry"""
        if self.districts_file.exists():
            with open(self.districts_file, 'r') as f:
                return json.load(f)
        return {}
    
    def load_system_manifest(self):
        """Load system manifest"""
        if self.system_manifest_file.exists():
            with open(self.system_manifest_file, 'r') as f:
                return json.load(f)
        return {}
    
    def get_recent_logs(self, log_file: str, lines: int = 50):
        """Get recent log entries"""
        log_path = LOGS_PATH / log_file
        if log_path.exists():
            with open(log_path, 'r') as f:
                all_lines = f.readlines()
                return all_lines[-lines:]
        return []
    
    def trigger_awakening(self):
        """Trigger Citadel awakening"""
        st.info("🚀 Triggering Citadel Awakening...")
        try:
            result = subprocess.run(
                [sys.executable, str(BASE_PATH / "scripts" / "citadel_awakening.py")],
                cwd=str(BASE_PATH),
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode == 0:
                st.success("✅ Citadel Awakening Complete!")
                st.code(result.stdout[-1000:])
            else:
                st.error("❌ Awakening Failed")
                st.code(result.stderr[-1000:])
        except subprocess.TimeoutExpired:
            st.warning("⏱️ Awakening still running (timeout reached)")
        except Exception as e:
            st.error(f"❌ Error: {e}")


def main():
    """Main dashboard"""
    
    cc = CommandCenter()
    
    # Header
    st.title("🏰 CITADEL COMMAND CENTER")
    st.markdown("**Q.G.T.N.L. Command Citadel - Central Control Interface**")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("🎮 Command Controls")
        
        if st.button("🚀 WAKE CITADEL", use_container_width=True, type="primary"):
            cc.trigger_awakening()
            st.rerun()
        
        st.markdown("---")
        
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
        
        st.markdown("---")
        
        st.header("📊 Quick Stats")
        
        # Load data for stats
        deployment = cc.load_deployment_results()
        if deployment:
            summary = deployment.get("summary", {})
            st.metric("Total Workers", summary.get("total_workers", 0))
            st.metric("Success Rate", summary.get("success_rate", "0%"))
            st.metric("Active Workers", summary.get("successful", 0))
        else:
            st.info("No deployment data yet")
        
        st.markdown("---")
        st.caption(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 Overview",
        "👥 Workers",
        "🗺️ Districts",
        "📊 Discoveries",
        "📝 Logs"
    ])
    
    with tab1:
        st.header("🎯 System Overview")
        
        # Deployment status
        st.subheader("🚀 Latest Deployment")
        deployment = cc.load_deployment_results()
        
        if deployment:
            timestamp = deployment.get("timestamp", "Unknown")
            st.info(f"**Last Deployment:** {timestamp}")
            
            summary = deployment.get("summary", {})
            
            # Metrics row
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Workers", summary.get("total_workers", 0))
            with col2:
                st.metric("✅ Successful", summary.get("successful", 0))
            with col3:
                st.metric("❌ Failed", summary.get("failed", 0))
            with col4:
                st.metric("Success Rate", summary.get("success_rate", "0%"))
            
            # Status breakdown by group
            st.subheader("📦 Worker Groups")
            results = deployment.get("results", {})
            
            for group_name, group_results in results.items():
                with st.expander(f"**{group_name.upper()}** ({len(group_results)} workers)"):
                    for result in group_results:
                        status = result.get("status", "unknown")
                        worker = result.get("worker", "Unknown")
                        
                        if status == "success":
                            st.success(f"✅ {worker}")
                        elif status == "failed" or status == "error":
                            st.error(f"❌ {worker}")
                            if "error" in result:
                                st.code(result["error"][-200:])
                        elif status == "timeout":
                            st.warning(f"⏱️ {worker} (timeout)")
                        else:
                            st.info(f"⚠️ {worker} ({status})")
        else:
            st.warning("⚠️ No deployment data available. Click 'WAKE CITADEL' to start!")
    
    with tab2:
        st.header("👥 Worker Status")
        
        worker_status = cc.load_worker_status()
        
        if worker_status:
            # Convert to dataframe
            workers_list = []
            for category, workers in worker_status.items():
                if isinstance(workers, list):
                    for worker in workers:
                        workers_list.append({
                            "Category": category,
                            "Worker": worker.get("worker_name", "Unknown"),
                            "Status": worker.get("status", "unknown"),
                            "Last Run": worker.get("last_run", "Never")
                        })
            
            if workers_list:
                df = pd.DataFrame(workers_list)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No worker status data available")
        else:
            st.info("No worker status data available")
        
        # Worker registry
        st.subheader("📋 Worker Registry")
        st.markdown("""
        **Available Workers:**
        
        🔍 **Scouts** (Discovery):
        - Domain Scout
        - Spiritual Network Mapper
        - Repo Scout
        - Trending Scout
        
        🐕 **Hounds** (Collection):
        - District Harvester
        - Laptop Scanner
        - Trading Garage Collector
        
        🛡️ **Sentinels** (Security & Monitoring):
        - Health Monitor
        - Sentinel Coordinator
        - TIA Coordinator
        
        👻 **Wraiths** (Maintenance):
        - Vacuum Cleaner
        
        🎯 **Coordinators** (Orchestration):
        - Master Pipeline Orchestrator
        - Sync Orchestrator
        - HarvestMoon Coordinator
        - Librarian Consolidator
        
        🔄 **Ingestors** (Processing):
        - RAG Ingest
        - Wake Up TIA
        """)
    
    with tab3:
        st.header("🗺️ Districts Status")
        
        districts = cc.load_districts()
        
        if districts:
            # Active districts
            active = districts.get("active_districts", [])
            st.metric("Active Districts", len(active))
            
            # District list
            for district in active:
                with st.expander(f"**{district.get('id', 'Unknown')}** - {district.get('name', 'Unknown')}"):
                    st.write(f"**Path:** `{district.get('path', 'Unknown')}`")
                    st.write(f"**Pillar:** {district.get('pillar', 'Unknown')}")
                    st.write(f"**Purpose:** {district.get('purpose', 'Unknown')}")
                    
                    # Artifacts
                    artifacts = district.get("artifacts", {})
                    st.write(f"**Artifacts Required:** {', '.join(artifacts.get('required', []))}")
        else:
            st.info("No district data available")
    
    with tab4:
        st.header("📊 Discoveries")
        
        # Domain discoveries
        st.subheader("🌐 Domain Discoveries")
        domains_file = DISCOVERIES_PATH / "domains.json"
        if domains_file.exists():
            with open(domains_file, 'r') as f:
                domains = json.load(f)
                stats = domains.get("statistics", {})
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Scanned", stats.get("total_scanned", 0))
                with col2:
                    st.metric("Available Found", stats.get("available_found", 0))
                with col3:
                    st.metric("High Value", stats.get("high_value", 0))
                
                # Show some domains
                spiritual = domains.get("spiritual_domains", [])
                if spiritual:
                    with st.expander(f"Spiritual Domains ({len(spiritual)})"):
                        for domain in spiritual[-10:]:
                            st.text(f"• {domain.get('domain', 'Unknown')}")
        else:
            st.info("No domain discoveries yet")
        
        # Spiritual networks
        st.subheader("✨ Spiritual Networks")
        spiritual_file = DISCOVERIES_PATH / "spiritual_networks.json"
        if spiritual_file.exists():
            with open(spiritual_file, 'r') as f:
                networks = json.load(f)
                stats = networks.get("statistics", {})
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Communities", stats.get("total_communities", 0))
                with col2:
                    st.metric("Platforms", stats.get("total_platforms", 0))
                with col3:
                    st.metric("Resources", stats.get("total_resources", 0))
                
                # Show communities
                reddit = networks.get("communities", {}).get("reddit", [])
                if reddit:
                    with st.expander(f"Reddit Communities ({len(reddit)})"):
                        for community in reddit:
                            st.text(f"• {community.get('name', 'Unknown')} - {community.get('members', 'Unknown')} members")
        else:
            st.info("No spiritual network discoveries yet")
    
    with tab5:
        st.header("📝 System Logs")
        
        # Log file selector
        log_files = list(LOGS_PATH.glob("*.log")) if LOGS_PATH.exists() else []
        
        if log_files:
            selected_log = st.selectbox(
                "Select Log File:",
                [f.name for f in log_files]
            )
            
            if selected_log:
                lines = st.slider("Number of lines", 10, 200, 50)
                recent_logs = cc.get_recent_logs(selected_log, lines)
                
                st.code("\n".join(recent_logs), language="log")
        else:
            st.info("No log files found")
    
    # Footer
    st.markdown("---")
    st.caption("🏰 Citadel Command Center v26.0 | Citadel Architect | Q.G.T.N.L. Command Citadel")


if __name__ == "__main__":
    main()
