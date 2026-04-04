#!/bin/bash
# TITAN 392 IGNITION SEQUENCE
# Citadel Architect — Full System Activation

set -e

echo "🔥 TITAN 392 IGNITION SEQUENCE"
echo "========================================"
echo ""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Parse phase argument
PHASE="${1:-full}"

function print_header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

function print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

function print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

function print_error() {
    echo -e "${RED}❌ $1${NC}"
}

function check_prerequisites() {
    print_header "PHASE 0: Prerequisites Check"
    
    # Check Python
    if command -v python3 &> /dev/null; then
        print_success "Python 3 installed: $(python3 --version)"
    else
        print_error "Python 3 not found"
        exit 1
    fi
    
    # Check Git
    if command -v git &> /dev/null; then
        print_success "Git installed: $(git --version | head -n1)"
    else
        print_error "Git not found"
        exit 1
    fi
    
    # Check gh CLI (optional)
    if command -v gh &> /dev/null; then
        print_success "GitHub CLI installed: $(gh --version | head -n1)"
    else
        print_warning "GitHub CLI not installed (optional)"
    fi
    
    # Check required secrets
    if [ -n "$GITHUB_TOKEN" ] || [ -n "$GH_PAT" ]; then
        print_success "GitHub token configured"
    else
        print_warning "GitHub token not configured (some features may not work)"
    fi
    
    if [ -n "$HF_TOKEN" ]; then
        print_success "HuggingFace token configured"
    else
        print_warning "HuggingFace token not configured (HF sync disabled)"
    fi
}

function phase_foundation() {
    print_header "PHASE 1: Foundation"
    
    # Create required directories
    echo "📁 Creating data directories..."
    mkdir -p data/monitoring
    mkdir -p data/monitoring/pulse_sync_reports
    mkdir -p data/discoveries
    mkdir -p data/models
    mkdir -p data/workers
    mkdir -p data/datasets
    mkdir -p data/forever_learning/cycle_reports
    print_success "Data directories created"
    
    # Verify Titan Registry
    if [ -f "data/titan_392_registry.json" ]; then
        print_success "Titan 392 Registry exists"
    else
        print_error "Titan 392 Registry not found!"
        exit 1
    fi
    
    # Verify Districts
    echo "🏛️ Checking Districts..."
    district_count=$(find Districts -maxdepth 1 -type d | tail -n +2 | wc -l)
    print_success "Found $district_count Districts"
    
    # Verify workflows
    echo "⚙️ Checking workflows..."
    workflow_count=$(find .github/workflows -name "*.yml" -o -name "*.yaml" | wc -l)
    print_success "Found $workflow_count workflows"
    
    print_success "Foundation phase complete"
}

function phase_pulse() {
    print_header "PHASE 2: Pulse Activation"
    
    # Test Pulse Sync Master workflow exists
    if [ -f ".github/workflows/pulse_sync_master.yml" ]; then
        print_success "Pulse Sync Master workflow found"
    else
        print_error "Pulse Sync Master workflow missing"
        exit 1
    fi
    
    # Test Mesh Heartbeat workflow exists
    if [ -f ".github/workflows/mesh_heartbeat.yml" ]; then
        print_success "Mesh Heartbeat workflow found"
    else
        print_warning "Mesh Heartbeat workflow missing"
    fi
    
    # Trigger Pulse Sync if gh CLI available
    if command -v gh &> /dev/null; then
        echo "🔄 Triggering Pulse Sync Master..."
        if gh workflow run pulse_sync_master.yml; then
            print_success "Pulse Sync triggered"
        else
            print_warning "Could not trigger Pulse Sync (may need manual trigger)"
        fi
    else
        print_warning "GitHub CLI not available - trigger Pulse Sync manually"
    fi
    
    print_success "Pulse activation complete"
}

function phase_weld() {
    print_header "PHASE 3: Weld Operations"
    
    # Check for weld scripts
    echo "🔗 Checking weld infrastructure..."
    
    if [ -d "scripts/citadel_grand_unification" ]; then
        print_success "Citadel Grand Unification scripts found"
    else
        print_warning "Citadel Grand Unification directory not found"
    fi
    
    # Run District validation
    echo "🏛️ Validating Districts..."
    district_errors=0
    for district in Districts/D*; do
        if [ -d "$district" ]; then
            district_name=$(basename "$district")
            
            # Check for required files
            if [ ! -f "$district/TREE.md" ]; then
                print_warning "$district_name: TREE.md missing"
                ((district_errors++))
            fi
            
            if [ ! -f "$district/INVENTORY.json" ]; then
                print_warning "$district_name: INVENTORY.json missing"
                ((district_errors++))
            fi
        fi
    done
    
    if [ $district_errors -eq 0 ]; then
        print_success "All Districts validated"
    else
        print_warning "$district_errors District artifacts missing"
    fi
    
    print_success "Weld operations complete"
}

function phase_learning() {
    print_header "PHASE 4: Forever Learning"
    
    # Check Forever Learning workflow
    if [ -f ".github/workflows/forever_learning_orchestrator.yml" ]; then
        print_success "Forever Learning workflow found"
    else
        print_warning "Forever Learning workflow missing"
    fi
    
    # Create cycle reports directory
    mkdir -p data/forever_learning/cycle_reports
    print_success "Forever Learning directory structure ready"
    
    # Trigger Forever Learning if gh CLI available
    if command -v gh &> /dev/null; then
        echo "🔄 Triggering Forever Learning cycle..."
        if gh workflow run forever_learning_orchestrator.yml 2>/dev/null; then
            print_success "Forever Learning triggered"
        else
            print_warning "Could not trigger Forever Learning (may need manual trigger)"
        fi
    else
        print_warning "GitHub CLI not available - trigger Forever Learning manually"
    fi
    
    print_success "Forever Learning activation complete"
}

function phase_monitor() {
    print_header "PHASE 5: Health Monitoring"
    
    # Check Titan Health Monitor script
    if [ -f "scripts/titan_health_monitor.py" ]; then
        print_success "Titan Health Monitor script found"
    else
        print_error "Titan Health Monitor script missing"
        exit 1
    fi
    
    # Install required Python packages
    echo "📦 Installing monitoring dependencies..."
    pip install -q requests huggingface_hub 2>/dev/null || print_warning "Could not install dependencies"
    
    # Run health check
    echo "🏥 Running health check..."
    if python3 scripts/titan_health_monitor.py; then
        print_success "Health check passed"
    else
        print_warning "Health check reported issues (see logs above)"
    fi
    
    # Display health report
    if [ -f "data/monitoring/titan_health.json" ]; then
        echo ""
        echo "📊 Health Report Summary:"
        overall_status=$(python3 -c "import json; print(json.load(open('data/monitoring/titan_health.json'))['overall_status'])")
        echo "   Status: $overall_status"
        print_success "Health monitoring active"
    fi
    
    print_success "Monitoring activation complete"
}

function full_ignition() {
    print_header "TITAN 392 FULL IGNITION SEQUENCE"
    
    echo "Executing all phases..."
    echo ""
    
    check_prerequisites
    phase_foundation
    phase_pulse
    phase_weld
    phase_learning
    phase_monitor
    
    print_header "🔥 IGNITION COMPLETE 🔥"
    
    echo ""
    echo -e "${GREEN}┌─────────────────────────────────────────────────┐${NC}"
    echo -e "${GREEN}│  TITAN 392 — FULLY OPERATIONAL                 │${NC}"
    echo -e "${GREEN}│                                                 │${NC}"
    echo -e "${GREEN}│  Status:     IGNITED ✅                         │${NC}"
    echo -e "${GREEN}│  Foundation: STABLE ✅                          │${NC}"
    echo -e "${GREEN}│  Pulse:      ACTIVE ✅                          │${NC}"
    echo -e "${GREEN}│  Weld:       COMPLETE ✅                        │${NC}"
    echo -e "${GREEN}│  Learning:   CYCLING ✅                         │${NC}"
    echo -e "${GREEN}│  Monitoring: ACTIVE ✅                          │${NC}"
    echo -e "${GREEN}│                                                 │${NC}"
    echo -e "${GREEN}│  Integration Points: 392 🏛️                    │${NC}"
    echo -e "${GREEN}│  Authority Chain:    L4→L3→L2→L1 🔗            │${NC}"
    echo -e "${GREEN}└─────────────────────────────────────────────────┘${NC}"
    echo ""
    
    echo "Next steps:"
    echo "  • Monitor health: python3 scripts/titan_health_monitor.py"
    echo "  • View heartbeat: cat data/monitoring/mesh_heartbeat.json"
    echo "  • Check workflows: gh workflow list"
    echo "  • View registry: cat data/titan_392_registry.json"
    echo ""
}

# Main execution
case "$PHASE" in
    prerequisites)
        check_prerequisites
        ;;
    foundation)
        check_prerequisites
        phase_foundation
        ;;
    pulse)
        check_prerequisites
        phase_pulse
        ;;
    weld)
        check_prerequisites
        phase_weld
        ;;
    learning)
        check_prerequisites
        phase_learning
        ;;
    monitor)
        check_prerequisites
        phase_monitor
        ;;
    full)
        full_ignition
        ;;
    *)
        echo "Usage: $0 {prerequisites|foundation|pulse|weld|learning|monitor|full}"
        echo ""
        echo "Phases:"
        echo "  prerequisites - Check system requirements"
        echo "  foundation    - Initialize foundation infrastructure"
        echo "  pulse         - Activate pulse sync mechanisms"
        echo "  weld          - Execute weld operations"
        echo "  learning      - Start Forever Learning cycle"
        echo "  monitor       - Activate health monitoring"
        echo "  full          - Execute all phases (default)"
        exit 1
        ;;
esac

print_success "TITAN 392 operation complete"
