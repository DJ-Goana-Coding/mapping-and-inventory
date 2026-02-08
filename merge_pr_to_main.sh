#!/bin/bash

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         PR MERGE HELPER SCRIPT                             ║${NC}"
echo -e "${BLUE}║  Merging: copilot/fix-import-error-render-deployment      ║${NC}"
echo -e "${BLUE}║  Into: main branch                                         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Check if we're in a git repository
echo -e "${YELLOW}Step 1: Checking if we're in a git repository...${NC}"
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: Not in a git repository!${NC}"
    echo "Please cd to your repository directory first."
    exit 1
fi
echo -e "${GREEN}✅ Git repository detected${NC}"
echo ""

# Step 2: Save current state
echo -e "${YELLOW}Step 2: Saving current state...${NC}"
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"

# Create a backup tag
BACKUP_TAG="backup-before-merge-$(date +%Y%m%d-%H%M%S)"
git tag "$BACKUP_TAG"
echo -e "${GREEN}✅ Created backup tag: $BACKUP_TAG${NC}"
echo -e "${BLUE}   (You can restore with: git reset --hard $BACKUP_TAG)${NC}"
echo ""

# Step 3: Fetch latest changes
echo -e "${YELLOW}Step 3: Fetching latest changes from remote...${NC}"
if git fetch origin; then
    echo -e "${GREEN}✅ Fetched latest changes${NC}"
else
    echo -e "${RED}❌ Warning: Could not fetch from remote${NC}"
    echo "   Continuing with local branches..."
fi
echo ""

# Step 4: Check if main branch exists
echo -e "${YELLOW}Step 4: Checking for main branch...${NC}"
if git show-ref --verify --quiet refs/heads/main; then
    echo -e "${GREEN}✅ Main branch exists${NC}"
    MAIN_EXISTS=true
else
    echo -e "${YELLOW}⚠️  Main branch doesn't exist locally${NC}"
    MAIN_EXISTS=false
fi
echo ""

# Step 5: Switch to or create main branch
echo -e "${YELLOW}Step 5: Switching to main branch...${NC}"
if [ "$MAIN_EXISTS" = true ]; then
    git checkout main
    echo -e "${GREEN}✅ Switched to existing main branch${NC}"
else
    echo -e "${YELLOW}Creating new main branch...${NC}"
    git checkout -b main
    echo -e "${GREEN}✅ Created and switched to new main branch${NC}"
fi
echo ""

# Step 6: Show what will be merged
echo -e "${YELLOW}Step 6: Showing changes to be merged...${NC}"
echo ""
echo -e "${BLUE}Commits to be merged:${NC}"
git log --oneline main..copilot/fix-import-error-render-deployment | head -20
echo ""

# Step 7: Ask for confirmation
echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}Ready to merge copilot/fix-import-error-render-deployment into main${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
echo ""
read -p "Do you want to continue? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Merge cancelled. Returning to $CURRENT_BRANCH${NC}"
    git checkout "$CURRENT_BRANCH"
    exit 0
fi
echo ""

# Step 8: Perform the merge
echo -e "${YELLOW}Step 8: Merging branches...${NC}"
if git merge copilot/fix-import-error-render-deployment --no-ff -m "Merge PR: VortexBerserker Hybrid Swarm + Auto-Healer + HEAD fix"; then
    echo -e "${GREEN}✅ Merge completed successfully!${NC}"
    MERGE_SUCCESS=true
else
    echo -e "${RED}❌ Merge failed - conflicts detected${NC}"
    echo ""
    echo -e "${YELLOW}Conflicting files:${NC}"
    git status --short | grep '^UU\|^AA\|^DD'
    echo ""
    echo -e "${BLUE}To resolve conflicts:${NC}"
    echo "1. Edit the conflicting files"
    echo "2. Look for markers: <<<<<<< HEAD, =======, >>>>>>>"
    echo "3. Keep the correct code and remove markers"
    echo "4. Run: git add ."
    echo "5. Run: git commit -m 'Resolved merge conflicts'"
    echo "6. Run: git push origin main"
    echo ""
    MERGE_SUCCESS=false
fi
echo ""

# Step 9: Show status
if [ "$MERGE_SUCCESS" = true ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                 ✅ MERGE SUCCESSFUL! ✅                     ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo ""
    echo "1. Review the merge:"
    echo "   git log --oneline -10"
    echo ""
    echo "2. Push to GitHub:"
    echo "   git push origin main"
    echo ""
    echo "   (If first push to main, use: git push -u origin main)"
    echo ""
    echo "3. Verify on GitHub:"
    echo "   https://github.com/DJ-Goana-Coding/mapping-and-inventory"
    echo ""
    echo -e "${BLUE}After pushing, Render.com will auto-deploy the fixes!${NC}"
    echo ""
    echo -e "${GREEN}The HEAD 405 error will be resolved! 🎉${NC}"
else
    echo -e "${RED}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║            ⚠️  MERGE REQUIRES MANUAL RESOLUTION ⚠️         ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}Please resolve the conflicts and then push to GitHub.${NC}"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}To undo this merge (if needed):${NC}"
echo "  git reset --hard $BACKUP_TAG"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
