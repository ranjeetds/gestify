#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

clear
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    ${GREEN}🎮 Gestify Setup v2.0${BLUE}            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}\n"

# Check Python version
echo -e "${YELLOW}⚙️  Checking Python version...${NC}"
python3 --version

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.8 or higher.${NC}"
    exit 1
fi

# Check Python version is 3.8+
python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Python 3.8 or higher is required${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python version OK${NC}"

# Create virtual environment
echo -e "\n${YELLOW}📦 Creating virtual environment...${NC}"
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to create virtual environment${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Virtual environment created${NC}"

# Activate virtual environment
echo -e "\n${YELLOW}🔧 Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "\n${YELLOW}📈 Upgrading pip...${NC}"
pip install --upgrade pip --quiet

# Install requirements
echo -e "\n${YELLOW}📥 Installing dependencies...${NC}"
echo -e "${BLUE}   This may take a few minutes...${NC}\n"
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to install dependencies${NC}"
    exit 1
fi

echo -e "\n${GREEN}✅ Dependencies installed${NC}"

# Install package in development mode
echo -e "\n${YELLOW}🔨 Installing Gestify package...${NC}"
pip install -e .

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to install package${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Gestify package installed${NC}"

# Test installation
echo -e "\n${YELLOW}🧪 Testing installation...${NC}"
python3 test_setup.py

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Installation test failed${NC}"
    exit 1
fi

echo -e "\n${GREEN}✅ All tests passed!${NC}"

# Print success message
echo -e "\n${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    ${GREEN}✅ Setup Complete!${BLUE}                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}\n"

echo -e "${YELLOW}🚀 Quick Start:${NC}\n"
echo -e "1. Activate virtual environment:"
echo -e "   ${GREEN}source venv/bin/activate${NC}\n"
echo -e "2. Run Gestify:"
echo -e "   ${GREEN}gestify${NC}                 # Command line"
echo -e "   ${GREEN}python run_gestify.py${NC}   # Direct script\n"
echo -e "3. Try different modes:"
echo -e "   ${GREEN}gestify --fast${NC}          # Fast mode"
echo -e "   ${GREEN}gestify --accurate${NC}      # Accurate mode"
echo -e "   ${GREEN}gestify --two-hand${NC}      # Two-hand mode\n"
echo -e "4. Get help:"
echo -e "   ${GREEN}gestify --help${NC}\n"

echo -e "${BLUE}📖 See README.md for full documentation${NC}"
echo -e "${BLUE}🐛 Issues? Check fix_camera.sh or README troubleshooting section${NC}\n"
