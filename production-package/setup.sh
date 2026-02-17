#!/bin/bash

# MJ SEO Quick Setup Script for aaPanel
# Run this script after uploading files to your aaPanel server

echo "🚀 MJ SEO Production Setup"
echo "================================"
echo ""

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root or with sudo"
    exit 1
fi

# Get domain from user
read -p "Enter your domain name (e.g., yourdomain.com): " DOMAIN
if [ -z "$DOMAIN" ]; then
    echo "❌ Domain name is required"
    exit 1
fi

WEBROOT="/www/wwwroot/$DOMAIN"
BACKEND_DIR="$WEBROOT/backend"

echo ""
echo "📁 Installation Directory: $WEBROOT"
echo "🔧 Backend Directory: $BACKEND_DIR"
echo ""

# Check if directories exist
if [ ! -d "$WEBROOT" ]; then
    echo "❌ Webroot directory does not exist: $WEBROOT"
    echo "Please create the website in aaPanel first"
    exit 1
fi

if [ ! -d "$BACKEND_DIR" ]; then
    echo "❌ Backend directory does not exist: $BACKEND_DIR"
    echo "Please upload the backend files first"
    exit 1
fi

# Setup Python virtual environment
echo "🐍 Setting up Python virtual environment..."
cd "$BACKEND_DIR"
python3 -m venv venv

# Activate venv and install dependencies
echo "📦 Installing Python dependencies..."
source venv/bin/activate

pip install --upgrade pip > /dev/null 2>&1

echo "   Installing core packages..."
pip install fastapi uvicorn sqlalchemy aiosqlite asyncpg pyjwt bcrypt passlib python-dotenv pydantic requests beautifulsoup4 lxml groq openai reportlab python-docx stripe > /dev/null 2>&1

echo "   Installing additional packages..."
pip install pydantic-settings email-validator python-multipart cryptography python-jose aiohttp anthropic google-generativeai > /dev/null 2>&1

echo "✅ Dependencies installed"

# Setup .env file
echo ""
echo "⚙️  Configuring environment..."
if [ -f "$BACKEND_DIR/.env.production" ]; then
    cp "$BACKEND_DIR/.env.production" "$BACKEND_DIR/.env"
    
    # Update domain in .env
    sed -i "s/marketautomailer.mj.publicvm.com/$DOMAIN/g" "$BACKEND_DIR/.env"
    
    echo "✅ Environment configured"
else
    echo "⚠️  Warning: .env.production not found"
fi

# Initialize database
echo ""
echo "🗄️  Initializing database..."
cd "$BACKEND_DIR"
source venv/bin/activate
python init_db_tables.py
echo "✅ Database initialized"

# Create systemd service
echo ""
echo "🔧 Creating systemd service..."

cat > /etc/systemd/system/mjseo-backend.service << EOF
[Unit]
Description=MJ SEO Backend Service
After=network.target

[Service]
Type=simple
User=www
Group=www
WorkingDirectory=$BACKEND_DIR
Environment="PATH=$BACKEND_DIR/venv/bin"
ExecStart=$BACKEND_DIR/venv/bin/uvicorn server:app --host 127.0.0.1 --port 9599 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd, enable and start service
systemctl daemon-reload
systemctl enable mjseo-backend
systemctl start mjseo-backend

echo "✅ Service created and started"

# Check service status
sleep 2
if systemctl is-active --quiet mjseo-backend; then
    echo "✅ Backend service is running"
else
    echo "⚠️  Warning: Backend service may not be running properly"
    echo "Check logs with: sudo journalctl -u mjseo-backend -n 50"
fi

# Test backend
echo ""
echo "🧪 Testing backend..."
sleep 2
HEALTH_CHECK=$(curl -s http://localhost:9599/api/health 2>/dev/null)
if [ "$HEALTH_CHECK" = '{"status":"healthy"}' ]; then
    echo "✅ Backend health check passed"
else
    echo "⚠️  Warning: Backend health check failed"
    echo "Response: $HEALTH_CHECK"
fi

echo ""
echo "================================"
echo "✅ Setup Complete!"
echo "================================"
echo ""
echo "📋 Next Steps:"
echo "1. Configure Nginx in aaPanel:"
echo "   - Go to Website → $DOMAIN → Settings → Config"
echo "   - Replace config with content from nginx.conf"
echo "   - Replace 'yourdomain.com' with '$DOMAIN'"
echo ""
echo "2. Setup SSL Certificate:"
echo "   - Go to Website → $DOMAIN → SSL"
echo "   - Click 'Let's Encrypt' and apply"
echo ""
echo "3. Test your application:"
echo "   - Visit: https://$DOMAIN"
echo "   - Login with: superadmin@test.com / test123"
echo ""
echo "4. Change default passwords immediately!"
echo ""
echo "📊 Service Management:"
echo "   Start:   sudo systemctl start mjseo-backend"
echo "   Stop:    sudo systemctl stop mjseo-backend"
echo "   Restart: sudo systemctl restart mjseo-backend"
echo "   Status:  sudo systemctl status mjseo-backend"
echo "   Logs:    sudo journalctl -u mjseo-backend -f"
echo ""
echo "🔐 Default Credentials:"
echo "   Superadmin: superadmin@test.com / test123"
echo "   Test User: test@example.com / test123"
echo ""
echo "⚠️  IMPORTANT: Change these passwords in production!"
echo ""
