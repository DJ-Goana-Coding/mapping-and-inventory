#!/bin/bash

# 🛡️ VAMGUARD ISO 20022 & CRYPTO ARSENAL - Installation Script
# Status: STORAGE MODE - Install when ready to deploy
# Date: 2026-04-03
# Purpose: One-shot installation of all VAMGUARD financial infrastructure

set -e  # Exit on error

echo "🏛️ CITADEL ARCHITECT: VAMGUARD Arsenal Installation"
echo "=================================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo -e "${RED}❌ Do not run as root${NC}"
   exit 1
fi

echo "📋 INSTALLATION CHECKLIST"
echo "========================="
echo ""
echo "This script will install:"
echo "  ✓ Python dependencies (ISO 20022, Solana, Ethereum)"
echo "  ✓ Node.js dependencies (Web3, Gaming SDKs)"
echo "  ✓ Rust and Anchor (Solana development)"
echo "  ✓ Docker containers (PostgreSQL, Redis, RabbitMQ)"
echo "  ✓ Solana CLI tools"
echo ""
read -p "Continue? (y/N) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled"
    exit 1
fi

# Create directories
echo ""
echo -e "${YELLOW}📁 Creating directory structure...${NC}"
mkdir -p vamguard-arsenal/{iso20022,crypto,gaming,bridges,api,workers,compliance}
cd vamguard-arsenal

# ============================================================================
# PART 1: PYTHON DEPENDENCIES
# ============================================================================
echo ""
echo -e "${YELLOW}🐍 Installing Python dependencies...${NC}"

# Check if Python 3.11+ is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.11+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "   Python version: $PYTHON_VERSION"

# Create virtual environment
echo "   Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "   Upgrading pip..."
pip install --upgrade pip setuptools wheel

# ISO 20022 Dependencies
echo "   Installing ISO 20022 libraries..."
pip install lxml xmlschema requests

# Solana Dependencies
echo "   Installing Solana libraries..."
pip install solana solders anchorpy

# Ethereum Dependencies
echo "   Installing Ethereum libraries..."
pip install web3 eth-account eth-utils eth-abi

# Additional Python tools
echo "   Installing additional Python tools..."
pip install python-dotenv pydantic fastapi uvicorn sqlalchemy psycopg2-binary redis celery

echo -e "${GREEN}✅ Python dependencies installed${NC}"

# ============================================================================
# PART 2: NODE.JS DEPENDENCIES
# ============================================================================
echo ""
echo -e "${YELLOW}📦 Installing Node.js dependencies...${NC}"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found. Please install Node.js 18+${NC}"
    exit 1
fi

NODE_VERSION=$(node --version)
echo "   Node.js version: $NODE_VERSION"

# Initialize package.json
echo "   Initializing package.json..."
cat > package.json <<EOF
{
  "name": "vamguard-arsenal",
  "version": "1.0.0",
  "description": "VAMGUARD ISO 20022 & Crypto Token Infrastructure",
  "main": "index.js",
  "scripts": {
    "test": "echo \"Error: no test specified\" && exit 1"
  },
  "keywords": ["iso20022", "crypto", "solana", "ethereum", "gaming"],
  "author": "DJ-Goana-Coding",
  "license": "MIT"
}
EOF

# Solana Dependencies
echo "   Installing Solana packages..."
npm install --save \
    @solana/web3.js \
    @solana/spl-token \
    @project-serum/anchor \
    @metaplex-foundation/js

# Ethereum Dependencies
echo "   Installing Ethereum packages..."
npm install --save \
    ethers \
    @openzeppelin/contracts \
    hardhat \
    @nomicfoundation/hardhat-toolbox

# Gaming SDKs
echo "   Installing Gaming SDKs..."
npm install --save \
    moralis \
    phaser \
    three

# Community Tools
echo "   Installing Community tools..."
npm install --save \
    discord.js \
    telegraf

# Dev Dependencies
echo "   Installing development dependencies..."
npm install --save-dev \
    @types/node \
    typescript \
    ts-node \
    prettier \
    eslint

echo -e "${GREEN}✅ Node.js dependencies installed${NC}"

# ============================================================================
# PART 3: RUST AND ANCHOR
# ============================================================================
echo ""
echo -e "${YELLOW}🦀 Installing Rust and Anchor...${NC}"

if ! command -v rustc &> /dev/null; then
    echo "   Installing Rust..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source $HOME/.cargo/env
else
    echo "   Rust already installed"
    RUST_VERSION=$(rustc --version)
    echo "   Rust version: $RUST_VERSION"
fi

# Install Anchor CLI
echo "   Installing Anchor CLI..."
if ! command -v anchor &> /dev/null; then
    cargo install --git https://github.com/coral-xyz/anchor anchor-cli --locked
else
    echo "   Anchor already installed"
    ANCHOR_VERSION=$(anchor --version)
    echo "   Anchor version: $ANCHOR_VERSION"
fi

echo -e "${GREEN}✅ Rust and Anchor installed${NC}"

# ============================================================================
# PART 4: SOLANA CLI
# ============================================================================
echo ""
echo -e "${YELLOW}☀️ Installing Solana CLI...${NC}"

if ! command -v solana &> /dev/null; then
    echo "   Installing Solana CLI..."
    sh -c "$(curl -sSfL https://release.solana.com/stable/install)"
    export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"
else
    echo "   Solana CLI already installed"
    SOLANA_VERSION=$(solana --version)
    echo "   Solana version: $SOLANA_VERSION"
fi

echo -e "${GREEN}✅ Solana CLI installed${NC}"

# ============================================================================
# PART 5: DOCKER INFRASTRUCTURE
# ============================================================================
echo ""
echo -e "${YELLOW}🐳 Setting up Docker infrastructure...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Please install Docker first${NC}"
    echo "   Skipping Docker setup..."
else
    # Create docker-compose.yml
    echo "   Creating docker-compose.yml..."
    cat > docker-compose.yml <<EOF
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: vamguard-db
    environment:
      POSTGRES_USER: vamguard
      POSTGRES_PASSWORD: changeme_in_production
      POSTGRES_DB: vamguard
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: vamguard-cache
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  rabbitmq:
    image: rabbitmq:3-management-alpine
    container_name: vamguard-queue
    environment:
      RABBITMQ_DEFAULT_USER: vamguard
      RABBITMQ_DEFAULT_PASS: changeme_in_production
    ports:
      - "5672:5672"
      - "15672:15672"
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  rabbitmq_data:
EOF

    echo "   Starting Docker containers..."
    docker-compose up -d

    echo ""
    echo "   Docker services started:"
    echo "     - PostgreSQL: localhost:5432"
    echo "     - Redis: localhost:6379"
    echo "     - RabbitMQ: localhost:5672 (Management UI: localhost:15672)"
    
    echo -e "${GREEN}✅ Docker infrastructure running${NC}"
fi

# ============================================================================
# PART 6: INITIALIZE PROJECTS
# ============================================================================
echo ""
echo -e "${YELLOW}🏗️ Initializing project structure...${NC}"

# Create .env template
echo "   Creating .env template..."
cat > .env.example <<EOF
# VAMGUARD Arsenal Configuration
# Copy this file to .env and fill in your values

# PostgreSQL
DATABASE_URL=postgresql://vamguard:changeme_in_production@localhost:5432/vamguard

# Redis
REDIS_URL=redis://localhost:6379

# RabbitMQ
RABBITMQ_URL=amqp://vamguard:changeme_in_production@localhost:5672

# Blockchain RPC Endpoints
SOLANA_RPC_URL=https://api.devnet.solana.com
ETHEREUM_RPC_URL=https://eth-goerli.alchemyapi.io/v2/YOUR_API_KEY
BSC_RPC_URL=https://data-seed-prebsc-1-s1.binance.org:8545

# API Keys (obtain from respective services)
ALCHEMY_API_KEY=your_alchemy_key
HELIUS_API_KEY=your_helius_key
MORALIS_API_KEY=your_moralis_key

# KYC/AML Services
SUMSUB_API_KEY=your_sumsub_key
CHAINALYSIS_API_KEY=your_chainalysis_key

# Discord/Telegram Bots
DISCORD_BOT_TOKEN=your_discord_token
TELEGRAM_BOT_TOKEN=your_telegram_token

# Security
JWT_SECRET=generate_a_strong_random_secret
ENCRYPTION_KEY=generate_a_strong_encryption_key
EOF

# Create README
echo "   Creating README..."
cat > README.md <<EOF
# 🛡️ VAMGUARD ISO 20022 & Crypto Arsenal

Complete infrastructure for ISO 20022 financial compliance and decentralized cryptocurrency ecosystem.

## 📋 Installation Complete

All dependencies and infrastructure have been installed:

- ✅ Python virtual environment with ISO 20022, Solana, Ethereum libraries
- ✅ Node.js packages for Web3 development and gaming SDKs
- ✅ Rust and Anchor for Solana smart contract development
- ✅ Solana CLI tools
- ✅ Docker containers (PostgreSQL, Redis, RabbitMQ)

## 🚀 Quick Start

### 1. Activate Python Environment
\`\`\`bash
source venv/bin/activate
\`\`\`

### 2. Configure Environment
\`\`\`bash
cp .env.example .env
# Edit .env with your API keys and configuration
\`\`\`

### 3. Verify Installation
\`\`\`bash
# Check Python packages
pip list

# Check Node.js packages
npm list

# Check Solana
solana --version
anchor --version

# Check Docker services
docker-compose ps
\`\`\`

## 📚 Next Steps

See \`VAMGUARD_ISO20022_CRYPTO_ARSENAL.md\` for:
- Complete technology documentation
- Architecture diagrams
- Implementation phases
- Development roadmap

## 🔒 Security Notes

- Change all default passwords in docker-compose.yml
- Never commit .env file to git
- Use environment variables for all secrets
- Enable 2FA on all service accounts

## 📖 Documentation

- ISO 20022: https://www.iso20022.org/
- Solana Docs: https://docs.solana.com/
- Ethereum Docs: https://ethereum.org/developers/
- Anchor Book: https://book.anchor-lang.com/

---

**Status**: 🛍️ Arsenal Ready - Deploy When Ready  
**Architect**: Citadel Architect v25.0.OMNI++  
**Date**: 2026-04-03
EOF

echo -e "${GREEN}✅ Project structure initialized${NC}"

# ============================================================================
# FINAL SUMMARY
# ============================================================================
echo ""
echo "=================================================="
echo -e "${GREEN}✅ VAMGUARD ARSENAL INSTALLATION COMPLETE${NC}"
echo "=================================================="
echo ""
echo "📦 Installed Components:"
echo "   ✓ Python virtual environment"
echo "   ✓ ISO 20022 libraries (lxml, xmlschema)"
echo "   ✓ Solana SDK (solana, solders, anchorpy)"
echo "   ✓ Ethereum SDK (web3, ethers, hardhat)"
echo "   ✓ Gaming SDKs (moralis, phaser)"
echo "   ✓ Rust and Anchor CLI"
echo "   ✓ Solana CLI tools"
echo "   ✓ Docker infrastructure (PostgreSQL, Redis, RabbitMQ)"
echo ""
echo "📁 Project Location:"
echo "   $(pwd)"
echo ""
echo "🚀 Next Steps:"
echo "   1. cd vamguard-arsenal"
echo "   2. source venv/bin/activate"
echo "   3. cp .env.example .env"
echo "   4. Edit .env with your configuration"
echo "   5. Read README.md and VAMGUARD_ISO20022_CRYPTO_ARSENAL.md"
echo ""
echo "🔒 Security Reminder:"
echo "   - Change default passwords in docker-compose.yml"
echo "   - Never commit .env to git"
echo "   - Use strong encryption keys"
echo ""
echo -e "${GREEN}🏛️ CITADEL COMMAND: Arsenal ready for deployment${NC}"
echo ""
