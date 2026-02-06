#!/bin/bash

# MJ SEO - Backend Setup Script for Production
# This script sets up the backend for production deployment

set -e  # Exit on any error

echo "====================================="
echo "MJ SEO - Backend Production Setup"
echo "====================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$SCRIPT_DIR/backend"

cd "$BACKEND_DIR"

echo -e "${YELLOW}Step 1: Checking Python version...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}$PYTHON_VERSION${NC}"
echo ""

echo -e "${YELLOW}Step 2: Setting up production environment...${NC}"
if [ -f ".env.production" ]; then
    cp .env.production .env
    echo -e "${GREEN}Production environment file copied${NC}"
    echo ""
    echo -e "${RED}IMPORTANT: Edit .env file and update:${NC}"
    echo -e "${YELLOW}1. DATABASE_URL with your PostgreSQL credentials${NC}"
    echo -e "${YELLOW}2. SECRET_KEY with a secure random key${NC}"
    echo -e "${YELLOW}3. API keys if needed${NC}"
    echo ""
    read -p "Have you updated the .env file? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Please update .env file and run this script again${NC}"
        exit 1
    fi
else
    echo -e "${RED}Warning: .env.production not found. Using existing .env${NC}"
fi
echo ""

echo -e "${YELLOW}Step 3: Creating virtual environment...${NC}"
if [ -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment already exists. Skipping...${NC}"
else
    python3 -m venv venv
    echo -e "${GREEN}Virtual environment created${NC}"
fi
echo ""

echo -e "${YELLOW}Step 4: Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}Virtual environment activated${NC}"
echo ""

echo -e "${YELLOW}Step 5: Upgrading pip...${NC}"
pip install --upgrade pip
echo ""

echo -e "${YELLOW}Step 6: Installing dependencies...${NC}"
echo -e "${YELLOW}This may take a few minutes...${NC}"
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Dependencies installed successfully${NC}"
else
    echo -e "${RED}Failed to install dependencies${NC}"
    exit 1
fi
echo ""

echo -e "${YELLOW}Step 7: Database initialization...${NC}"
read -p "Do you want to initialize the database? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python init_db_tables.py
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Database initialized successfully${NC}"
        echo ""
        echo -e "${GREEN}Default superadmin account created:${NC}"
        echo -e "${GREEN}Email: superadmin@test.com${NC}"
        echo -e "${GREEN}Password: test123${NC}"
        echo ""
        echo -e "${RED}IMPORTANT: Change the superadmin password after first login!${NC}"
    else
        echo -e "${RED}Database initialization failed${NC}"
        echo "Please check your DATABASE_URL in .env file"
        exit 1
    fi
fi
echo ""

echo -e "${YELLOW}Step 8: Testing backend server...${NC}"
echo -e "${YELLOW}Starting server for 5 seconds to test...${NC}"
timeout 5 uvicorn server:app --host 0.0.0.0 --port 9599 || true
echo ""

echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}Backend setup completed!${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""
echo "To start the backend server:"
echo -e "${GREEN}cd $BACKEND_DIR${NC}"
echo -e "${GREEN}source venv/bin/activate${NC}"
echo -e "${GREEN}uvicorn server:app --host 0.0.0.0 --port 9599 --workers 4${NC}"
echo ""
echo "Or use systemd service (recommended for production):"
echo "See PRODUCTION_DEPLOYMENT_GUIDE.md for details"
echo ""
