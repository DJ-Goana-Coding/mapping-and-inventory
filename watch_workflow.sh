#!/bin/bash
# 📡 Workflow Watch Helper Script
# 
# This script helps you easily monitor GitHub Actions workflow runs.
# Usage: ./watch_workflow.sh [run-id]
#        ./watch_workflow.sh              (watches the latest run)
#        ./watch_workflow.sh 23840652380  (watches specific run)

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ Error: GitHub CLI (gh) is not installed.${NC}"
    echo -e "${YELLOW}Install it from: https://cli.github.com/${NC}"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${RED}❌ Error: Not authenticated with GitHub CLI.${NC}"
    echo -e "${YELLOW}Run: gh auth login${NC}"
    exit 1
fi

# Function to display usage
usage() {
    echo -e "${BLUE}📡 Workflow Watch Helper${NC}"
    echo ""
    echo "Usage:"
    echo "  ./watch_workflow.sh [OPTIONS] [run-id]"
    echo ""
    echo "Options:"
    echo "  -h, --help         Show this help message"
    echo "  -l, --list         List recent workflow runs"
    echo "  -c, --compact      Use compact output (recommended)"
    echo "  -w, --workflow     Specify workflow name to list/watch"
    echo "  -v, --view         View run summary instead of watching"
    echo "  --log              View logs instead of watching"
    echo "  --web              Open run in browser"
    echo ""
    echo "Examples:"
    echo "  ./watch_workflow.sh                               # Watch latest run"
    echo "  ./watch_workflow.sh --compact                     # Watch latest run (compact)"
    echo "  ./watch_workflow.sh 23840652380                   # Watch specific run"
    echo "  ./watch_workflow.sh --list                        # List recent runs"
    echo "  ./watch_workflow.sh --workflow tia_citadel_deep_scan.yml --list"
    echo "  ./watch_workflow.sh 23840652380 --view            # View summary"
    echo "  ./watch_workflow.sh 23840652380 --log             # View logs"
    echo ""
}

# Parse arguments
RUN_ID=""
COMPACT=""
WORKFLOW=""
LIST_ONLY=false
VIEW_MODE=""
WEB_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        -l|--list)
            LIST_ONLY=true
            shift
            ;;
        -c|--compact)
            COMPACT="--compact"
            shift
            ;;
        -w|--workflow)
            WORKFLOW="$2"
            shift 2
            ;;
        -v|--view)
            VIEW_MODE="view"
            shift
            ;;
        --log)
            VIEW_MODE="log"
            shift
            ;;
        --web)
            WEB_MODE=true
            shift
            ;;
        [0-9]*)
            RUN_ID="$1"
            shift
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            usage
            exit 1
            ;;
    esac
done

# List mode
if [ "$LIST_ONLY" = true ]; then
    echo -e "${BLUE}📋 Recent Workflow Runs:${NC}"
    echo ""
    if [ -n "$WORKFLOW" ]; then
        gh run list --workflow="$WORKFLOW" --limit 10
    else
        gh run list --limit 10
    fi
    exit 0
fi

# Get run ID if not provided
if [ -z "$RUN_ID" ]; then
    echo -e "${YELLOW}🔍 No run ID provided. Fetching latest run...${NC}"
    if [ -n "$WORKFLOW" ]; then
        RUN_ID=$(gh run list --workflow="$WORKFLOW" --limit 1 --json databaseId --jq '.[0].databaseId')
    else
        RUN_ID=$(gh run list --limit 1 --json databaseId --jq '.[0].databaseId')
    fi
    
    if [ -z "$RUN_ID" ]; then
        echo -e "${RED}❌ Error: Could not find any workflow runs.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Found run ID: $RUN_ID${NC}"
    echo ""
fi

# Open in web mode
if [ "$WEB_MODE" = true ]; then
    echo -e "${BLUE}🌐 Opening run $RUN_ID in browser...${NC}"
    gh run view "$RUN_ID" --web
    exit 0
fi

# View or log mode
if [ "$VIEW_MODE" = "view" ]; then
    echo -e "${BLUE}📊 Viewing run $RUN_ID summary:${NC}"
    echo ""
    gh run view "$RUN_ID"
    exit 0
elif [ "$VIEW_MODE" = "log" ]; then
    echo -e "${BLUE}📜 Viewing run $RUN_ID logs:${NC}"
    echo ""
    gh run view "$RUN_ID" --log
    exit 0
fi

# Watch mode (default)
echo -e "${BLUE}📡 Watching run $RUN_ID...${NC}"
echo ""

if [ -n "$COMPACT" ]; then
    echo -e "${YELLOW}💡 Using compact mode (showing only relevant steps)${NC}"
    echo ""
fi

# Show quick summary first
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
gh run view "$RUN_ID" --json headBranch,workflowName,status,conclusion,createdAt --template '{{.workflowName}} ({{.status}})
Branch: {{.headBranch}}
Created: {{.createdAt}}
'
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Start watching
if [ -n "$COMPACT" ]; then
    gh run watch "$RUN_ID" --compact --exit-status
else
    gh run watch "$RUN_ID" --exit-status
fi

# Show final status
EXIT_CODE=$?
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ Workflow completed successfully!${NC}"
else
    echo -e "${RED}❌ Workflow failed with exit code $EXIT_CODE${NC}"
    echo ""
    echo -e "${YELLOW}💡 To view failed logs only:${NC}"
    echo "   gh run view $RUN_ID --log-failed"
fi
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

exit $EXIT_CODE
