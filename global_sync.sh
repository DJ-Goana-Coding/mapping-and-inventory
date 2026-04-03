#!/bin/bash
###############################################################################
# GLOBAL WELD: Multi-Repository Synchronization Engine
# Citadel Architect v25.0.OMNI+ - Sovereign Systems Overseer
#
# Purpose: Sync all DJ-Goana-Coding repos, extract artifacts, aggregate
#          inventory, and push to GitHub + HuggingFace Space
#
# Authority: Cloud Hubs > GitHub > GDrive Metadata > Local Nodes
# Protocol: Pull-Over-Push (L4 Vacuum ingestion priority)
###############################################################################

set -e  # Exit on error

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

GITHUB_ORG="DJ-Goana-Coding"
HF_ORG="DJ-Goanna-Coding"  # Double-N Rift
HF_SPACE="Mapping-and-Inventory"
WORKSPACE="/tmp/citadel_sync_workspace"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SYNC_REPORT="sync_report_${TIMESTAMP}.txt"

# Credential detection
GITHUB_TOKEN="${GITHUB_TOKEN:-}"
HF_TOKEN="${HF_TOKEN:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ═══════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

log() {
    echo -e "${CYAN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

banner() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# ═══════════════════════════════════════════════════════════════════════════
# INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════

initialize() {
    banner "🏛️ CITADEL ARCHITECT: GLOBAL WELD v25.0.OMNI+"
    
    log "Initializing sync workspace..."
    
    # Create workspace
    mkdir -p "${WORKSPACE}"
    mkdir -p "${WORKSPACE}/repos"
    mkdir -p "${WORKSPACE}/artifacts"
    mkdir -p "${WORKSPACE}/aggregated"
    
    # Initialize report
    cat > "${WORKSPACE}/${SYNC_REPORT}" << EOF
═══════════════════════════════════════════════════════════════════════════
CITADEL OMEGA - GLOBAL WELD SYNC REPORT
Generated: $(date +'%Y-%m-%d %H:%M:%S UTC')
Operator: ${USER:-github-actions}
Workspace: ${WORKSPACE}
═══════════════════════════════════════════════════════════════════════════

EOF
    
    success "Workspace initialized: ${WORKSPACE}"
}

# ═══════════════════════════════════════════════════════════════════════════
# REPOSITORY DISCOVERY
# ═══════════════════════════════════════════════════════════════════════════

discover_repos() {
    banner "🔍 Discovering DJ-Goana-Coding Repositories"
    
    local repos_file="${WORKSPACE}/discovered_repos.txt"
    
    if [ -n "${GITHUB_TOKEN}" ]; then
        log "Using GitHub API for repository discovery..."
        
        # Fetch all repos from the organization
        curl -s -H "Authorization: token ${GITHUB_TOKEN}" \
            "https://api.github.com/orgs/${GITHUB_ORG}/repos?per_page=100" \
            | grep -o '"full_name": "[^"]*"' \
            | cut -d'"' -f4 > "${repos_file}" 2>/dev/null || true
    fi
    
    # Fallback: Known canonical repositories
    if [ ! -s "${repos_file}" ]; then
        warn "GitHub API unavailable. Using canonical repository list."
        
        cat > "${repos_file}" << 'EOF'
DJ-Goana-Coding/mapping-and-inventory
DJ-Goana-Coding/ARK_CORE
DJ-Goana-Coding/TIA-ARCHITECT-CORE
DJ-Goana-Coding/tias-citadel
DJ-Goana-Coding/tias-sentinel-scout-swarm-2
DJ-Goana-Coding/goanna_coding
DJ-Goana-Coding/Vortex_Web3
DJ-Goana-Coding/Genesis-Research-Rack
DJ-Goana-Coding/Citadel_Genetics
EOF
    fi
    
    local repo_count=$(wc -l < "${repos_file}")
    success "Discovered ${repo_count} repositories"
    
    # Log to report
    echo "" >> "${WORKSPACE}/${SYNC_REPORT}"
    echo "DISCOVERED REPOSITORIES: ${repo_count}" >> "${WORKSPACE}/${SYNC_REPORT}"
    echo "─────────────────────────────────────────────────────────────────" >> "${WORKSPACE}/${SYNC_REPORT}"
    cat "${repos_file}" >> "${WORKSPACE}/${SYNC_REPORT}"
    echo "" >> "${WORKSPACE}/${SYNC_REPORT}"
    
    echo "${repos_file}"
}

# ═══════════════════════════════════════════════════════════════════════════
# REPOSITORY CLONING
# ═══════════════════════════════════════════════════════════════════════════

clone_repos() {
    local repos_file=$1
    banner "📥 Cloning/Pulling Repositories"
    
    local success_count=0
    local fail_count=0
    
    while IFS= read -r repo_full_name; do
        local repo_name=$(basename "${repo_full_name}")
        local repo_dir="${WORKSPACE}/repos/${repo_name}"
        
        log "Processing: ${repo_name}..."
        
        # Skip if already exists and update
        if [ -d "${repo_dir}" ]; then
            log "  Repository exists, pulling latest..."
            (cd "${repo_dir}" && git pull origin main 2>&1) || warn "  Pull failed for ${repo_name}"
        else
            # Clone repository
            local clone_url="https://github.com/${repo_full_name}.git"
            
            if [ -n "${GITHUB_TOKEN}" ]; then
                clone_url="https://${GITHUB_TOKEN}@github.com/${repo_full_name}.git"
            fi
            
            if git clone --depth 1 "${clone_url}" "${repo_dir}" 2>&1 | tee -a "${WORKSPACE}/${SYNC_REPORT}"; then
                success_count=$((success_count + 1))
                success "  Cloned: ${repo_name}"
            else
                fail_count=$((fail_count + 1))
                error "  Failed: ${repo_name}"
                echo "FAILED: ${repo_name}" >> "${WORKSPACE}/${SYNC_REPORT}"
            fi
        fi
        
    done < "${repos_file}"
    
    echo "" >> "${WORKSPACE}/${SYNC_REPORT}"
    echo "CLONE SUMMARY:" >> "${WORKSPACE}/${SYNC_REPORT}"
    echo "  Success: ${success_count}" >> "${WORKSPACE}/${SYNC_REPORT}"
    echo "  Failed: ${fail_count}" >> "${WORKSPACE}/${SYNC_REPORT}"
    echo "" >> "${WORKSPACE}/${SYNC_REPORT}"
    
    success "Clone phase complete: ${success_count} succeeded, ${fail_count} failed"
}

# ═══════════════════════════════════════════════════════════════════════════
# ARTIFACT EXTRACTION
# ═══════════════════════════════════════════════════════════════════════════

extract_artifacts() {
    banner "📦 Extracting District Artifacts"
    
    local artifacts_dir="${WORKSPACE}/artifacts"
    local total_artifacts=0
    
    # Search for TREE.md, INVENTORY.json, SCAFFOLD.md in all repos
    for repo_dir in "${WORKSPACE}"/repos/*; do
        if [ ! -d "${repo_dir}" ]; then continue; fi
        
        local repo_name=$(basename "${repo_dir}")
        log "Scanning: ${repo_name}..."
        
        # Find all District artifacts
        for artifact_type in "TREE.md" "INVENTORY.json" "SCAFFOLD.md"; do
            find "${repo_dir}" -name "${artifact_type}" -type f 2>/dev/null | while read -r artifact_path; do
                # Create artifact directory structure
                local rel_path=$(realpath --relative-to="${repo_dir}" "${artifact_path}")
                local dest_dir="${artifacts_dir}/${repo_name}/$(dirname "${rel_path}")"
                
                mkdir -p "${dest_dir}"
                cp "${artifact_path}" "${dest_dir}/"
                
                total_artifacts=$((total_artifacts + 1))
                log "  Found: ${rel_path}"
            done
        done
    done
    
    echo "" >> "${WORKSPACE}/${SYNC_REPORT}"
    echo "ARTIFACT EXTRACTION:" >> "${WORKSPACE}/${SYNC_REPORT}"
    echo "  Total artifacts extracted: ${total_artifacts}" >> "${WORKSPACE}/${SYNC_REPORT}"
    echo "" >> "${WORKSPACE}/${SYNC_REPORT}"
    
    success "Extracted ${total_artifacts} artifacts"
}

# ═══════════════════════════════════════════════════════════════════════════
# INVENTORY AGGREGATION
# ═══════════════════════════════════════════════════════════════════════════

aggregate_inventory() {
    banner "🔮 Aggregating Master Inventory"
    
    log "Running Python aggregation script..."
    
    # Call Python script to merge all inventories
    python3 << 'PYTHON_SCRIPT'
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

workspace = os.environ.get('WORKSPACE', '/tmp/citadel_sync_workspace')
artifacts_dir = Path(workspace) / 'artifacts'
aggregated_dir = Path(workspace) / 'aggregated'

master_inventory = []
master_map_lines = []
stats = {
    'total_repos': 0,
    'total_districts': 0,
    'total_files': 0,
    'timestamp': datetime.now(timezone.utc).isoformat()
}

# Process all INVENTORY.json files
for inventory_file in artifacts_dir.rglob('INVENTORY.json'):
    try:
        with open(inventory_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        repo_name = inventory_file.parts[len(artifacts_dir.parts)]
        district_path = inventory_file.parent.relative_to(artifacts_dir / repo_name)
        
        # Add repository context
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    item['_source_repo'] = repo_name
                    item['_source_district'] = str(district_path)
                    master_inventory.append(item)
        elif isinstance(data, dict):
            data['_source_repo'] = repo_name
            data['_source_district'] = str(district_path)
            master_inventory.append(data)
            
        stats['total_districts'] += 1
        
    except Exception as e:
        print(f"Warning: Failed to process {inventory_file}: {e}", file=sys.stderr)

# Process all TREE.md files for intelligence map
for tree_file in artifacts_dir.rglob('TREE.md'):
    try:
        with open(tree_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        repo_name = tree_file.parts[len(artifacts_dir.parts)]
        district_path = tree_file.parent.relative_to(artifacts_dir / repo_name)
        
        master_map_lines.append(f"\n{'='*70}\n")
        master_map_lines.append(f"REPO: {repo_name}\n")
        master_map_lines.append(f"DISTRICT: {district_path}\n")
        master_map_lines.append(f"{'='*70}\n\n")
        master_map_lines.append(content)
        
    except Exception as e:
        print(f"Warning: Failed to process {tree_file}: {e}", file=sys.stderr)

stats['total_repos'] = len(set(item.get('_source_repo', '') for item in master_inventory))
stats['total_files'] = len(master_inventory)

# Write aggregated master_inventory.json
aggregated_dir.mkdir(exist_ok=True, parents=True)
with open(aggregated_dir / 'master_inventory.json', 'w', encoding='utf-8') as f:
    json.dump(master_inventory, f, indent=2, ensure_ascii=False)

# Write aggregated master_intelligence_map.txt
with open(aggregated_dir / 'master_intelligence_map.txt', 'w', encoding='utf-8') as f:
    f.write(f"CITADEL OMEGA - MASTER INTELLIGENCE MAP\n")
    f.write(f"Generated: {stats['timestamp']}\n")
    f.write(f"Total Repos: {stats['total_repos']}\n")
    f.write(f"Total Districts: {stats['total_districts']}\n")
    f.write(f"Total Files: {stats['total_files']}\n")
    f.write(''.join(master_map_lines))

# Write stats
with open(aggregated_dir / 'sync_stats.json', 'w', encoding='utf-8') as f:
    json.dump(stats, f, indent=2)

print(f"✅ Aggregation complete:")
print(f"   - Repos: {stats['total_repos']}")
print(f"   - Districts: {stats['total_districts']}")
print(f"   - Files: {stats['total_files']}")
PYTHON_SCRIPT
    
    success "Master inventory aggregated"
}

# ═══════════════════════════════════════════════════════════════════════════
# COMMIT TO MAPPING-AND-INVENTORY
# ═══════════════════════════════════════════════════════════════════════════

commit_to_repo() {
    banner "💾 Committing to mapping-and-inventory"
    
    local repo_root=$(pwd)
    
    # Copy aggregated files to repository
    log "Copying aggregated files..."
    cp "${WORKSPACE}/aggregated/master_inventory.json" "${repo_root}/" 2>/dev/null || warn "No master_inventory.json to copy"
    cp "${WORKSPACE}/aggregated/master_intelligence_map.txt" "${repo_root}/" 2>/dev/null || warn "No master_intelligence_map.txt to copy"
    cp "${WORKSPACE}/${SYNC_REPORT}" "${repo_root}/sync_reports/" 2>/dev/null || mkdir -p "${repo_root}/sync_reports" && cp "${WORKSPACE}/${SYNC_REPORT}" "${repo_root}/sync_reports/"
    
    # Git status
    log "Checking git status..."
    git status --short
    
    # Add changes
    log "Staging changes..."
    git add master_inventory.json master_intelligence_map.txt sync_reports/ 2>/dev/null || true
    
    # Check if there are changes to commit
    if git diff --cached --quiet; then
        warn "No changes to commit"
        return 0
    fi
    
    # Commit
    log "Committing changes..."
    git commit -m "🦎 Global Weld: Sync $(date +'%Y-%m-%d %H:%M:%S')

- Synced all DJ-Goana-Coding repositories
- Aggregated District artifacts (TREE.md, INVENTORY.json, SCAFFOLD.md)
- Updated master_inventory.json and master_intelligence_map.txt
- Generated sync report: ${SYNC_REPORT}

Citadel Architect v25.0.OMNI+ - Stainless Compliance"
    
    success "Changes committed to local repository"
}

# ═══════════════════════════════════════════════════════════════════════════
# PUSH TO GITHUB
# ═══════════════════════════════════════════════════════════════════════════

push_to_github() {
    banner "⬆️  Pushing to GitHub"
    
    log "Pushing to origin..."
    
    if git push origin main; then
        success "Successfully pushed to GitHub"
    else
        error "Failed to push to GitHub"
        return 1
    fi
}

# ═══════════════════════════════════════════════════════════════════════════
# PUSH TO HUGGINGFACE
# ═══════════════════════════════════════════════════════════════════════════

push_to_huggingface() {
    banner "🤗 Pushing to HuggingFace Space"
    
    if [ -z "${HF_TOKEN}" ]; then
        warn "HF_TOKEN not set. Skipping HuggingFace push."
        warn "Set HF_TOKEN environment variable to enable HF sync."
        return 0
    fi
    
    log "Configuring HuggingFace remote..."
    
    # Configure git credentials
    git config --global credential.helper store
    echo "https://${HF_ORG}:${HF_TOKEN}@huggingface.co" >> ~/.git-credentials
    
    # Add or update HF remote
    if git remote get-url hf 2>/dev/null; then
        git remote set-url hf "https://huggingface.co/spaces/${HF_ORG}/${HF_SPACE}"
    else
        git remote add hf "https://huggingface.co/spaces/${HF_ORG}/${HF_SPACE}"
    fi
    
    log "Pushing to HuggingFace Space..."
    
    if git push hf main; then
        success "Successfully pushed to HuggingFace Space"
    else
        error "Failed to push to HuggingFace"
        return 1
    fi
}

# ═══════════════════════════════════════════════════════════════════════════
# CLEANUP
# ═══════════════════════════════════════════════════════════════════════════

cleanup() {
    banner "🧹 Cleanup"
    
    if [ "${KEEP_WORKSPACE:-false}" = "true" ]; then
        warn "KEEP_WORKSPACE=true, preserving workspace"
        log "Workspace location: ${WORKSPACE}"
    else
        log "Removing workspace..."
        rm -rf "${WORKSPACE}"
        success "Workspace cleaned"
    fi
}

# ═══════════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════════════

main() {
    # Trap errors
    trap 'error "Script failed at line $LINENO"' ERR
    
    initialize
    
    repos_file=$(discover_repos)
    clone_repos "${repos_file}"
    extract_artifacts
    aggregate_inventory
    commit_to_repo
    push_to_github
    push_to_huggingface
    
    cleanup
    
    banner "✅ GLOBAL WELD COMPLETE"
    success "All operations completed successfully"
    success "Sync report: ${WORKSPACE}/${SYNC_REPORT}"
}

# Run main if executed directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
