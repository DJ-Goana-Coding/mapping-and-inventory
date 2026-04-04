#!/usr/bin/env python3
"""
🎯 COMMANDER WEBSITE DASHBOARD v1.0
Central status dashboard showing all systems operational status.

Authority: Citadel Architect v25.0.OMNI++
Role: Commander Interface
"""

import streamlit as st
import json
import os
from pathlib import Path
from datetime import datetime
import pandas as pd

st.set_page_config(
    page_title="Commander Dashboard | Citadel Mesh",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Paths
BASE_PATH = Path("/home/runner/work/mapping-and-inventory/mapping-and-inventory")
DISTRICTS_PATH = BASE_PATH / "Districts"
DATA_PATH = BASE_PATH / "data"
MONITORING_PATH = DATA_PATH / "monitoring"


def load_json(file_path):
    """Load JSON file safely."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except:
        return {}


def check_district_status(district_name):
    """Check if district has all required artifacts."""
    district_path = DISTRICTS_PATH / district_name
    artifacts = ["TREE.md", "INVENTORY.json", "SCAFFOLD.md", "BIBLE.md"]
    
    status = {
        "name": district_name,
        "exists": district_path.exists(),
        "artifacts": {},
        "health": 100.0
    }
    
    if not district_path.exists():
        status["health"] = 0.0
        return status
    
    missing_count = 0
    for artifact in artifacts:
        exists = (district_path / artifact).exists()
        status["artifacts"][artifact] = exists
        if not exists:
            missing_count += 1
    
    status["health"] = ((len(artifacts) - missing_count) / len(artifacts)) * 100
    return status


def main():
    """Main dashboard."""
    
    # Header
    st.title("🏛️ CITADEL MESH COMMANDER DASHBOARD")
    st.markdown("**Central Command & Control Interface**")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("🎯 Quick Actions")
        if st.button("🔄 Refresh All Data"):
            st.rerun()
        
        if st.button("🧪 Run All Tests"):
            st.info("Triggering comprehensive test suite...")
            os.system("python /home/runner/work/mapping-and-inventory/mapping-and-inventory/scripts/comprehensive_test_runner.py &")
        
        if st.button("🧹 Run Sweep"):
            st.info("Triggering omnidimensional sweep...")
            os.system("python /home/runner/work/mapping-and-inventory/mapping-and-inventory/scripts/omnidimensional_sweep.py &")
        
        st.markdown("---")
        st.markdown("### 📊 System Time")
        st.markdown(f"**{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC**")
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏛️ Districts",
        "📊 Test Results",
        "🧹 Security Sweep",
        "📦 Artifacts",
        "🚀 Workflows"
    ])
    
    # Tab 1: Districts Overview
    with tab1:
        st.header("🏛️ Districts Status")
        
        districts = [
            "D01_COMMAND_INPUT",
            "D02_TIA_VAULT",
            "D03_VORTEX_ENGINE",
            "D04_OMEGA_TRADER",
            "D06_RANDOM_FUTURES",
            "D07_ARCHIVE_SCROLLS",
            "D09_MEDIA_CODING",
            "D11_PERSONA_MODULES",
            "D12_ZENITH_VIEW",
        ]
        
        # Check all districts
        district_statuses = []
        for district in districts:
            status = check_district_status(district)
            district_statuses.append(status)
        
        # Display grid
        cols = st.columns(3)
        for idx, status in enumerate(district_statuses):
            col = cols[idx % 3]
            with col:
                health = status["health"]
                if health == 100:
                    health_icon = "✅"
                    health_color = "green"
                elif health >= 75:
                    health_icon = "⚠️"
                    health_color = "orange"
                else:
                    health_icon = "❌"
                    health_color = "red"
                
                st.markdown(f"### {health_icon} {status['name']}")
                st.progress(health / 100.0)
                st.markdown(f"**Health: {health}%**")
                
                # Artifact details
                with st.expander("Artifacts"):
                    for artifact, exists in status["artifacts"].items():
                        icon = "✅" if exists else "❌"
                        st.markdown(f"{icon} {artifact}")
        
        # Overall health
        st.markdown("---")
        overall_health = sum(s["health"] for s in district_statuses) / len(district_statuses)
        st.metric("Overall District Health", f"{overall_health:.1f}%")
    
    # Tab 2: Test Results
    with tab2:
        st.header("🧪 Test Results")
        
        test_results_path = MONITORING_PATH / "test_results.json"
        if test_results_path.exists():
            test_results = load_json(test_results_path)
            
            col1, col2, col3, col4 = st.columns(4)
            summary = test_results.get("summary", {})
            
            col1.metric("Total Tests", summary.get("total_tests", 0))
            col2.metric("✅ Passed", summary.get("passed", 0))
            col3.metric("❌ Failed", summary.get("failed", 0))
            col4.metric("⏭️ Skipped", summary.get("skipped", 0))
            
            st.markdown("---")
            st.metric("Success Rate", f"{summary.get('success_rate', 0)}%")
            
            # District details
            st.subheader("District Test Details")
            districts_data = test_results.get("districts", {})
            
            for district, results in districts_data.items():
                with st.expander(f"🏛️ {district}"):
                    cols = st.columns(3)
                    
                    unit_status = results["unit_tests"]["status"]
                    integration_status = results["integration_tests"]["status"]
                    stress_status = results["stress_tests"]["status"]
                    
                    cols[0].markdown(f"**Unit Tests:** {unit_status}")
                    cols[1].markdown(f"**Integration:** {integration_status}")
                    cols[2].markdown(f"**Stress:** {stress_status}")
        else:
            st.info("No test results available. Run tests to generate data.")
            if st.button("▶️ Run Tests Now"):
                os.system("python /home/runner/work/mapping-and-inventory/mapping-and-inventory/scripts/comprehensive_test_runner.py &")
                st.success("Tests started in background...")
    
    # Tab 3: Security Sweep
    with tab3:
        st.header("🧹 Security Sweep Results")
        
        sweep_path = MONITORING_PATH / "omnidimensional_sweep.json"
        if sweep_path.exists():
            sweep_results = load_json(sweep_path)
            
            col1, col2, col3, col4 = st.columns(4)
            summary = sweep_results.get("summary", {})
            
            col1.metric("🦠 Infected Files", summary.get("infected_files", 0))
            col2.metric("⚠️ Suspicious", summary.get("suspicious_files", 0))
            col3.metric("📋 Duplicates", summary.get("total_duplicates", 0))
            col4.metric("❌ Missing", summary.get("missing_artifacts", 0))
            
            st.markdown("---")
            st.subheader("🎯 Recommendations")
            recommendations = sweep_results.get("recommendations", [])
            for rec in recommendations:
                if "CRITICAL" in rec:
                    st.error(rec)
                elif "WARNING" in rec:
                    st.warning(rec)
                elif "ACTION" in rec:
                    st.info(rec)
                else:
                    st.success(rec)
        else:
            st.info("No sweep results available. Run sweep to generate data.")
            if st.button("▶️ Run Sweep Now"):
                os.system("python /home/runner/work/mapping-and-inventory/mapping-and-inventory/scripts/omnidimensional_sweep.py &")
                st.success("Sweep started in background...")
    
    # Tab 4: Artifacts
    with tab4:
        st.header("📦 Artifact Status")
        
        st.markdown("### District Artifacts")
        
        # Check all districts for artifacts
        artifact_data = []
        for district in districts:
            district_path = DISTRICTS_PATH / district
            if district_path.exists():
                row = {"District": district}
                for artifact in ["TREE.md", "INVENTORY.json", "SCAFFOLD.md", "BIBLE.md"]:
                    row[artifact] = "✅" if (district_path / artifact).exists() else "❌"
                artifact_data.append(row)
        
        if artifact_data:
            df = pd.DataFrame(artifact_data)
            st.dataframe(df, use_container_width=True)
    
    # Tab 5: Workflows
    with tab5:
        st.header("🚀 GitHub Actions Workflows")
        
        workflows_path = BASE_PATH / ".github" / "workflows"
        if workflows_path.exists():
            workflow_files = list(workflows_path.glob("*.yml"))
            st.metric("Total Workflows", len(workflow_files))
            
            st.markdown("### Active Workflows")
            for workflow in sorted(workflow_files)[:20]:
                st.markdown(f"- `{workflow.name}`")
        else:
            st.warning("Workflows directory not found")
    
    # Footer
    st.markdown("---")
    st.markdown("**🏛️ Citadel Architect v25.0.OMNI++ | Sovereign Systems Overseer**")


if __name__ == "__main__":
    main()
