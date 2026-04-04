#!/bin/bash
# 🔐 GDRIVE RCLONE SETUP AUTOMATION
# Authority: Citadel Architect v25.0.OMNI+
# Purpose: Guide operator through Rclone setup for both GDrive accounts

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔐 GDRIVE RCLONE SETUP - Citadel Architect v25.0.OMNI+"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 This script will guide you through setting up Rclone for:"
echo "   1. chanceroofing@gmail.com (locked account - GDrive still accessible)"
echo "   2. mynewemail110411@gmail.com (active account)"
echo ""

# Check if rclone is installed
if ! command -v rclone &> /dev/null; then
    echo "❌ Rclone is not installed!"
    echo ""
    echo "📥 Please install Rclone first:"
    echo ""
    echo "   Linux/macOS:"
    echo "   curl https://rclone.org/install.sh | sudo bash"
    echo ""
    echo "   Windows (PowerShell as Administrator):"
    echo "   iex \"& { \$(irm https://rclone.org/install.ps1) } -Scope CurrentUser\""
    echo ""
    echo "   Or download from: https://rclone.org/downloads/"
    echo ""
    exit 1
fi

echo "✅ Rclone is installed: $(rclone version | head -1)"
echo ""

# Function to setup a remote
setup_remote() {
    local REMOTE_NAME=$1
    local EMAIL=$2
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔧 Setting up remote: $REMOTE_NAME"
    echo "   Email: $EMAIL"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Check if remote already exists
    if rclone listremotes | grep -q "^${REMOTE_NAME}:$"; then
        echo "⚠️  Remote '$REMOTE_NAME' already exists!"
        read -p "   Do you want to reconfigure it? (y/n): " RECONFIGURE
        if [[ $RECONFIGURE != "y" ]]; then
            echo "   Skipping $REMOTE_NAME"
            return
        fi
    fi
    
    echo "📝 Instructions for $REMOTE_NAME:"
    echo "   1. When prompted, choose 'n' for new remote"
    echo "   2. Name: $REMOTE_NAME"
    echo "   3. Storage: Type '13' or 'drive' for Google Drive"
    echo "   4. Client ID: Leave blank (press Enter)"
    echo "   5. Client Secret: Leave blank (press Enter)"
    echo "   6. Scope: Choose '1' for full access"
    echo "   7. Root folder ID: Leave blank (press Enter)"
    echo "   8. Service account file: Leave blank (press Enter)"
    echo "   9. Advanced config: Choose 'n'"
    echo "  10. Auto config: Choose 'y' (will open browser)"
    echo "  11. Login with: $EMAIL"
    echo "  12. Team drive: Choose 'n'"
    echo "  13. Confirm: Choose 'y'"
    echo ""
    read -p "Press Enter to start Rclone configuration..."
    
    # Start rclone config
    rclone config
    
    echo ""
    echo "✅ Configuration complete for $REMOTE_NAME"
    echo ""
}

# Setup both remotes
setup_remote "gdrive_chanceroofing" "chanceroofing@gmail.com"
setup_remote "gdrive_mynewemail" "mynewemail110411@gmail.com"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 Testing Rclone Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test both remotes
for REMOTE in "gdrive_chanceroofing" "gdrive_mynewemail"; do
    echo "Testing $REMOTE..."
    if rclone lsf "${REMOTE}:" --max-depth 1 --max-results 5 &> /dev/null; then
        echo "   ✅ $REMOTE is accessible!"
        echo "   Top 5 items:"
        rclone lsf "${REMOTE}:" --max-depth 1 --max-results 5 | sed 's/^/      /'
    else
        echo "   ❌ $REMOTE is not accessible!"
        echo "      Please reconfigure this remote"
    fi
    echo ""
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 Exporting Rclone Config for GitHub Secrets"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

RCLONE_CONFIG_PATH="$HOME/.config/rclone/rclone.conf"

if [[ -f "$RCLONE_CONFIG_PATH" ]]; then
    echo "📄 Rclone config location: $RCLONE_CONFIG_PATH"
    echo ""
    echo "🔐 To use this config in GitHub Actions:"
    echo "   1. Copy the config content:"
    echo "      cat $RCLONE_CONFIG_PATH | base64"
    echo ""
    echo "   2. Go to GitHub repository settings:"
    echo "      https://github.com/DJ-Goana-Coding/mapping-and-inventory/settings/secrets/actions"
    echo ""
    echo "   3. Create new secret:"
    echo "      Name: RCLONE_CONFIG_DATA"
    echo "      Value: <paste the base64 output>"
    echo ""
    echo "   Or run this automated command:"
    echo "      gh secret set RCLONE_CONFIG_DATA < <(cat $RCLONE_CONFIG_PATH | base64 -w 0)"
    echo ""
    
    read -p "Do you want to display the base64 config now? (y/n): " SHOW_CONFIG
    if [[ $SHOW_CONFIG == "y" ]]; then
        echo ""
        echo "━━━━━━━━━━━━━ Base64 Config (copy this) ━━━━━━━━━━━━━"
        cat "$RCLONE_CONFIG_PATH" | base64 -w 0
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    fi
else
    echo "❌ Rclone config not found at $RCLONE_CONFIG_PATH"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ RCLONE SETUP COMPLETE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Next Steps:"
echo "   1. ✅ Rclone configured for both accounts"
echo "   2. 🔐 Add RCLONE_CONFIG_DATA to GitHub Secrets"
echo "   3. 🧪 Run: python scripts/verify_gdrive_access.py"
echo "   4. 🚀 Trigger workflow: gdrive_emergency_extraction.yml"
echo ""
echo "📚 Documentation:"
echo "   - COMPLETE_DATA_MIGRATION_GUIDE.md"
echo "   - GDRIVE_OAUTH_SETUP.md"
echo ""
