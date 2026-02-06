#!/bin/bash

# MJ SEO - Quick Server Setup Script
# Run this on your production server after uploading files

set -e

echo "====================================="
echo "MJ SEO - Server Quick Setup"
echo "====================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
BACKEND_DIR="/www/wwwroot/MarketAutoMailer.mj.publicvm.com/deployment-package/backend"
FRONTEND_DIR="/www/wwwroot/MarketAutoMailer.mj.publicvm.com"

echo -e "${YELLOW}This script will:${NC}"
echo "1. Check PostgreSQL installation"
echo "2. Create database and user"
echo "3. Set up backend virtual environment"
echo "4. Install Python dependencies"
echo "5. Initialize database tables"
echo "6. Test backend server"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi
echo ""

# Step 1: Check PostgreSQL
echo -e "${YELLOW}Step 1: Checking PostgreSQL...${NC}"
if ! command -v psql &> /dev/null; then
    echo -e "${RED}PostgreSQL is not installed!${NC}"
    echo "Please install PostgreSQL first:"
    echo "  apt-get install postgresql postgresql-contrib"
    exit 1
fi
echo -e "${GREEN}PostgreSQL found${NC}"
echo ""

# Step 2: Database setup
echo -e "${YELLOW}Step 2: Database setup${NC}"
echo "Enter PostgreSQL superuser password when prompted"
echo ""

read -p "Database name [mjseo_db]: " DB_NAME
DB_NAME=${DB_NAME:-mjseo_db}

read -p "Database user [mjseo_user]: " DB_USER
DB_USER=${DB_USER:-mjseo_user}

read -s -p "Database password: " DB_PASS
echo

if [ -z "$DB_PASS" ]; then
    echo -e "${RED}Password cannot be empty!${NC}"
    exit 1
fi

# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE $DB_NAME;
CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Database created successfully${NC}"
else
    echo -e "${YELLOW}Database may already exist (this is OK)${NC}"
fi
echo ""

# Step 3: Backend setup
echo -e "${YELLOW}Step 3: Setting up backend...${NC}"

if [ ! -d "$BACKEND_DIR" ]; then
    echo -e "${RED}Backend directory not found: $BACKEND_DIR${NC}"
    echo "Please ensure backend files are uploaded to the correct location"
    exit 1
fi

cd "$BACKEND_DIR"

# Create .env file
echo -e "${YELLOW}Creating .env file...${NC}"

cat > .env << EOF
# Database Configuration
DATABASE_URL="postgresql+asyncpg://$DB_USER:$DB_PASS@localhost:5432/$DB_NAME"

# CORS Configuration
CORS_ORIGINS="http://marketautomailer.mj.publicvm.com,https://marketautomailer.mj.publicvm.com"

# Security
SECRET_KEY="$(openssl rand -hex 32)"

# Frontend URL
FRONTEND_URL="https://marketautomailer.mj.publicvm.com"

# API Keys (update these with your actual keys)
GROQ_API_KEY="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"
EXA_API_KEY="28a8cf69-fb6d-45db-8c2a-7f832d29aec3"

# Stripe Configuration
STRIPE_SECRET_KEY="sk_test_51STFwADoGaR8tHFRfRhrM62DdDzoC8eAc2x5GJrReQlyi6Vgw4IULPn74ihpcryqjho0Gn5RUOfmEI9ycwT03ZL000RlTcoUkW"
STRIPE_PUBLISHABLE_KEY="pk_test_51STFwADoGaR8tHFRLsFDEAvjeaKa80Reh6XZ0wQUqkhxxZfq63NOPk549NpuNBdXaIMnZMEBYwkbHyirPtnjLsoV00IQm4fIiO"
STRIPE_WEBHOOK_SECRET="whsec_placeholder"

# DataForSEO Credentials
DATAFORSEO_USERNAME="evelyene@devbaytech.com"
DATAFORSEO_PASSWORD="6ecff7f6476fd099"

# Google OAuth Credentials
GOOGLE_CLIENT_ID="835555676390-o94n7a0ubcmhi4uvnrh1cjojprlgfs0a.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="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"
GOOGLE_PROJECT_ID="mjseo-479908"

# Production Security
ENABLE_HSTS="true"
ENABLE_CSP="false"
EOF

echo -e "${GREEN}.env file created${NC}"
echo ""

# Step 4: Virtual environment
echo -e "${YELLOW}Step 4: Setting up Python virtual environment...${NC}"

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}Virtual environment created${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists${NC}"
fi

source venv/bin/activate
echo ""

# Step 5: Install dependencies
echo -e "${YELLOW}Step 5: Installing Python dependencies...${NC}"
echo -e "${YELLOW}This may take a few minutes...${NC}"

pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Dependencies installed successfully${NC}"
else
    echo -e "${RED}Failed to install dependencies${NC}"
    exit 1
fi
echo ""

# Step 6: Initialize database
echo -e "${YELLOW}Step 6: Initializing database...${NC}"
python init_db_tables.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Database initialized successfully${NC}"
    echo ""
    echo -e "${GREEN}Default superadmin account:${NC}"
    echo -e "${GREEN}Email: superadmin@test.com${NC}"
    echo -e "${GREEN}Password: test123${NC}"
    echo ""
    echo -e "${RED}IMPORTANT: Change password after first login!${NC}"
else
    echo -e "${RED}Database initialization failed${NC}"
    exit 1
fi
echo ""

# Step 7: Test backend
echo -e "${YELLOW}Step 7: Testing backend server...${NC}"
echo -e "${YELLOW}Starting server for 10 seconds...${NC}"

# Start server in background
uvicorn server:app --host 0.0.0.0 --port 9599 &
SERVER_PID=$!

# Wait for server to start
sleep 5

# Test health endpoint
HEALTH=$(curl -s http://localhost:9599/api/health)

if echo "$HEALTH" | grep -q "healthy"; then
    echo -e "${GREEN}Backend server is working!${NC}"
    echo "Response: $HEALTH"
else
    echo -e "${RED}Backend server test failed${NC}"
    echo "Response: $HEALTH"
fi

# Stop test server
kill $SERVER_PID 2>/dev/null
wait $SERVER_PID 2>/dev/null

echo ""
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}Setup completed successfully!${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""
echo "To start the backend server:"
echo -e "${GREEN}cd $BACKEND_DIR${NC}"
echo -e "${GREEN}source venv/bin/activate${NC}"
echo -e "${GREEN}nohup uvicorn server:app --host 0.0.0.0 --port 9599 --workers 4 > backend.log 2>&1 &${NC}"
echo ""
echo "To check if backend is running:"
echo -e "${GREEN}ps aux | grep uvicorn${NC}"
echo -e "${GREEN}curl http://localhost:9599/api/health${NC}"
echo ""
echo "Next steps:"
echo "1. Build and upload frontend (see BUILD_README.md)"
echo "2. Update nginx configuration (see nginx-production.conf)"
echo "3. Reload nginx: sudo systemctl reload nginx"
echo ""
echo "For complete instructions, see: PRODUCTION_DEPLOYMENT_GUIDE.md"
echo ""
