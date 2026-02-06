#!/bin/bash

# MJ SEO - Production Build Script for Frontend
# This script builds the React frontend for production deployment

set -e  # Exit on any error

echo "====================================="
echo "MJ SEO - Frontend Production Build"
echo "====================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

cd "$FRONTEND_DIR"

echo -e "${YELLOW}Step 1: Checking Node.js and Yarn...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}Error: Node.js is not installed${NC}"
    exit 1
fi

if ! command -v yarn &> /dev/null; then
    echo -e "${YELLOW}Yarn not found. Installing yarn...${NC}"
    npm install -g yarn
fi

echo -e "${GREEN}Node version: $(node --version)${NC}"
echo -e "${GREEN}Yarn version: $(yarn --version)${NC}"
echo ""

echo -e "${YELLOW}Step 2: Setting up production environment...${NC}"
if [ -f ".env.production" ]; then
    cp .env.production .env
    echo -e "${GREEN}Production environment file copied${NC}"
else
    echo -e "${RED}Warning: .env.production not found. Using existing .env${NC}"
fi
echo ""

echo -e "${YELLOW}Step 3: Installing dependencies...${NC}"
yarn install --frozen-lockfile
echo -e "${GREEN}Dependencies installed${NC}"
echo ""

echo -e "${YELLOW}Step 4: Building production bundle...${NC}"
echo -e "${YELLOW}This may take a few minutes...${NC}"
yarn build

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}=====================================${NC}"
    echo -e "${GREEN}Build completed successfully!${NC}"
    echo -e "${GREEN}=====================================${NC}"
    echo ""
    echo -e "${GREEN}Build output directory: $FRONTEND_DIR/build${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Upload the contents of 'build' folder to your web server"
    echo "2. Configure nginx to serve the static files"
    echo "3. Ensure backend API is running and accessible"
    echo ""
    echo "For detailed deployment instructions, see:"
    echo "PRODUCTION_DEPLOYMENT_GUIDE.md"
    echo ""
else
    echo ""
    echo -e "${RED}=====================================${NC}"
    echo -e "${RED}Build failed!${NC}"
    echo -e "${RED}=====================================${NC}"
    echo ""
    echo "Please check the error messages above and fix any issues."
    exit 1
fi
