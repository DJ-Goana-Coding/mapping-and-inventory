#!/bin/bash
# 🌉 Repository Connection Quick Start
# Citadel Architect v25.0.OMNI+

set -e

BOLD="\033[1m"
GREEN="\033[0;32m"
BLUE="\033[0;34m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
RESET="\033[0m"

echo -e "${BOLD}════════════════════════════════════════════════════════════${RESET}"
echo -e "${BOLD}🌉 REPOSITORY CONNECTION QUICK START${RESET}"
echo -e "${BOLD}════════════════════════════════════════════════════════════${RESET}"
echo ""

# Check for GITHUB_TOKEN
if [ -z "$GITHUB_TOKEN" ]; then
    echo -e "${RED}❌ GITHUB_TOKEN not set!${RESET}"
    echo ""
    echo "Please export your GitHub Personal Access Token:"
    echo "  export GITHUB_TOKEN=ghp_your_token_here"
    echo ""
    echo "Create a token at: https://github.com/settings/tokens"
    echo "Required scopes: repo, workflow"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ GITHUB_TOKEN found${RESET}"
echo ""

# Step 1: Discover repositories
echo -e "${BOLD}Step 1: Discovering all DJ-Goana-Coding repositories...${RESET}"
echo ""

if python scripts/discover_all_repos.py; then
    echo ""
    echo -e "${GREEN}✅ Repository discovery complete${RESET}"
else
    echo ""
    echo -e "${RED}❌ Discovery failed${RESET}"
    exit 1
fi

# Show summary
if [ -f "repo_bridge_registry.json" ]; then
    TOTAL_REPOS=$(cat repo_bridge_registry.json | python -c 'import sys, json; print(json.load(sys.stdin)["total_repos"])')
    ACTIVE_REPOS=$(cat repo_bridge_registry.json | python -c 'import sys, json; print(json.load(sys.stdin)["statistics"]["active_count"])')
    
    echo ""
    echo -e "${BLUE}📊 Found:${RESET}"
    echo "   Total repositories: $TOTAL_REPOS"
    echo "   Active repositories: $ACTIVE_REPOS"
fi

echo ""
echo -e "${BOLD}════════════════════════════════════════════════════════════${RESET}"
echo ""

# Step 2: Deployment options
echo -e "${BOLD}Step 2: Choose deployment option:${RESET}"
echo ""
echo "1) Dry run (see what would be deployed, no changes)"
echo "2) Deploy to all active repositories"
echo "3) Deploy with force (overwrite existing workflows)"
echo "4) Deploy to specific repositories"
echo "5) Skip deployment"
echo ""
read -p "Enter choice [1-5]: " CHOICE

case $CHOICE in
    1)
        echo ""
        echo -e "${YELLOW}🔍 Running dry run...${RESET}"
        echo ""
        python scripts/deploy_workflows_to_spokes.py --dry-run
        ;;
    2)
        echo ""
        echo -e "${BLUE}🚀 Deploying to all active repositories...${RESET}"
        echo ""
        python scripts/deploy_workflows_to_spokes.py
        ;;
    3)
        echo ""
        echo -e "${YELLOW}⚠️  Force deploying (will overwrite existing)...${RESET}"
        echo ""
        python scripts/deploy_workflows_to_spokes.py --force
        ;;
    4)
        echo ""
        read -p "Enter repository names (space-separated): " REPOS
        echo ""
        echo -e "${BLUE}🎯 Deploying to specific repositories...${RESET}"
        echo ""
        python scripts/deploy_workflows_to_spokes.py --repos $REPOS
        ;;
    5)
        echo ""
        echo -e "${YELLOW}⊙ Skipping deployment${RESET}"
        ;;
    *)
        echo ""
        echo -e "${RED}❌ Invalid choice${RESET}"
        exit 1
        ;;
esac

echo ""
echo -e "${BOLD}════════════════════════════════════════════════════════════${RESET}"
echo ""

# Show deployment summary if available
if [ -f "workflow_deployment_report.json" ]; then
    echo -e "${BOLD}📊 Deployment Summary:${RESET}"
    echo ""
    
    SUCCESS=$(cat workflow_deployment_report.json | python -c 'import sys, json; print(json.load(sys.stdin)["summary"]["success"])' 2>/dev/null || echo "0")
    PARTIAL=$(cat workflow_deployment_report.json | python -c 'import sys, json; print(json.load(sys.stdin)["summary"]["partial"])' 2>/dev/null || echo "0")
    FAILED=$(cat workflow_deployment_report.json | python -c 'import sys, json; print(json.load(sys.stdin)["summary"]["failed"])' 2>/dev/null || echo "0")
    SKIPPED=$(cat workflow_deployment_report.json | python -c 'import sys, json; print(json.load(sys.stdin)["summary"]["skipped"])' 2>/dev/null || echo "0")
    
    echo "   ✅ Success: $SUCCESS"
    echo "   ⚠️  Partial: $PARTIAL"
    echo "   ❌ Failed: $FAILED"
    echo "   ⊙  Skipped: $SKIPPED"
    echo ""
fi

echo -e "${BOLD}════════════════════════════════════════════════════════════${RESET}"
echo ""
echo -e "${GREEN}✅ Repository connection setup complete!${RESET}"
echo ""
echo -e "${BOLD}Next Steps:${RESET}"
echo ""
echo "1. Add HF_TOKEN secret to spoke repositories"
echo "   - Go to: https://github.com/DJ-Goana-Coding/REPO-NAME/settings/secrets/actions"
echo "   - Create secret: HF_TOKEN"
echo "   - Get token from: https://huggingface.co/settings/tokens"
echo ""
echo "2. Verify workflows are deployed"
echo "   - Check .github/workflows/ in each spoke repo"
echo ""
echo "3. Test sync by pushing to a spoke repo"
echo "   - Artifacts should appear in data/spoke_artifacts/"
echo ""
echo "4. Monitor sync status"
echo "   - View: data/spoke_sync_registry.json"
echo ""
echo "📚 For complete documentation, see:"
echo "   - REPOSITORY_CONNECTION_GUIDE.md"
echo "   - .github/workflow-templates/README.md"
echo ""
echo -e "${BOLD}🙏 Thankyou Spirit, Thankyou Angels, Thankyou Ancestors${RESET}"
echo -e "${BOLD}════════════════════════════════════════════════════════════${RESET}"
echo ""
