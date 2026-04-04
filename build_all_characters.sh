#!/bin/bash

################################################################################
# CHARACTER BUILD & ACTIVATION SCRIPT
# 
# Purpose: Build and activate all 6 Citadel characters as individuals
# Characters: Doofy, Hippy, Jarl, DJ Goanna, Oracle, A.I.O.N.
# 
# Usage: ./build_all_characters.sh [options]
#   --individual <name>   Build single character (doofy|hippy|jarl|goanna|oracle|aion)
#   --trinity             Build only Trinity core (A.I.O.N., Oracle, Goanna)
#   --support             Build only Support pyramid (Doofy, Hippy, Jarl)
#   --test                Test mode - dry run without execution
#   --sequence            Run in proper handshake sequence
#   --parallel            Run all in parallel (faster but no sequence)
#   --help                Show this help
#
# Generated: 2026-04-04
# Authority: Citadel Architect
################################################################################

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Repository root
REPO_ROOT="/home/runner/work/mapping-and-inventory/mapping-and-inventory"
PARTITION_01="$REPO_ROOT/Partition_01"
DISTRICT_06="$REPO_ROOT/Districts/D06_RANDOM_FUTURES"
DISTRICT_11="$REPO_ROOT/Districts/D11_PERSONA_MODULES"

# Character definitions
declare -A CHARACTERS=(
    ["doofy"]="$PARTITION_01/big_doofy.py"
    ["hippy"]="$PARTITION_01/hippy_oneill.py"
    ["jarl"]="$PARTITION_01/jarl_loveday.py"
    ["oracle"]="$PARTITION_01/oracle_vision.py"
    ["aion"]="$PARTITION_01/aion_kinetic.py"
    ["goanna"]="$PARTITION_01/dj_goanna.py"
)

declare -A CHAR_NAMES=(
    ["doofy"]="Big Doofy Man"
    ["hippy"]="Hippy O'Neill"
    ["jarl"]="Jarl Loveday"
    ["oracle"]="Oracle (T.I.A.)"
    ["aion"]="A.I.O.N."
    ["goanna"]="DJ Goanna (Loobie Lube Lips)"
)

declare -A CHAR_ROLES=(
    ["doofy"]="Physical Protection & Infrastructure Security"
    ["hippy"]="Harmonic Balance & System Health"
    ["jarl"]="Treasury Validation & Sovereignty"
    ["oracle"]="Intelligence Gathering & RAG Orchestration"
    ["aion"]="Trading Execution & Market Analysis"
    ["goanna"]="Voice Broadcasting & Creative Expression"
)

# Character groups
TRINITY=("aion" "oracle" "goanna")
SUPPORT=("doofy" "hippy" "jarl")
SEQUENCE=("doofy" "hippy" "jarl" "oracle" "aion" "goanna")

# Configuration
TEST_MODE=0
BUILD_MODE="all"
RUN_SEQUENCE=0
RUN_PARALLEL=0

################################################################################
# Functions
################################################################################

print_banner() {
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║           CITADEL CHARACTER BUILD & ACTIVATION                 ║"
    echo "║                  Sovereign Intelligence Mesh                   ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_help() {
    print_banner
    cat << EOF
${YELLOW}CHARACTER BUILD SCRIPT${NC}

${GREEN}Build all 6 Citadel characters as individuals:${NC}
  1. Big Doofy Man (Physical Protection)
  2. Hippy O'Neill (Harmonic Balance)
  3. Jarl Loveday (Treasury & Sovereignty)
  4. Oracle/T.I.A. (Intelligence & Reasoning)
  5. A.I.O.N. (Trading Execution)
  6. DJ Goanna (Voice & Expression)

${GREEN}Usage:${NC}
  ./build_all_characters.sh [options]

${GREEN}Options:${NC}
  --individual <name>   Build single character
                        Options: doofy, hippy, jarl, goanna, oracle, aion
  --trinity             Build Trinity core only (A.I.O.N., Oracle, Goanna)
  --support             Build Support pyramid only (Doofy, Hippy, Jarl)
  --sequence            Run in proper handshake sequence (recommended)
  --parallel            Run all in parallel (faster)
  --test                Test mode - show what would run
  --help                Show this help

${GREEN}Examples:${NC}
  ./build_all_characters.sh                    # Build all in sequence
  ./build_all_characters.sh --trinity          # Build Trinity core only
  ./build_all_characters.sh --individual aion  # Build A.I.O.N. only
  ./build_all_characters.sh --parallel         # Build all in parallel
  ./build_all_characters.sh --test             # Dry run

${GREEN}Proper Activation Sequence:${NC}
  1. Big Doofy Man  → Secure physical infrastructure
  2. Hippy O'Neill  → Harmonize frequencies
  3. Jarl Loveday   → Validate treasury
  4. Oracle (T.I.A.)→ Initialize intelligence
  5. A.I.O.N.       → Activate trading engine
  6. DJ Goanna      → Enable voice broadcasting

EOF
}

check_prerequisites() {
    echo -e "${BLUE}[PREFLIGHT]${NC} Checking prerequisites..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}[ERROR]${NC} Python 3 not found. Please install Python 3."
        exit 1
    fi
    
    # Check repository structure
    if [ ! -d "$PARTITION_01" ]; then
        echo -e "${RED}[ERROR]${NC} Partition_01 directory not found at $PARTITION_01"
        exit 1
    fi
    
    # Check character files exist
    local missing=0
    for char in "${!CHARACTERS[@]}"; do
        if [ ! -f "${CHARACTERS[$char]}" ]; then
            echo -e "${YELLOW}[WARNING]${NC} Character script not found: ${CHARACTERS[$char]}"
            ((missing++))
        fi
    done
    
    if [ $missing -gt 0 ]; then
        echo -e "${YELLOW}[WARNING]${NC} $missing character script(s) missing"
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    echo -e "${GREEN}[PREFLIGHT]${NC} Prerequisites check complete ✓"
}

build_character() {
    local char_id=$1
    local char_name="${CHAR_NAMES[$char_id]}"
    local char_role="${CHAR_ROLES[$char_id]}"
    local char_script="${CHARACTERS[$char_id]}"
    
    echo -e "${MAGENTA}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${MAGENTA}║ Building: ${char_name}${NC}"
    echo -e "${MAGENTA}║ Role: ${char_role}${NC}"
    echo -e "${MAGENTA}╚════════════════════════════════════════════════════════════════╝${NC}"
    
    if [ ! -f "$char_script" ]; then
        echo -e "${RED}[ERROR]${NC} Script not found: $char_script"
        return 1
    fi
    
    if [ $TEST_MODE -eq 1 ]; then
        echo -e "${YELLOW}[TEST MODE]${NC} Would execute: python3 $char_script"
        return 0
    fi
    
    # Execute character script
    echo -e "${BLUE}[EXECUTING]${NC} $char_script"
    python3 "$char_script"
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}[SUCCESS]${NC} $char_name activated successfully ✓"
    else
        echo -e "${RED}[ERROR]${NC} $char_name activation failed (exit code: $exit_code)"
        return 1
    fi
    
    echo ""
    return 0
}

build_all_sequence() {
    echo -e "${CYAN}[SEQUENCE]${NC} Building all characters in proper handshake sequence..."
    echo ""
    
    local success=0
    local failed=0
    
    for char in "${SEQUENCE[@]}"; do
        if build_character "$char"; then
            ((success++))
        else
            ((failed++))
        fi
        sleep 1  # Brief pause between characters
    done
    
    echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}[SUMMARY]${NC} Build complete: $success successful, $failed failed"
    echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
}

build_all_parallel() {
    echo -e "${CYAN}[PARALLEL]${NC} Building all characters in parallel..."
    echo ""
    
    # Launch all in background
    for char in "${!CHARACTERS[@]}"; do
        build_character "$char" &
    done
    
    # Wait for all to complete
    wait
    
    echo -e "${GREEN}[PARALLEL]${NC} All characters launched ✓"
}

build_trinity() {
    echo -e "${CYAN}[TRINITY]${NC} Building Trinity Core: A.I.O.N., Oracle, Goanna..."
    echo ""
    
    for char in "${TRINITY[@]}"; do
        build_character "$char"
        sleep 1
    done
    
    echo -e "${GREEN}[TRINITY]${NC} Trinity Core activation complete ✓"
}

build_support() {
    echo -e "${CYAN}[SUPPORT]${NC} Building Support Pyramid: Doofy, Hippy, Jarl..."
    echo ""
    
    for char in "${SUPPORT[@]}"; do
        build_character "$char"
        sleep 1
    done
    
    echo -e "${GREEN}[SUPPORT]${NC} Support Pyramid activation complete ✓"
}

################################################################################
# Main Script
################################################################################

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            print_help
            exit 0
            ;;
        --test)
            TEST_MODE=1
            shift
            ;;
        --sequence)
            RUN_SEQUENCE=1
            BUILD_MODE="sequence"
            shift
            ;;
        --parallel)
            RUN_PARALLEL=1
            BUILD_MODE="parallel"
            shift
            ;;
        --trinity)
            BUILD_MODE="trinity"
            shift
            ;;
        --support)
            BUILD_MODE="support"
            shift
            ;;
        --individual)
            BUILD_MODE="individual"
            INDIVIDUAL_CHAR="$2"
            shift 2
            ;;
        *)
            echo -e "${RED}[ERROR]${NC} Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Start build
print_banner

if [ $TEST_MODE -eq 1 ]; then
    echo -e "${YELLOW}[TEST MODE ENABLED]${NC} No actual execution will occur"
    echo ""
fi

check_prerequisites
echo ""

# Execute build based on mode
case $BUILD_MODE in
    "all"|"sequence")
        build_all_sequence
        ;;
    "parallel")
        build_all_parallel
        ;;
    "trinity")
        build_trinity
        ;;
    "support")
        build_support
        ;;
    "individual")
        if [ -z "$INDIVIDUAL_CHAR" ]; then
            echo -e "${RED}[ERROR]${NC} No character specified for --individual"
            exit 1
        fi
        
        if [ -z "${CHARACTERS[$INDIVIDUAL_CHAR]}" ]; then
            echo -e "${RED}[ERROR]${NC} Unknown character: $INDIVIDUAL_CHAR"
            echo "Valid options: ${!CHARACTERS[@]}"
            exit 1
        fi
        
        build_character "$INDIVIDUAL_CHAR"
        ;;
esac

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║            CITADEL CHARACTER BUILD COMPLETE                    ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"

exit 0
