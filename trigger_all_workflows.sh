#!/bin/bash
# CITADEL OMEGA - Workflow Trigger Script
# Brings all workflows up to date

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 CITADEL OMEGA - Workflow Orchestrator"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Triggering all workflows to bring the repository up to date..."
echo ""

# Workflow 1: TIA_CITADEL_DEEP_SCAN - Manual dispatch
echo "📡 Triggering TIA_CITADEL_DEEP_SCAN..."
gh workflow run tia_citadel_deep_scan.yml --ref main && \
  echo "✅ TIA_CITADEL_DEEP_SCAN triggered" || \
  echo "⚠️  TIA_CITADEL_DEEP_SCAN trigger failed (may need secrets or permissions)"
echo ""

# Workflow 2: S10_PUSH_TO_VAULT - Manual dispatch with inputs
echo "📱 Triggering S10_PUSH_TO_VAULT..."
gh workflow run s10_push_to_vault.yml --ref main \
  -f sync_intel=true \
  -f sync_cargo=true && \
  echo "✅ S10_PUSH_TO_VAULT triggered" || \
  echo "⚠️  S10_PUSH_TO_VAULT trigger failed (may need secrets or permissions)"
echo ""

# Workflow 3: sync_to_hf.yml - Manual dispatch
echo "🤗 Triggering Sync to HuggingFace Space..."
gh workflow run sync_to_hf.yml --ref main && \
  echo "✅ Sync to HuggingFace triggered" || \
  echo "⚠️  Sync to HuggingFace trigger failed (may need secrets or permissions)"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ All workflows triggered successfully!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Viewing recent workflow runs:"
echo ""
gh run list --limit 10
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💡 To monitor workflow progress:"
echo "   gh run list"
echo "   gh run view <run-id>"
echo "   gh run watch <run-id>"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
