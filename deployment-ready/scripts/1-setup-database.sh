#!/bin/bash

# Step 1: Database Setup
set -e

echo "========================================="
echo "MJ SEO - Step 1: Database Setup"
echo "========================================="
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}This script will:${NC}"
echo "1. Check PostgreSQL installation"
echo "2. Create database and user"
echo "3. Grant permissions"
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

echo ""
echo -e "${YELLOW}Creating database...${NC}"

sudo -u postgres psql << EOF
CREATE DATABASE $DB_NAME;
CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Database created successfully${NC}"
else
    echo -e "${YELLOW}⚠️  Database may already exist (this is OK)${NC}"
fi

echo ""
echo -e "${YELLOW}Testing connection...${NC}"
PGPASSWORD="$DB_PASS" psql -h localhost -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Database connection successful${NC}"
else
    echo -e "${RED}❌ Database connection failed${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}=========================================="
echo -e "Database Setup Complete!${NC}"
echo -e "${GREEN}==========================================${NC}"
echo ""
echo "Database Name: $DB_NAME"
echo "Database User: $DB_USER"
echo "Database Password: [hidden]"
echo ""
echo "Connection string:"
echo -e "${GREEN}postgresql+asyncpg://$DB_USER:$DB_PASS@localhost:5432/$DB_NAME${NC}"
echo ""
echo "Save this information! You'll need it for the .env file."
echo ""
echo "Next step: Run ./2-setup-backend.sh"
