# MJ SEO Production Deployment Guide for aaPanel

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Database Setup](#database-setup)
3. [Backend Deployment](#backend-deployment)
4. [Frontend Build & Deployment](#frontend-build--deployment)
5. [Nginx Configuration](#nginx-configuration)
6. [Common Issues & Solutions](#common-issues--solutions)

---

## Prerequisites

### Required Software
- aaPanel installed and configured
- PostgreSQL 12+ installed
- Python 3.10+ installed
- Node.js 18+ installed
- Nginx (managed by aaPanel)

### Domain Configuration
- Domain: `marketautomailer.mj.publicvm.com`
- SSL certificate installed (Let's Encrypt recommended)

---

## Database Setup

### Step 1: Create PostgreSQL Database

```bash
# Login as postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE mjseo_db;
CREATE USER mjseo_user WITH PASSWORD 'your_secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE mjseo_db TO mjseo_user;

# Exit psql
\q
```

### Step 2: Test Database Connection

```bash
# Test connection
psql -h localhost -U mjseo_user -d mjseo_db -W
```

---

## Backend Deployment

### Step 1: Upload Backend Files

Upload the entire `backend` folder to your server:
```bash
/www/wwwroot/MarketAutoMailer.mj.publicvm.com/deployment-package/backend/
```

### Step 2: Configure Production Environment

```bash
cd /www/wwwroot/MarketAutoMailer.mj.publicvm.com/deployment-package/backend/

# Copy production environment file
cp .env.production .env

# Edit .env with your actual credentials
nano .env
```

**IMPORTANT: Update these values in .env:**

```bash
# Replace with your actual PostgreSQL credentials
DATABASE_URL="postgresql+asyncpg://mjseo_user:your_secure_password_here@localhost:5432/mjseo_db"

# Verify domain is correct
CORS_ORIGINS="http://marketautomailer.mj.publicvm.com,https://marketautomailer.mj.publicvm.com"
FRONTEND_URL="https://marketautomailer.mj.publicvm.com"
```

### Step 3: Set Up Python Virtual Environment

```bash
cd /www/wwwroot/MarketAutoMailer.mj.publicvm.com/deployment-package/backend/

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Initialize Database

```bash
# Make sure you're in the backend directory with venv activated
source venv/bin/activate

# Run database initialization
python init_db_tables.py
```

This will create:
- All database tables
- Default plans (Free, Basic, Pro, Enterprise)
- Superadmin account: `superadmin@test.com` / `test123`
- Default themes

### Step 5: Test Backend Locally

```bash
# Start backend server (test)
python -m uvicorn server:app --host 0.0.0.0 --port 9599

# In another terminal, test the API
curl http://localhost:9599/api/health

# Should return: {"status":"healthy","service":"MJ SEO Backend",...}
```

### Step 6: Set Up Systemd Service (Recommended)

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/mjseo-backend.service
```

Add the following content:

```ini
[Unit]
Description=MJ SEO FastAPI Backend
After=network.target postgresql.service

[Service]
Type=simple
User=www
Group=www
WorkingDirectory=/www/wwwroot/MarketAutoMailer.mj.publicvm.com/deployment-package/backend
Environment="PATH=/www/wwwroot/MarketAutoMailer.mj.publicvm.com/deployment-package/backend/venv/bin"
ExecStart=/www/wwwroot/MarketAutoMailer.mj.publicvm.com/deployment-package/backend/venv/bin/uvicorn server:app --host 0.0.0.0 --port 9599 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable mjseo-backend
sudo systemctl start mjseo-backend
sudo systemctl status mjseo-backend
```

**OR** if you prefer to keep using uvicorn directly:

```bash
# Run in background with nohup
cd /www/wwwroot/MarketAutoMailer.mj.publicvm.com/deployment-package/backend
source venv/bin/activate
nohup uvicorn server:app --host 0.0.0.0 --port 9599 --workers 4 > backend.log 2>&1 &

# Check if running
ps aux | grep uvicorn
```

---

## Frontend Build & Deployment

### Step 1: Build Frontend Locally or on Server

**Option A: Build on Your Local Machine (Recommended)**

```bash
cd /app/frontend

# Install dependencies
yarn install

# Build for production
yarn build

# This creates a 'build' folder with optimized production files
```

Then upload the `build` folder contents to:
```
/www/wwwroot/MarketAutoMailer.mj.publicvm.com/
```

**Option B: Build on Server**

```bash
cd /www/wwwroot/MarketAutoMailer.mj.publicvm.com/frontend-source/

# Copy production env
cp .env.production .env

# Install dependencies
yarn install

# Build
yarn build

# Copy build files to web root
cp -r build/* /www/wwwroot/MarketAutoMailer.mj.publicvm.com/
```

### Step 2: Verify Frontend Files

Your web root should have:
```
/www/wwwroot/MarketAutoMailer.mj.publicvm.com/
├── index.html
├── static/
│   ├── css/
│   ├── js/
│   └── media/
├── manifest.json
└── favicon.ico
```

---

## Nginx Configuration

### Updated Nginx Configuration (CORS Fixed)

Replace your current nginx config with this:

```nginx
server {
    listen 80;
    server_name marketautomailer.mj.publicvm.com;

    # Force HTTP → HTTPS redirect
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name marketautomailer.mj.publicvm.com;

    # ---------- SSL CERTIFICATE ----------
    ssl_certificate /www/server/panel/vhost/cert/marketautomailer.mj.publicvm.com/fullchain.pem;
    ssl_certificate_key /www/server/panel/vhost/cert/marketautomailer.mj.publicvm.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # ---------- REACT FRONTEND ----------
    root /www/wwwroot/MarketAutoMailer.mj.publicvm.com;
    index index.html;

    # ---------- FASTAPI BACKEND - NO CORS HEADERS (Backend handles it) ----------
    location /api/ {
        # Proxy to backend WITHOUT adding CORS headers
        proxy_pass http://localhost:9599;
        proxy_http_version 1.1;

        # Standard proxy headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;

        # WebSocket support
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Disable buffering for real-time responses
        proxy_buffering off;
    }

    # ---------- FRONTEND ROUTING (React Router) ----------
    location / {
        try_files $uri $uri/ /index.html;
    }

    # ---------- SECURITY ----------
    # Block access to sensitive files
    location ~ /\.(git|env|htaccess|user\.ini|svn|project|bak|sql)$ {
        return 404;
    }

    # Allow Let's Encrypt verification
    location ~ /\.well-known {
        allow all;
    }

    # ---------- STATIC FILE CACHING ----------
    location /static/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Image caching
    location ~* \.(jpg|jpeg|png|gif|webp|ico|svg|avif)$ {
        expires 30d;
        add_header Cache-Control "public";
    }

    # Font and CSS/JS caching
    location ~* \.(js|css|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # ---------- LOGS ----------
    access_log /www/wwwlogs/marketautomailer.mj.publicvm.com.log;
    error_log /www/wwwlogs/marketautomailer.mj.publicvm.com.error.log;
}
```

**KEY CHANGES:**
1. ✅ Removed all CORS headers from nginx (FastAPI handles CORS)
2. ✅ Simplified proxy configuration
3. ✅ Added React Router support with `try_files`

### Apply Nginx Configuration

```bash
# Test nginx configuration
sudo nginx -t

# If test passes, reload nginx
sudo systemctl reload nginx
```

---

## Common Issues & Solutions

### Issue 1: CORS Error

**Error:**
```
Access to XMLHttpRequest at 'https://marketautomailer.mj.publicvm.com/api/auth/register' 
from origin 'http://marketautomailer.mj.publicvm.com' has been blocked by CORS policy
```

**Solution:**
1. Make sure nginx config does NOT add CORS headers (use config above)
2. Verify backend `.env` has correct CORS_ORIGINS:
   ```bash
   CORS_ORIGINS="http://marketautomailer.mj.publicvm.com,https://marketautomailer.mj.publicvm.com"
   ```
3. Restart backend:
   ```bash
   sudo systemctl restart mjseo-backend
   # OR
   pkill -f uvicorn
   cd /www/wwwroot/MarketAutoMailer.mj.publicvm.com/deployment-package/backend
   source venv/bin/activate
   nohup uvicorn server:app --host 0.0.0.0 --port 9599 --workers 4 > backend.log 2>&1 &
   ```

### Issue 2: Database Connection Error

**Error:**
```
sqlalchemy.exc.ArgumentError: Could not parse SQLAlchemy URL from given URL string
```

**Solution:**
1. Check DATABASE_URL format in `/app/backend/.env`:
   ```bash
   DATABASE_URL="postgresql+asyncpg://username:password@localhost:5432/database_name"
   ```
2. Test PostgreSQL connection:
   ```bash
   psql -h localhost -U mjseo_user -d mjseo_db -W
   ```
3. Ensure PostgreSQL is running:
   ```bash
   sudo systemctl status postgresql
   ```

### Issue 3: Backend Not Starting

**Check logs:**
```bash
# If using systemd
sudo journalctl -u mjseo-backend -f

# If using nohup
tail -f /www/wwwroot/MarketAutoMailer.mj.publicvm.com/deployment-package/backend/backend.log
```

**Common causes:**
1. Missing dependencies: `pip install -r requirements.txt`
2. Wrong DATABASE_URL format
3. Port 9599 already in use: `lsof -i :9599`

### Issue 4: Frontend Shows Blank Page

**Solutions:**
1. Check browser console for errors (F12)
2. Verify build files exist:
   ```bash
   ls -la /www/wwwroot/MarketAutoMailer.mj.publicvm.com/
   ```
3. Check nginx error log:
   ```bash
   tail -f /www/wwwlogs/marketautomailer.mj.publicvm.com.error.log
   ```
4. Verify REACT_APP_BACKEND_URL in build (check browser network tab)

### Issue 5: 502 Bad Gateway

**Causes:**
- Backend not running
- Backend crashed
- Wrong port in nginx config

**Check:**
```bash
# Is backend running?
ps aux | grep uvicorn

# Can nginx reach backend?
curl http://localhost:9599/api/health

# Check nginx error log
tail -f /www/wwwlogs/marketautomailer.mj.publicvm.com.error.log
```

---

## Production Checklist

### Security
- [ ] Change SECRET_KEY in backend .env
- [ ] Use strong PostgreSQL password
- [ ] Set up Stripe webhook URL
- [ ] Enable HSTS (ENABLE_HSTS="true")
- [ ] Configure firewall (allow only 80, 443, 22)
- [ ] Regular backups of PostgreSQL database

### Performance
- [ ] Backend running with multiple workers (--workers 4)
- [ ] Nginx caching configured
- [ ] Frontend built with `yarn build`
- [ ] Database indexes optimized

### Monitoring
- [ ] Set up log rotation
- [ ] Monitor backend logs
- [ ] Monitor nginx logs
- [ ] Set up uptime monitoring
- [ ] Monitor database size

---

## Quick Start Commands

### Start Backend
```bash
cd /www/wwwroot/MarketAutoMailer.mj.publicvm.com/deployment-package/backend
source venv/bin/activate
uvicorn server:app --host 0.0.0.0 --port 9599 --workers 4
```

### Restart Services
```bash
# Backend
sudo systemctl restart mjseo-backend

# Nginx
sudo systemctl reload nginx

# PostgreSQL
sudo systemctl restart postgresql
```

### Check Status
```bash
# Backend
sudo systemctl status mjseo-backend

# Nginx
sudo systemctl status nginx

# PostgreSQL
sudo systemctl status postgresql
```

### View Logs
```bash
# Backend logs
sudo journalctl -u mjseo-backend -f

# Nginx access log
tail -f /www/wwwlogs/marketautomailer.mj.publicvm.com.log

# Nginx error log
tail -f /www/wwwlogs/marketautomailer.mj.publicvm.com.error.log
```

---

## Support

For issues or questions:
1. Check logs first
2. Review [Common Issues](#common-issues--solutions) section
3. Verify all environment variables are correct
4. Test backend API directly: `curl http://localhost:9599/api/health`

---

**Last Updated:** January 2025
**Version:** 2.0.0
