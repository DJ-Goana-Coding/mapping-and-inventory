#!/bin/bash
###############################################################################
# 🏛️ AGENT LEGION QUICKSTART
# Q.G.T.N.L. Command Citadel - Agent Legion Framework
#
# Purpose: One-command deployment of entire Agent Legion
# Authority: Citadel Architect v26.0.LEGION+
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Banner
echo -e "${PURPLE}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║              🏛️  AGENT LEGION FRAMEWORK  🏛️                  ║
║                                                              ║
║       Q.G.T.N.L. Command Citadel - Autonomous Agents        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python 3 found${NC}"

# Create directories
echo -e "\n${CYAN}📁 Creating directory structure...${NC}"
mkdir -p data/agent_legion
mkdir -p data/security/{reports,quarantine,baselines,removed_targets_backup}
mkdir -p data/teaching/{reports,curricula}
mkdir -p data/reconnaissance/reports
mkdir -p data/workers/reports
mkdir -p data/bridge_transfers
mkdir -p data/rag_brains/{security,teaching,supply,technical,spiritual,integration}
mkdir -p data/forever_learning/reports
mkdir -p data/Mapping-and-Inventory-storage/forever_learning

echo -e "${GREEN}✅ Directories created${NC}"

# Parse arguments
MODE="${1:-security}"

case "$MODE" in
    security)
        echo -e "\n${BLUE}🛡️  DEPLOYING SECURITY TEAM${NC}"
        echo -e "${CYAN}═══════════════════════════${NC}\n"
        
        echo -e "${YELLOW}👻 Wraith Security Agent...${NC}"
        python3 scripts/agent_legion/wraith_security_agent.py || true
        
        echo -e "\n${YELLOW}🐕 Hound Tracker Agent...${NC}"
        python3 scripts/agent_legion/hound_tracker_agent.py || true
        
        echo -e "\n${YELLOW}🛡️  Sentinel Defensive Agent...${NC}"
        python3 scripts/agent_legion/sentinel_defensive_agent.py || true
        ;;
    
    teaching)
        echo -e "\n${BLUE}🌀 DEPLOYING TEACHING TEAM${NC}"
        echo -e "${CYAN}═══════════════════════════${NC}\n"
        
        echo -e "${YELLOW}🌀 TIA Teaching Agent...${NC}"
        python3 scripts/agent_legion/tia_teaching_agent.py || true
        ;;
    
    workers)
        echo -e "\n${BLUE}🌊 DEPLOYING AUTONOMOUS WORKERS${NC}"
        echo -e "${CYAN}═══════════════════════════════${NC}\n"
        
        echo -e "${YELLOW}🌊 Bridge Worker...${NC}"
        python3 scripts/agent_legion/bridge_worker.py || true
        
        echo -e "\n${YELLOW}📚 Learning Collector...${NC}"
        python3 scripts/agent_legion/learning_collector.py || true
        ;;
    
    rag)
        echo -e "\n${BLUE}🧠 DEPLOYING MULTI-BRAIN RAG SYSTEM${NC}"
        echo -e "${CYAN}════════════════════════════════════${NC}\n"
        
        echo -e "${YELLOW}🧠 Multi-Brain RAG System...${NC}"
        python3 scripts/agent_legion/multi_brain_rag_system.py || true
        ;;
    
    all)
        echo -e "\n${BLUE}🏛️  FULL AGENT LEGION DEPLOYMENT${NC}"
        echo -e "${CYAN}═════════════════════════════════${NC}\n"
        
        # Security Team
        echo -e "${PURPLE}═══ SECURITY TEAM ═══${NC}"
        python3 scripts/agent_legion/wraith_security_agent.py || true
        python3 scripts/agent_legion/hound_tracker_agent.py || true
        python3 scripts/agent_legion/sentinel_defensive_agent.py || true
        
        # Teaching Team
        echo -e "\n${PURPLE}═══ TEACHING TEAM ═══${NC}"
        python3 scripts/agent_legion/tia_teaching_agent.py || true
        
        # Workers
        echo -e "\n${PURPLE}═══ AUTONOMOUS WORKERS ═══${NC}"
        python3 scripts/agent_legion/bridge_worker.py || true
        python3 scripts/agent_legion/learning_collector.py || true
        
        # RAG
        echo -e "\n${PURPLE}═══ MULTI-BRAIN RAG ═══${NC}"
        python3 scripts/agent_legion/multi_brain_rag_system.py || true
        ;;
    
    orchestrate)
        echo -e "\n${BLUE}🏛️  ORCHESTRATED DEPLOYMENT${NC}"
        echo -e "${CYAN}═══════════════════════════${NC}\n"
        
        python3 scripts/agent_legion/agent_legion_orchestrator.py
        ;;
    
    *)
        echo -e "${RED}❌ Invalid mode: $MODE${NC}"
        echo ""
        echo "Usage: $0 [mode]"
        echo ""
        echo "Modes:"
        echo "  security    - Deploy security team (default)"
        echo "  teaching    - Deploy teaching team"
        echo "  workers     - Deploy autonomous workers"
        echo "  rag         - Deploy RAG system"
        echo "  all         - Deploy all agents"
        echo "  orchestrate - Use orchestrator"
        exit 1
        ;;
esac

# Summary
echo -e "\n${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                 DEPLOYMENT COMPLETE                      ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"

# Count reports
SECURITY_REPORTS=$(find data/security/reports -type f 2>/dev/null | wc -l)
TEACHING_REPORTS=$(find data/teaching/reports -type f 2>/dev/null | wc -l)
WORKER_REPORTS=$(find data/workers/reports -type f 2>/dev/null | wc -l)
LEARNING_REPORTS=$(find data/forever_learning/reports -type f 2>/dev/null | wc -l)

echo -e "\n${CYAN}📊 Report Summary:${NC}"
echo -e "  Security Reports: ${YELLOW}$SECURITY_REPORTS${NC}"
echo -e "  Teaching Reports: ${YELLOW}$TEACHING_REPORTS${NC}"
echo -e "  Worker Reports: ${YELLOW}$WORKER_REPORTS${NC}"
echo -e "  Learning Reports: ${YELLOW}$LEARNING_REPORTS${NC}"

echo -e "\n${CYAN}📁 Data Locations:${NC}"
echo -e "  Security: ${BLUE}data/security/${NC}"
echo -e "  Teaching: ${BLUE}data/teaching/${NC}"
echo -e "  Workers: ${BLUE}data/workers/${NC}"
echo -e "  RAG Brains: ${BLUE}data/rag_brains/${NC}"
echo -e "  Forever Learning: ${BLUE}data/forever_learning/${NC}"
echo -e "  Mapping Storage: ${BLUE}data/Mapping-and-Inventory-storage/${NC}"

echo -e "\n${GREEN}✅ Agent Legion deployment complete!${NC}\n"
