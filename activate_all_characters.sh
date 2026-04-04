#!/bin/bash
#
# 🎭 MASTER CHARACTER ACTIVATION
# Activates all 6 characters with tech stacks, workers, swarms, shopping, testing, documentation
#

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo "================================="
echo "🎭 MASTER CHARACTER ACTIVATION"
echo "================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    exit 1
fi

echo -e "${BLUE}🐍 Python 3: $(python3 --version)${NC}"

# Install dependencies
echo ""
echo -e "${YELLOW}📦 Installing dependencies...${NC}"
pip install -q requests asyncio 2>/dev/null || true

# Parse mode
MODE=${1:-full}

case $MODE in
    test)
        echo -e "${GREEN}🧪 Testing activation infrastructure...${NC}"
        echo ""
        
        # Check scripts exist
        if [ -f "scripts/activate_all_characters.py" ]; then
            echo -e "${GREEN}✅ Character activator found${NC}"
        else
            echo -e "${RED}❌ Character activator missing${NC}"
            exit 1
        fi
        
        if [ -f "scripts/deploy_character_swarms.py" ]; then
            echo -e "${GREEN}✅ Swarm deployer found${NC}"
        else
            echo -e "${RED}❌ Swarm deployer missing${NC}"
            exit 1
        fi
        
        echo ""
        echo -e "${GREEN}✅ All activation infrastructure ready!${NC}"
        ;;
    
    swarms)
        echo -e "${GREEN}🐝 Deploying worker swarms only...${NC}"
        python3 scripts/deploy_character_swarms.py
        ;;
    
    characters)
        echo -e "${GREEN}🎭 Activating characters only...${NC}"
        python3 scripts/activate_all_characters.py
        ;;
    
    full)
        echo -e "${GREEN}🚀 FULL ACTIVATION SEQUENCE${NC}"
        echo ""
        echo -e "${PURPLE}This will:${NC}"
        echo "  1. Activate all 6 AI characters"
        echo "  2. Load tech stacks for each"
        echo "  3. Deploy autonomous worker swarms"
        echo "  4. Generate shopping lists (10 solutions each)"
        echo "  5. Deploy shopping agents"
        echo "  6. Search for lost funds/crypto/knowledge"
        echo "  7. Run comprehensive tests"
        echo "  8. Document everything"
        echo "  9. Map and inventory all components"
        echo "  10. Integrate at 100% pass rate"
        echo ""
        
        read -p "Continue? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Activation cancelled."
            exit 0
        fi
        
        echo ""
        echo -e "${BLUE}═══════════════════════════════════════${NC}"
        echo -e "${BLUE}PHASE 1: CHARACTER ACTIVATION${NC}"
        echo -e "${BLUE}═══════════════════════════════════════${NC}"
        python3 scripts/activate_all_characters.py
        
        echo ""
        echo -e "${BLUE}═══════════════════════════════════════${NC}"
        echo -e "${BLUE}PHASE 2: SWARM DEPLOYMENT${NC}"
        echo -e "${BLUE}═══════════════════════════════════════${NC}"
        python3 scripts/deploy_character_swarms.py
        
        echo ""
        echo -e "${BLUE}═══════════════════════════════════════${NC}"
        echo -e "${BLUE}PHASE 3: FINAL INTEGRATION${NC}"
        echo -e "${BLUE}═══════════════════════════════════════${NC}"
        
        # Generate master inventory
        echo -e "${GREEN}📊 Generating master inventory...${NC}"
        
        # Count activations
        CHAR_COUNT=$(ls data/characters/*/activation_*.json 2>/dev/null | wc -l)
        SWARM_COUNT=$(ls data/swarms/*/*/swarm_*.json 2>/dev/null | wc -l)
        
        echo ""
        echo -e "${GREEN}═══════════════════════════════════════${NC}"
        echo -e "${GREEN}✅ ACTIVATION COMPLETE!${NC}"
        echo -e "${GREEN}═══════════════════════════════════════${NC}"
        echo ""
        echo "📊 Summary:"
        echo "  - Characters activated: $CHAR_COUNT"
        echo "  - Swarms deployed: $SWARM_COUNT"
        echo ""
        echo "📁 Data locations:"
        echo "  - Character data: data/characters/"
        echo "  - Swarm data: data/swarms/"
        echo ""
        echo "📝 Reports:"
        echo "  - Activation reports: data/characters/*/ACTIVATION_REPORT.md"
        echo "  - Session data: data/characters/session_*.json"
        ;;
    
    trinity)
        echo -e "${GREEN}🔱 Activating CORE TRINITY only (AION, ORACLE, GOANNA)...${NC}"
        echo ""
        echo "Note: This activates the three primary characters."
        echo "Support Pyramid (DOOFY, HIPPY, JARL) will not be activated."
        echo ""
        # Would need to modify activate_all_characters.py to support selective activation
        echo -e "${YELLOW}⚠️  Use 'full' mode to activate all characters${NC}"
        ;;
    
    status)
        echo -e "${GREEN}📊 CHARACTER ACTIVATION STATUS${NC}"
        echo ""
        
        # Check character activations
        if [ -d "data/characters" ]; then
            echo "Characters activated:"
            for char_dir in data/characters/*/; do
                if [ -d "$char_dir" ]; then
                    char_name=$(basename "$char_dir")
                    activation_count=$(ls "$char_dir"/activation_*.json 2>/dev/null | wc -l)
                    if [ $activation_count -gt 0 ]; then
                        echo -e "  ${GREEN}✅ $(echo $char_name | tr '[:lower:]' '[:upper:]')${NC} - $activation_count activation(s)"
                    fi
                fi
            done
        else
            echo "No character activations found."
        fi
        
        echo ""
        
        # Check swarms
        if [ -d "data/swarms" ]; then
            echo "Swarms deployed:"
            TOTAL_SWARMS=0
            for char_dir in data/swarms/*/; do
                if [ -d "$char_dir" ]; then
                    char_name=$(basename "$char_dir")
                    for swarm_type_dir in "$char_dir"*/; do
                        if [ -d "$swarm_type_dir" ]; then
                            swarm_type=$(basename "$swarm_type_dir")
                            swarm_count=$(ls "$swarm_type_dir"/swarm_*.json 2>/dev/null | wc -l)
                            if [ $swarm_count -gt 0 ]; then
                                echo -e "  ${BLUE}🐝 $(echo $char_name | tr '[:lower:]' '[:upper:]') - $swarm_type${NC} ($swarm_count swarm(s))"
                                TOTAL_SWARMS=$((TOTAL_SWARMS + swarm_count))
                            fi
                        fi
                    done
                fi
            done
            echo ""
            echo "Total swarms deployed: $TOTAL_SWARMS"
        else
            echo "No swarms deployed."
        fi
        ;;
    
    *)
        echo -e "${YELLOW}Usage: $0 [test|swarms|characters|full|trinity|status]${NC}"
        echo ""
        echo "Modes:"
        echo "  test       - Test activation infrastructure"
        echo "  swarms     - Deploy worker swarms only"
        echo "  characters - Activate characters only"
        echo "  full       - Complete activation (recommended)"
        echo "  trinity    - Activate CORE TRINITY only"
        echo "  status     - Check activation status"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✅ Done!${NC}"
