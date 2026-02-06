#!/bin/bash

# Step 4: Start Services
set -e

echo "========================================="
echo "MJ SEO - Step 4: Start Services"
echo "========================================="
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

BACKEND_DIR="/www/wwwroot/MarketAutoMailer.mj.publicvm.com/backend"
NGINX_CONF="/www/server/panel/vhost/nginx/marketautomailer.mj.publicvm.com.conf"

echo -e "${YELLOW}Step 1: Updating nginx configuration...${NC}"

if [ -f "../nginx/marketautomailer.conf" ]; then
    sudo cp "$NGINX_CONF" "$NGINX_CONF.backup" 2>/dev/null
    sudo cp "../nginx/marketautomailer.conf" "$NGINX_CONF"
    echo -e "${GREEN}✅ Nginx configuration updated${NC}"
    echo "   (Backup saved to $NGINX_CONF.backup)"
else
    echo -e "${YELLOW}⚠️  Nginx config not found, skipping...${NC}"
fi

echo ""
echo -e "${YELLOW}Step 2: Testing nginx configuration...${NC}"
sudo nginx -t

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Nginx configuration is valid${NC}"
    echo -e "${YELLOW}Reloading nginx...${NC}"
    sudo systemctl reload nginx
    echo -e "${GREEN}✅ Nginx reloaded${NC}"
else
    echo -e "${RED}❌ Nginx configuration test failed${NC}"
    echo "Restoring backup..."
    sudo cp "$NGINX_CONF.backup" "$NGINX_CONF"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 3: Starting backend server...${NC}"

cd "$BACKEND_DIR"

# Stop any existing uvicorn processes
pkill -f "uvicorn server:app" 2>/dev/null || true
sleep 2

# Start backend
source venv/bin/activate
nohup uvicorn server:app --host 0.0.0.0 --port 9599 --workers 4 > backend.log 2>&1 &

sleep 5

# Check if backend is running
if ps aux | grep -v grep | grep "uvicorn server:app" > /dev/null; then
    echo -e "${GREEN}✅ Backend server started${NC}"
else
    echo -e "${RED}❌ Backend server failed to start${NC}"
    echo "Check logs: tail -f $BACKEND_DIR/backend.log"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 4: Testing backend...${NC}"
sleep 2

HEALTH=$(curl -s http://localhost:9599/api/health)

if echo "$HEALTH" | grep -q "healthy"; then
    echo -e "${GREEN}✅ Backend is healthy!${NC}"
    echo "Response: $HEALTH"
else
    echo -e "${RED}❌ Backend health check failed${NC}"
    echo "Response: $HEALTH"
fi

echo ""
echo -e "${GREEN}=========================================="
echo "All Services Started!${NC}"
echo -e "${GREEN}==========================================${NC}"
echo ""
echo "Service Status:"
echo -e "${GREEN}✅ Backend: Running on port 9599${NC}"
echo -e "${GREEN}✅ Nginx: Running${NC}"
echo ""
echo "Access your application:"
echo -e "${GREEN}https://marketautomailer.mj.publicvm.com${NC}"
echo ""
echo "Superadmin Login:"
echo "  Email: superadmin@test.com"
echo "  Password: test123"
echo -e "${RED}  ⚠️  CHANGE PASSWORD IMMEDIATELY!${NC}"
echo ""
echo "To check logs:"
echo "  Backend: tail -f $BACKEND_DIR/backend.log"
echo "  Nginx: tail -f /www/wwwlogs/marketautomailer.mj.publicvm.com.error.log"
echo ""
echo "To restart backend:"
echo "  pkill -f 'uvicorn server:app'"
echo "  cd $BACKEND_DIR && source venv/bin/activate"
echo "  nohup uvicorn server:app --host 0.0.0.0 --port 9599 --workers 4 > backend.log 2>&1 &"
echo ""
