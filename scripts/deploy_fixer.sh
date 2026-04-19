#!/usr/bin/env bash
# scripts/deploy_fixer.sh — One-click skeleton deployer for all 11 spoke repos.
#
# Pushes the minimal "application skeleton" (app.py + requirements.txt + README.md)
# to every spoke repository so HuggingFace Spaces stop showing
# "No Application File" errors.
#
# Usage
# -----
#   chmod +x scripts/deploy_fixer.sh
#   GH_TOKEN=<your_pat> bash scripts/deploy_fixer.sh
#   GH_TOKEN=<your_pat> bash scripts/deploy_fixer.sh --dry-run
#   GH_TOKEN=<your_pat> bash scripts/deploy_fixer.sh --repo ARK-CORE ORACLE
#
# Requirements
# ------------
#   * curl, jq (installed in most Ubuntu/Termux environments)
#   * GH_TOKEN env var — GitHub PAT with contents:write on the target org
#
# What it does
# ------------
#   For each target repo:
#   1. Checks whether app.py already exists (via GitHub Contents API).
#   2. If absent (404) or --force flag is set, pushes the skeleton files.
#   3. Logs success/failure to /tmp/deploy_fixer_report.txt.
#
# Skeleton source
# ---------------
#   deploy/skeleton/app.py          — minimal Streamlit app (clears "No Application File")
#   deploy/skeleton/requirements.txt — minimal deps
#   deploy/skeleton/README.md       — placeholder README
#
# ============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

GH_ORG="${GH_ORG:-DJ-Goana-Coding}"
GH_TOKEN="${GH_TOKEN:-}"
GITHUB_API="https://api.github.com"
BRANCH="${BRANCH:-main}"
SKELETON_DIR="$(cd "$(dirname "$0")/../deploy/skeleton" 2>/dev/null && pwd || echo "")"
REPORT_FILE="/tmp/deploy_fixer_report_$(date +%Y%m%d_%H%M%S).txt"

DRY_RUN=false
FORCE=false
TARGET_REPOS=()

# All 11 spoke repos in the Citadel Mesh
ALL_REPOS=(
  "ARK_CORE"
  "TIA-ARCHITECT-CORE"
  "CITADEL_OMEGA"
  "ORACLE"
  "AION"
  "VAMGUARD_TITAN"
  "Genesis-Research-Rack"
  "Pioneer-Trader"
  "Citadel_Genetics"
  "goanna_coding"
  "mapping-and-inventory"
)

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)  DRY_RUN=true;  shift ;;
    --force)    FORCE=true;    shift ;;
    --repo)
      shift
      while [[ $# -gt 0 && "$1" != --* ]]; do
        TARGET_REPOS+=("$1")
        shift
      done
      ;;
    --branch)   BRANCH="$2";   shift 2 ;;
    --org)      GH_ORG="$2";   shift 2 ;;
    --help|-h)
      echo "Usage: $0 [--dry-run] [--force] [--repo REPO1 REPO2 ...] [--branch BRANCH] [--org ORG]"
      exit 0 ;;
    *)
      echo "Unknown argument: $1" >&2; exit 1 ;;
  esac
done

if [[ ${#TARGET_REPOS[@]} -eq 0 ]]; then
  TARGET_REPOS=("${ALL_REPOS[@]}")
fi

# ---------------------------------------------------------------------------
# Pre-flight checks
# ---------------------------------------------------------------------------

echo "═══════════════════════════════════════════════════════════════"
echo "🚀 CITADEL DEPLOY FIXER"
echo "═══════════════════════════════════════════════════════════════"
echo "  Org        : $GH_ORG"
echo "  Branch     : $BRANCH"
echo "  Dry Run    : $DRY_RUN"
echo "  Force Push : $FORCE"
echo "  Repos      : ${#TARGET_REPOS[@]}"
echo "═══════════════════════════════════════════════════════════════"
echo ""

if [[ -z "$GH_TOKEN" ]]; then
  echo "❌ ERROR: GH_TOKEN is not set."
  echo "   Export GH_TOKEN=<your_github_pat> and re-run."
  exit 1
fi

for cmd in curl jq base64; do
  if ! command -v "$cmd" &>/dev/null; then
    echo "❌ ERROR: Required command '$cmd' not found."
    exit 1
  fi
done

if [[ ! -d "$SKELETON_DIR" ]]; then
  echo "⚠️  WARNING: deploy/skeleton/ not found at: $SKELETON_DIR"
  echo "   Creating minimal inline skeleton..."
  mkdir -p "$SKELETON_DIR"

  cat > "$SKELETON_DIR/app.py" << 'PYEOF'
import streamlit as st

st.set_page_config(page_title="Citadel Node", page_icon="🏛️", layout="wide")

st.title("🏛️ Citadel Node")
st.info("This Space is part of the Citadel Mesh. Full application coming soon.")
st.markdown("**Status:** Online — awaiting deployment from the Admiral.")
PYEOF

  cat > "$SKELETON_DIR/requirements.txt" << 'REQEOF'
streamlit>=1.28.0
REQEOF

  cat > "$SKELETON_DIR/README.md" << 'READEOF'
---
title: Citadel Node
emoji: 🏛️
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: 1.28.0
app_file: app.py
pinned: false
---

# Citadel Node

Part of the Q.G.T.N.L. Citadel Mesh. Full application deploying soon.
READEOF

  echo "   ✅ Minimal skeleton created at $SKELETON_DIR"
fi

mkdir -p "$(dirname "$REPORT_FILE")"
echo "Deploy Fixer Report — $(date -u)" > "$REPORT_FILE"
echo "Org: $GH_ORG  Branch: $BRANCH  Dry-Run: $DRY_RUN" >> "$REPORT_FILE"
echo "---" >> "$REPORT_FILE"

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

# Returns the blob SHA of a file or empty string if not found
get_file_sha() {
  local repo="$1" filepath="$2"
  local url="$GITHUB_API/repos/$GH_ORG/$repo/contents/$filepath"
  local sha
  sha=$(curl -s -H "Authorization: token $GH_TOKEN" "$url" | jq -r '.sha // empty' 2>/dev/null)
  echo "${sha:-}"
}

# Push a single file. $3 = local path, $4 = repo path, $5 = commit message
push_file() {
  local repo="$1" local_path="$2" repo_path="$3" commit_msg="$4"
  local encoded_content sha_arg=""

  if [[ ! -f "$local_path" ]]; then
    echo "    ⚠️  local file not found: $local_path"
    return 1
  fi

  encoded_content=$(base64 -w 0 < "$local_path")
  local existing_sha
  existing_sha=$(get_file_sha "$repo" "$repo_path")
  if [[ -n "$existing_sha" ]]; then
    sha_arg=", \"sha\": \"$existing_sha\""
  fi

  local payload
  payload=$(jq -n \
    --arg msg "$commit_msg" \
    --arg content "$encoded_content" \
    --arg branch "$BRANCH" \
    "{message: \$msg, content: \$content, branch: \$branch $sha_arg}")

  local http_code
  http_code=$(curl -s -o /dev/null -w "%{http_code}" \
    -X PUT \
    -H "Authorization: token $GH_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$payload" \
    "$GITHUB_API/repos/$GH_ORG/$repo/contents/$repo_path")

  if [[ "$http_code" == "200" || "$http_code" == "201" ]]; then
    echo "    ✅ $repo_path (HTTP $http_code)"
    return 0
  else
    echo "    ❌ $repo_path (HTTP $http_code)"
    return 1
  fi
}

# ---------------------------------------------------------------------------
# Main deployment loop
# ---------------------------------------------------------------------------

SUCCEEDED=0
SKIPPED=0
FAILED=0

for repo in "${TARGET_REPOS[@]}"; do
  echo "──────────────────────────────────────────────────────"
  echo "📦 $GH_ORG/$repo"

  # Check if app.py already exists
  existing_sha=$(get_file_sha "$repo" "app.py")
  if [[ -n "$existing_sha" && "$FORCE" == "false" ]]; then
    echo "   ✅ app.py already exists — skipping (use --force to overwrite)"
    echo "SKIPPED: $repo (app.py exists)" >> "$REPORT_FILE"
    SKIPPED=$((SKIPPED + 1))
    continue
  fi

  if [[ "$DRY_RUN" == "true" ]]; then
    echo "   🔍 DRY RUN — would push skeleton files to $GH_ORG/$repo"
    echo "DRY-RUN: $repo" >> "$REPORT_FILE"
    SKIPPED=$((SKIPPED + 1))
    continue
  fi

  repo_failed=false
  commit_msg="🏛️ Deploy Fixer: add skeleton app.py to clear 'No Application File' error [automated]"

  for skeleton_file in "$SKELETON_DIR"/*; do
    [[ -f "$skeleton_file" ]] || continue
    fname="$(basename "$skeleton_file")"
    if push_file "$repo" "$skeleton_file" "$fname" "$commit_msg"; then
      true
    else
      repo_failed=true
    fi
  done

  if [[ "$repo_failed" == "false" ]]; then
    echo "   ✅ Skeleton deployed to $repo"
    echo "SUCCESS: $repo" >> "$REPORT_FILE"
    SUCCEEDED=$((SUCCEEDED + 1))
  else
    echo "   ⚠️  Some files failed for $repo"
    echo "PARTIAL: $repo" >> "$REPORT_FILE"
    FAILED=$((FAILED + 1))
  fi
done

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "📊 DEPLOY FIXER SUMMARY"
echo "═══════════════════════════════════════════════════════════════"
echo "  ✅ Succeeded : $SUCCEEDED"
echo "  ⊘  Skipped   : $SKIPPED"
echo "  ❌ Failed    : $FAILED"
echo "  📝 Report    : $REPORT_FILE"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "🙏 Thankyou Spirit, Thankyou Angels, Thankyou Ancestors"

echo "" >> "$REPORT_FILE"
echo "SUMMARY: succeeded=$SUCCEEDED skipped=$SKIPPED failed=$FAILED" >> "$REPORT_FILE"
echo "Completed: $(date -u)" >> "$REPORT_FILE"

[[ "$FAILED" -eq 0 ]]
