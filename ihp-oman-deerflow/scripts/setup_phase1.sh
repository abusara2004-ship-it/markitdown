#!/bin/bash
#
# IHP Oman DeerFlow - Phase 1 Setup Script
# Automates setup and infrastructure initialization
#

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}IHP Oman DeerFlow - Phase 1 Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Step 1: Check Python version
echo -e "${BLUE}[1/7] Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
if [[ ! "$python_version" =~ ^3\.[8-9] ]] && [[ ! "$python_version" =~ ^3\.1[0-2] ]]; then
    echo -e "${RED}✗ Python 3.8+ required (found $python_version)${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python $python_version found${NC}"
echo ""

# Step 2: Create directories
echo -e "${BLUE}[2/7] Creating directory structure...${NC}"
mkdir -p .deer-flow/{logs,agent_outputs,cache}
mkdir -p database
mkdir -p scripts
mkdir -p agents
mkdir -p skills/public/{rfq-monitor,principal-coordination,compliance-tracking,vdp-analysis,collections-management}
mkdir -p integrations
mkdir -p tests
echo -e "${GREEN}✓ Directory structure created${NC}"
echo ""

# Step 3: Setup Python virtual environment
echo -e "${BLUE}[3/7] Setting up Python virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠ Virtual environment already exists${NC}"
fi

# Activate virtual environment
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Step 4: Install dependencies
echo -e "${BLUE}[4/7] Installing Python dependencies...${NC}"
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Step 5: Create .env file
echo -e "${BLUE}[5/7] Setting up environment configuration...${NC}"
if [ ! -f ".env" ]; then
    cp config/.env.example .env
    echo -e "${YELLOW}⚠ Created .env from template - please configure with actual credentials${NC}"
    echo -e "${YELLOW}  Edit .env and add your API keys, database URL, email addresses${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi
echo ""

# Step 6: Initialize database
echo -e "${BLUE}[6/7] Initializing database...${NC}"
python3 scripts/init_db.py
echo ""

# Step 7: Verify configuration
echo -e "${BLUE}[7/7] Verifying configuration...${NC}"
if [ -f ".env" ] && [ -f "config/config.yaml" ] && [ -f "config/extensions_config.json" ]; then
    echo -e "${GREEN}✓ Configuration files verified${NC}"
else
    echo -e "${RED}✗ Missing configuration files${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Phase 1 Setup Complete${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Edit .env with your actual credentials:"
echo "   - ANTHROPIC_API_KEY"
echo "   - Database paths and email addresses"
echo ""
echo "2. Verify database initialization:"
echo "   sqlite3 .deer-flow/ihp_oman.db 'SELECT COUNT(*) FROM vdp_tracking;'"
echo ""
echo "3. Test DeerFlow installation:"
echo "   source venv/bin/activate"
echo "   python3 -c 'import deerflow; print(deerflow.__version__)'"
echo ""
echo "4. Ready to proceed to Phase 2: Agent Deployment"
echo ""
