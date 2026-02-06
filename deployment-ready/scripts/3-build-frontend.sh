#!/bin/bash

# Step 3: Build Frontend (Run on LOCAL machine)
set -e

echo "========================================="
echo "MJ SEO - Step 3: Build Frontend"
echo "========================================="
echo ""
echo "⚠️  Run this script on your LOCAL machine, not on the server!"
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

FRONTEND_DIR="../frontend-source"

if [ ! -d "$FRONTEND_DIR" ]; then
    echo -e "${RED}Frontend directory not found: $FRONTEND_DIR${NC}"
    exit 1
fi

cd "$FRONTEND_DIR"

echo -e "${YELLOW}Step 1: Setting up production environment...${NC}"
if [ -f ".env.production" ]; then
    cp .env.production .env
    echo -e "${GREEN}✅ Production environment copied${NC}"
else
    echo -e "${RED}❌ .env.production not found${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 2: Installing dependencies...${NC}"
yarn install

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to install dependencies${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 3: Building production bundle...${NC}"
echo "This may take a few minutes..."
yarn build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Build completed successfully!${NC}"
else
    echo -e "${RED}❌ Build failed${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}=========================================="
echo "Frontend Build Complete!${NC}"
echo -e "${GREEN}==========================================${NC}"
echo ""
echo "Build output: $FRONTEND_DIR/build/"
echo ""
echo "Next steps:"
echo "1. Upload the contents of 'build' folder to your server:"
echo "   /www/wwwroot/MarketAutoMailer.mj.publicvm.com/"
echo ""
echo "2. Then run ./4-start-services.sh on the server"
