#!/bin/bash
# CITADEL OMEGA - Full Automation Orchestrator
# Automates pulls, workflows, and merges across all repositories

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Banner
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${PURPLE}   CITADEL OMEGA - Full Automation Orchestrator${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ Error: GitHub CLI (gh) is not installed${NC}"
    echo "Install it from: https://cli.github.com/"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${RED}❌ Error: Not authenticated with GitHub${NC}"
    echo "Run: gh auth login"
    exit 1
fi

echo -e "${GREEN}✅ GitHub CLI authenticated${NC}"
echo ""

# Function to display menu
show_menu() {
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Select automation operation:${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo "  1) 📥 Pull latest changes from main"
    echo "  2) 🚀 Trigger all workflows"
    echo "  3) 🔀 Check and merge eligible PRs"
    echo "  4) ⚡ Full automation (pull + workflows + merge)"
    echo "  5) 📊 Status report (branches, PRs, workflows)"
    echo "  6) 🔄 Sync all related repositories"
    echo "  7) 🛠️  Manual workflow dispatch"
    echo "  8) ❌ Exit"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -n "Enter your choice [1-8]: "
}

# Function: Pull latest changes
pull_latest() {
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}📥 Pulling latest changes from main branch${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    git fetch origin
    git checkout main
    git pull origin main
    
    echo ""
    echo -e "${GREEN}✅ Main branch synchronized${NC}"
    echo ""
}

# Function: Trigger all workflows
trigger_workflows() {
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}🚀 Triggering all workflows${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    echo ""
    echo "📡 Triggering TIA_CITADEL_DEEP_SCAN..."
    gh workflow run tia_citadel_deep_scan.yml --ref main && \
        echo -e "${GREEN}✅ TIA_CITADEL_DEEP_SCAN triggered${NC}" || \
        echo -e "${YELLOW}⚠️  TIA_CITADEL_DEEP_SCAN failed (may need secrets)${NC}"
    
    echo ""
    echo "📱 Triggering S10_PUSH_TO_VAULT..."
    gh workflow run s10_push_to_vault.yml --ref main \
        -f sync_intel=true \
        -f sync_cargo=true && \
        echo -e "${GREEN}✅ S10_PUSH_TO_VAULT triggered${NC}" || \
        echo -e "${YELLOW}⚠️  S10_PUSH_TO_VAULT failed (may need secrets)${NC}"
    
    echo ""
    echo "🤗 Triggering Sync to HuggingFace Space..."
    gh workflow run sync_to_hf.yml --ref main && \
        echo -e "${GREEN}✅ sync_to_hf triggered${NC}" || \
        echo -e "${YELLOW}⚠️  sync_to_hf failed (may need secrets)${NC}"
    
    echo ""
    echo -e "${GREEN}✅ All workflows triggered${NC}"
    echo ""
}

# Function: Check and merge PRs
check_merge_prs() {
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}🔀 Checking for PRs eligible for auto-merge${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    echo ""
    echo "Open Pull Requests:"
    gh pr list --state open
    
    echo ""
    echo -e "${YELLOW}ℹ️  Auto-merge requirements:${NC}"
    echo "  1. PR must have 'auto-merge' label"
    echo "  2. All status checks must pass"
    echo "  3. No merge conflicts"
    echo ""
    echo -e "${YELLOW}⚠️  Manual approval recommended for code changes${NC}"
    echo ""
}

# Function: Full automation
full_automation() {
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}⚡ Running full automation sequence${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    pull_latest
    sleep 2
    trigger_workflows
    sleep 2
    check_merge_prs
    
    echo ""
    echo -e "${GREEN}✅ Full automation sequence complete${NC}"
    echo ""
}

# Function: Status report
status_report() {
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}📊 Repository Status Report${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    echo ""
    echo -e "${PURPLE}📍 Current Branch:${NC}"
    git branch --show-current
    
    echo ""
    echo -e "${PURPLE}📝 Git Status:${NC}"
    git status --short
    
    echo ""
    echo -e "${PURPLE}🔄 Recent Commits:${NC}"
    git log --oneline -5
    
    echo ""
    echo -e "${PURPLE}🔀 Open Pull Requests:${NC}"
    gh pr list --state open || echo "No open PRs"
    
    echo ""
    echo -e "${PURPLE}⚙️  Recent Workflow Runs:${NC}"
    gh run list --limit 5
    
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Function: Sync related repositories
sync_repositories() {
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}🔄 Syncing related repositories${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    echo ""
    echo -e "${YELLOW}ℹ️  Current repository: mapping-and-inventory${NC}"
    pull_latest
    
    echo ""
    echo -e "${PURPLE}📋 Related repositories (from SYSTEM_MAP.txt):${NC}"
    echo "  - omega-trading-system (TRADING pillar)"
    echo "  - forever-learning (TRADING/MEMORY pillar)"
    echo "  - CITADEL_ARK (TRADING pillar)"
    echo "  - memory-codex (LORE pillar)"
    echo ""
    echo -e "${YELLOW}ℹ️  These repos will be synced when created${NC}"
    echo ""
}

# Function: Manual workflow dispatch
manual_dispatch() {
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}🛠️  Manual Workflow Dispatch${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    echo ""
    echo "Available workflows:"
    echo "  1) tia_citadel_deep_scan.yml"
    echo "  2) s10_push_to_vault.yml"
    echo "  3) sync_to_hf.yml"
    echo "  4) auto_sync_and_run.yml"
    echo "  5) multi_repo_sync.yml"
    echo "  6) auto_merge_to_main.yml"
    echo ""
    echo -n "Select workflow [1-6]: "
    read workflow_choice
    
    case $workflow_choice in
        1) gh workflow run tia_citadel_deep_scan.yml --ref main ;;
        2) gh workflow run s10_push_to_vault.yml --ref main -f sync_intel=true -f sync_cargo=true ;;
        3) gh workflow run sync_to_hf.yml --ref main ;;
        4) gh workflow run auto_sync_and_run.yml --ref main ;;
        5) gh workflow run multi_repo_sync.yml --ref main ;;
        6) gh workflow run auto_merge_to_main.yml --ref main ;;
        *) echo -e "${RED}Invalid choice${NC}" ;;
    esac
    
    echo ""
    echo -e "${GREEN}✅ Workflow triggered${NC}"
    echo ""
}

# Main menu loop
while true; do
    show_menu
    read choice
    echo ""
    
    case $choice in
        1) pull_latest ;;
        2) trigger_workflows ;;
        3) check_merge_prs ;;
        4) full_automation ;;
        5) status_report ;;
        6) sync_repositories ;;
        7) manual_dispatch ;;
        8) 
            echo -e "${GREEN}👋 Exiting automation orchestrator${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Invalid choice. Please select 1-8.${NC}"
            echo ""
            ;;
    esac
    
    # Wait before showing menu again
    echo ""
    echo -n "Press Enter to continue..."
    read
    echo ""
done
