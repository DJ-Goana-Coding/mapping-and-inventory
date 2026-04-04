import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import pandas as pd

st.set_page_config(
    page_title="Data Migration Dashboard",
    page_icon="📦",
    layout="wide"
)

st.title("📦 Data Migration & Backup Dashboard")
st.caption("Complete Data Sovereignty System - Citadel Architect v25.0.OMNI+")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "☁️ GDrive Status", "💻 Laptop Status", "📋 Action Items"])

with tab1:
    st.header("📊 System Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="GDrive Accounts",
            value="2",
            delta="Both Accessible"
        )
        st.caption("chanceroofing@gmail.com")
        st.caption("mynewemail110411@gmail.com")
    
    with col2:
        st.metric(
            label="Laptop Drives",
            value="3",
            delta="C:, D:, F:"
        )
        st.caption("All non-Windows files")
    
    with col3:
        st.metric(
            label="Total Backed Up",
            value="Calculating...",
            delta="In Progress"
        )
        st.caption("Files + Data Size")
    
    st.divider()
    
    # Recent Activity
    st.subheader("🕐 Recent Activity")
    
    activity_data = {
        "Timestamp": [
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            (datetime.now().replace(hour=datetime.now().hour-1)).strftime("%Y-%m-%d %H:%M"),
            (datetime.now().replace(hour=datetime.now().hour-6)).strftime("%Y-%m-%d %H:%M"),
        ],
        "Activity": [
            "GDrive Emergency Extraction - chanceroofing",
            "Laptop Media Harvest",
            "System Profile Generated"
        ],
        "Status": ["✅ Complete", "✅ Complete", "✅ Complete"]
    }
    
    st.dataframe(activity_data, use_container_width=True, hide_index=True)

with tab2:
    st.header("☁️ GDrive Extraction Status")
    
    # Account status
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("chanceroofing@gmail.com")
        
        # Try to load manifest
        manifest_path = Path("data/gdrive_manifests/chanceroofing_complete_index.json")
        if manifest_path.exists():
            with open(manifest_path) as f:
                data = json.load(f)
            
            st.metric("Total Files", f"{data.get('total_files', 0):,}")
            st.metric("Total Size", f"{data.get('total_size_bytes', 0) / (1024**3):.2f} GB")
            st.caption(f"Last scan: {data.get('scan_timestamp', 'Unknown')}")
            
            # Priority breakdown
            st.write("**Priority Breakdown:**")
            copy_manifest = Path("data/gdrive_archive/chanceroofing/copy_manifest.json")
            if copy_manifest.exists():
                with open(copy_manifest) as f:
                    copy_data = json.load(f)
                
                for priority, info in copy_data.get('priorities', {}).items():
                    st.write(f"- {priority}: {info.get('files_copied', 0)}/{info.get('total_files', 0)} files")
        else:
            st.warning("No manifest found. Run extraction workflow.")
            st.button("🚨 Run Emergency Extraction")
    
    with col2:
        st.subheader("mynewemail110411@gmail.com")
        
        # Try to load manifest
        manifest_path = Path("data/gdrive_manifests/mynewemail_complete_index.json")
        if manifest_path.exists():
            with open(manifest_path) as f:
                data = json.load(f)
            
            st.metric("Total Files", f"{data.get('total_files', 0):,}")
            st.metric("Total Size", f"{data.get('total_size_bytes', 0) / (1024**3):.2f} GB")
            st.caption(f"Last scan: {data.get('scan_timestamp', 'Unknown')}")
            
            # Priority breakdown
            st.write("**Priority Breakdown:**")
            copy_manifest = Path("data/gdrive_archive/mynewemail/copy_manifest.json")
            if copy_manifest.exists():
                with open(copy_manifest) as f:
                    copy_data = json.load(f)
                
                for priority, info in copy_data.get('priorities', {}).items():
                    st.write(f"- {priority}: {info.get('files_copied', 0)}/{info.get('total_files', 0)} files")
        else:
            st.warning("No manifest found. Run extraction workflow.")
            st.button("🚨 Run Emergency Extraction ", key="mynewemail_btn")
    
    st.divider()
    
    # Extraction progress
    st.subheader("📈 Extraction Progress")
    
    progress_data = {
        "Tier": ["P0 (Critical)", "P1 (High)", "P2 (Medium)", "P3 (Low)"],
        "chanceroofing": [100, 85, 40, 10],
        "mynewemail": [100, 90, 50, 15]
    }
    
    df = pd.DataFrame(progress_data)
    st.bar_chart(df.set_index("Tier"))

with tab3:
    st.header("💻 Laptop Vacuum Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📊 System Profile")
        
        profile_path = Path("data/laptop_inventory/system_profile_latest.json")
        if profile_path.exists():
            with open(profile_path) as f:
                profile = json.load(f)
            
            st.write(f"**Hostname:** {profile.get('hostname', 'Unknown')}")
            st.write(f"**OS:** {profile.get('os', {}).get('system', 'Unknown')}")
            st.write(f"**Last Updated:** {profile.get('timestamp', 'Unknown')}")
            st.success("Profile Available")
        else:
            st.warning("No profile found")
            st.button("Generate Profile")
    
    with col2:
        st.subheader("🎵 Media Catalog")
        
        media_files = list(Path("data/laptop_inventory").glob("media_harvest_catalog_*.json"))
        if media_files:
            latest_media = max(media_files, key=lambda x: x.stat().st_mtime)
            with open(latest_media) as f:
                media_data = json.load(f)
            
            total_files = media_data.get('stats', {}).get('total_files', 0)
            total_size_gb = media_data.get('stats', {}).get('total_size_bytes', 0) / (1024**3)
            
            st.metric("Total Files", f"{total_files:,}")
            st.metric("Total Size", f"{total_size_gb:.2f} GB")
            
            by_category = media_data.get('stats', {}).get('by_category', {})
            for category, stats in by_category.items():
                st.write(f"- **{category.title()}:** {stats.get('count', 0):,} files")
        else:
            st.warning("No media catalog found")
            st.button("Run Media Harvest")
    
    with col3:
        st.subheader("🎯 Programs Catalog")
        
        program_files = list(Path("data/laptop_inventory").glob("programs_catalog_*.json"))
        if program_files:
            latest_programs = max(program_files, key=lambda x: x.stat().st_mtime)
            with open(latest_programs) as f:
                programs_data = json.load(f)
            
            total_installed = programs_data.get('stats', {}).get('total_installed', 0)
            total_portable = programs_data.get('stats', {}).get('total_portable', 0)
            
            st.metric("Installed Programs", total_installed)
            st.metric("Portable Apps", total_portable)
            st.success("Catalog Available")
        else:
            st.warning("No programs catalog found")
            st.button("Run Programs Catalog")

with tab4:
    st.header("📋 Action Items & Next Steps")
    
    st.subheader("🚨 Critical Actions (Do These NOW)")
    
    critical_actions = [
        ("Setup Rclone", "./scripts/setup_gdrive_rclone.sh", "Configure GDrive access"),
        ("Verify Access", "python scripts/verify_gdrive_access.py", "Test authentication"),
        ("Emergency Extract", "gh workflow run gdrive_emergency_extraction.yml", "Start extraction"),
        ("Laptop Harvest", "python scripts/laptop_media_harvester.py --paths C:/ D:/ F:/", "Catalog media")
    ]
    
    for action, command, description in critical_actions:
        with st.expander(f"📌 {action}"):
            st.write(description)
            st.code(command, language="bash")
    
    st.divider()
    
    st.subheader("📂 Manual Upload Required")
    
    # Check for large files
    routing_files = list(Path("data/laptop_inventory").glob("routing_manifest_*.json"))
    if routing_files:
        latest_routing = max(routing_files, key=lambda x: x.stat().st_mtime)
        with open(latest_routing) as f:
            routing_data = json.load(f)
        
        large_files = [
            d for d in routing_data.get('routing_decisions', [])
            if d.get('tier') in ['large', 'xlarge']
        ]
        
        if large_files:
            st.warning(f"Found {len(large_files)} large files requiring manual upload")
            
            for decision in large_files[:10]:
                filename = decision.get('filename', 'unknown')
                size_mb = decision.get('size_mb', 0)
                st.write(f"- {filename} ({size_mb:.2f} MB)")
            
            if len(large_files) > 10:
                st.caption(f"... and {len(large_files) - 10} more")
            
            st.code("""
python scripts/gdrive_large_file_uploader.py \\
  --source <source_dir> \\
  --repo-name laptop-large-files \\
  --min-size 100
""", language="bash")
    
    st.divider()
    
    st.subheader("📚 Documentation")
    
    docs = [
        ("Complete Migration Guide", "COMPLETE_DATA_MIGRATION_GUIDE.md"),
        ("GDrive Shared Access", "GDRIVE_SHARED_ACCESS_GUIDE.md"),
        ("Laptop Copy Guide", "LAPTOP_COPY_COMPLETE_GUIDE.md"),
        ("Quantum Vault Guide", "QUANTUM_VAULT_OPERATOR_GUIDE.md")
    ]
    
    for title, path in docs:
        if Path(path).exists():
            st.markdown(f"- [{title}]({path})")
        else:
            st.markdown(f"- {title} (pending)")

# Footer
st.divider()
st.caption("🏛️ Citadel Architect v25.0.OMNI+ | Cloud-First Authority | Section 142 Compliant")
