#!/bin/bash
# ════════════════════════════════════════════════════════════════════
# 🔥 TIA-ARCHITECT-CORE STATUS CHECK & IGNITION
# ════════════════════════════════════════════════════════════════════
# Purpose: Monitor TIA-ARCHITECT-CORE HuggingFace Space status
# Usage: ./scripts/check_tia_status.sh
# Version: 25.0.OMNI+
# ════════════════════════════════════════════════════════════════════

echo "════════════════════════════════════════════════════════════════════"
echo "🔥 TIA-ARCHITECT-CORE IGNITION SEQUENCE"
echo "════════════════════════════════════════════════════════════════════"
echo ""

# Space URLs
SPACE_URL="https://huggingface.co/spaces/DJ-Goanna-Coding/TIA-ARCHITECT-CORE"
SPACE_API="https://huggingface.co/api/spaces/DJ-Goanna-Coding/TIA-ARCHITECT-CORE"

# Check Space accessibility
echo "🔍 Checking HuggingFace Space status..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$SPACE_URL" --max-time 10)

echo "   HTTP Status: $HTTP_CODE"

# Interpret status
case $HTTP_CODE in
    200)
        echo "   ✅ Space is ONLINE and ACCESSIBLE"
        
        # Get Space info
        SPACE_INFO=$(curl -s "$SPACE_API" --max-time 10 2>/dev/null)
        
        if [ $? -eq 0 ] && [ -n "$SPACE_INFO" ]; then
            echo ""
            echo "📊 Space Information:"
            echo "$SPACE_INFO" | jq -r '
                "   SDK: " + (.sdk // "unknown"),
                "   Runtime: " + (.runtime.stage // "unknown"),
                "   Last Modified: " + (.lastModified // "unknown")
            ' 2>/dev/null || echo "   (Space info available via API)"
        fi
        
        echo ""
        echo "🎯 Space is LIVE:"
        echo "   $SPACE_URL"
        ;;
        
    404)
        echo "   ❌ Space NOT FOUND (404)"
        echo "   ⚠️  Space may have been deleted, renamed, or permissions issue"
        ;;
        
    503)
        echo "   🔨 Space is BUILDING or RESTARTING (503)"
        echo "   💭 This is expected after pushing changes"
        echo "   ⏱️  Typical build time: 3-5 minutes"
        ;;
        
    000)
        echo "   🔨 Space is BUILDING or OFFLINE"
        echo "   💭 This is expected if you just pushed changes"
        echo "   📋 The Space is rebuilding with your updated requirements.txt"
        echo "   ⏱️  Build typically takes 3-5 minutes with pre-built wheels"
        ;;
        
    *)
        echo "   ⚠️  Unexpected status: $HTTP_CODE"
        ;;
esac

echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "📡 MONITORING OPTIONS"
echo "════════════════════════════════════════════════════════════════════"
echo ""
echo "1. 🌐 Direct Space Access:"
echo "   $SPACE_URL"
echo ""
echo "2. 📋 Build Logs (watch the rebuild in real-time):"
echo "   ${SPACE_URL}/logs"
echo ""
echo "3. ⚙️  Space Settings:"
echo "   ${SPACE_URL}/settings"
echo ""
echo "4. 🔄 Force Rebuild (if stuck):"
echo "   Go to Settings → Factory Reboot"
echo ""

echo "════════════════════════════════════════════════════════════════════"
echo "✅ EXPECTED BUILD SUCCESS INDICATORS (in logs)"
echo "════════════════════════════════════════════════════════════════════"
echo ""
echo "With numpy>=2.0.0 and pandas>=2.2.0, you should see:"
echo ""
echo "✅ Collecting numpy>=2.0.0"
echo "✅ Downloading numpy-2.x.x-cp313-cp313-manylinux_x86_64.whl (PRE-BUILT)"
echo "✅ Successfully installed numpy-2.x.x"
echo "✅ Successfully installed pandas-2.2.x"
echo "✅ Successfully installed setuptools-75.x.x"
echo "✅ Successfully installed streamlit-1.4x.x"
echo "✅ Running on local URL: http://0.0.0.0:7860"
echo ""
echo "⏱️  Build time: ~3-5 minutes (vs 30+ minutes timeout with old deps)"
echo ""

echo "════════════════════════════════════════════════════════════════════"
echo "🔧 TROUBLESHOOTING"
echo "════════════════════════════════════════════════════════════════════"
echo ""
echo "If build fails or hangs:"
echo ""
echo "1. Check build logs for specific errors"
echo "2. Verify requirements.txt was updated correctly"
echo "3. Ensure Python 3.13 compatibility for all deps"
echo "4. Trigger repair workflow:"
echo "   gh workflow run repair_tia_core_space.yml"
echo ""

echo "════════════════════════════════════════════════════════════════════"
echo "🔥 Status check complete. Monitor build logs at:"
echo "   ${SPACE_URL}/logs"
echo "════════════════════════════════════════════════════════════════════"
