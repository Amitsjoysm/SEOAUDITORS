#!/bin/bash

# Step 2: Backend Setup
set -e

echo "========================================="
echo "MJ SEO - Step 2: Backend Setup"
echo "========================================="
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

BACKEND_DIR="/www/wwwroot/MarketAutoMailer.mj.publicvm.com/backend"

if [ ! -d "$BACKEND_DIR" ]; then
    echo -e "${RED}Backend directory not found: $BACKEND_DIR${NC}"
    echo "Please ensure you've uploaded the backend folder first."
    exit 1
fi

cd "$BACKEND_DIR"

echo -e "${YELLOW}Step 1: Creating .env file...${NC}"

if [ -f "../.env.production" ]; then
    cp ../.env.production .env
    echo -e "${GREEN}✅ Copied .env.production to .env${NC}"
else
    echo -e "${RED}❌ .env.production not found${NC}"
    echo "Please ensure .env.production is in the parent directory"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 2: Edit .env file...${NC}"
echo "You need to update the following in .env:"
echo "  1. DATABASE_URL (with your database credentials)"
echo "  2. SECRET_KEY (generate a secure key)"
echo ""
read -p "Press Enter to open .env in nano editor..."
nano .env

echo ""
echo -e "${YELLOW}Step 3: Setting up Python virtual environment...${NC}"

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists${NC}"
fi

source venv/bin/activate

echo ""
echo -e "${YELLOW}Step 4: Installing dependencies...${NC}"
echo "This may take a few minutes..."

pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dependencies installed successfully${NC}"
else
    echo -e "${RED}❌ Failed to install dependencies${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 5: Initializing database...${NC}"
python init_db_tables.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Database initialized successfully${NC}"
    echo ""
    echo -e "${GREEN}Default superadmin account:${NC}"
    echo -e "${GREEN}  Email: superadmin@test.com${NC}"
    echo -e "${GREEN}  Password: test123${NC}"
    echo -e "${RED}  ⚠️  CHANGE PASSWORD AFTER FIRST LOGIN!${NC}"
else
    echo -e "${RED}❌ Database initialization failed${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 6: Testing backend...${NC}"
uvicorn server:app --host 0.0.0.0 --port 9599 &
SERVER_PID=$!
sleep 5

HEALTH=$(curl -s http://localhost:9599/api/health)

if echo "$HEALTH" | grep -q "healthy"; then
    echo -e "${GREEN}✅ Backend server is working!${NC}"
else
    echo -e "${RED}❌ Backend server test failed${NC}"
fi

kill $SERVER_PID 2>/dev/null
wait $SERVER_PID 2>/dev/null

echo ""
echo -e "${GREEN}=========================================="
echo "Backend Setup Complete!${NC}"
echo -e "${GREEN}==========================================${NC}"
echo ""
echo "Next step: Run ./3-build-frontend.sh on your local machine"
echo "Then run ./4-start-services.sh on the server"
