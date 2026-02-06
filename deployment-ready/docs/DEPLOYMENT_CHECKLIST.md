# 🚀 MJ SEO - Production Deployment Checklist

## 📁 Files Created for You

```
✅ backend/.env.production       - Production environment config
✅ backend/.env.template        - Environment variables template
✅ frontend/.env.production     - Frontend production config
✅ build-production.sh          - Frontend build script (Linux/Mac)
✅ build-production.bat         - Frontend build script (Windows)
✅ setup-backend-production.sh  - Backend setup script
✅ server-quick-setup.sh        - Quick server setup script
✅ nginx-production.conf        - Fixed nginx configuration
✅ PRODUCTION_DEPLOYMENT_GUIDE.md - Complete deployment guide
✅ BUILD_README.md              - Quick build instructions
✅ DEPLOYMENT_SUMMARY.md        - Issue analysis & solutions
✅ DEPLOYMENT_CHECKLIST.md      - This file!
```

---

## 🐞 Current Issues

### Issue #1: CORS Error ❌
```
Access to XMLHttpRequest at 'https://...' from origin 'http://...'
has been blocked by CORS policy
```

**Why:** 
- Nginx adding CORS headers that conflict with FastAPI
- Backend CORS_ORIGINS doesn't include HTTP origin
- Users accessing via HTTP but CORS expects HTTPS

**Fix:**
- ☑️ Remove CORS headers from nginx config
- ☑️ Update backend CORS_ORIGINS to include both HTTP and HTTPS
- ☑️ Let FastAPI handle CORS completely

---

### Issue #2: Database Connection Error ❌
```
sqlalchemy.exc.ArgumentError: Could not parse SQLAlchemy URL
```

**Why:**
- DATABASE_URL in backend .env is wrong format or missing
- Currently set to SQLite, but production needs PostgreSQL

**Fix:**
- ☑️ Create PostgreSQL database
- ☑️ Update DATABASE_URL with correct format
- ☑️ Initialize database tables

---

### Issue #3: Backend Crashes on Startup ❌
```
Backend fails to start, internal server error
```

**Why:**
- Database connection fails (issue #2)
- Missing environment variables
- Import errors cascade from database.py failure

**Fix:**
- ☑️ Fix database connection first
- ☑️ Verify all environment variables
- ☑️ Restart backend properly

---

## 🛠️ Quick Fix Guide

### Option 1: Automated Setup (Recommended)

**Upload to your server:**
- Upload entire `/app/backend/` folder
- Upload `server-quick-setup.sh` script

**Run on server:**
```bash
cd /www/wwwroot/MarketAutoMailer.mj.publicvm.com/deployment-package/
chmod +x server-quick-setup.sh
./server-quick-setup.sh
```

This script will:
- ✅ Check PostgreSQL
- ✅ Create database and user
- ✅ Set up virtual environment
- ✅ Install dependencies
- ✅ Create .env file with correct settings
- ✅ Initialize database
- ✅ Test backend

---

### Option 2: Manual Setup

#### Step 1: Database Setup

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE mjseo_db;
CREATE USER mjseo_user WITH PASSWORD 'YourSecurePassword';
GRANT ALL PRIVILEGES ON DATABASE mjseo_db TO mjseo_user;
\q
```

**✅ Checkpoint:** Test connection
```bash
psql -h localhost -U mjseo_user -d mjseo_db -W
```

---

#### Step 2: Backend Configuration

```bash
cd /www/wwwroot/MarketAutoMailer.mj.publicvm.com/deployment-package/backend/

# Copy template
cp .env.template .env

# Edit .env
nano .env
```

**Update these critical values:**
```bash
# MUST UPDATE:
DATABASE_URL="postgresql+asyncpg://mjseo_user:YourPassword@localhost:5432/mjseo_db"
CORS_ORIGINS="http://marketautomailer.mj.publicvm.com,https://marketautomailer.mj.publicvm.com"
SECRET_KEY="$(openssl rand -hex 32)"

# Verify these exist:
GROQ_API_KEY="..."
EXA_API_KEY="..."
STRIPE_SECRET_KEY="..."
```

**✅ Checkpoint:** Verify .env format
```bash
cat .env | grep DATABASE_URL
# Should show: DATABASE_URL="postgresql+asyncpg://..."
```

---

#### Step 3: Python Environment

```bash
cd /www/wwwroot/MarketAutoMailer.mj.publicvm.com/deployment-package/backend/

# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

**✅ Checkpoint:** Verify installations
```bash
pip list | grep -E "fastapi|sqlalchemy|uvicorn"
```

---

#### Step 4: Initialize Database

```bash
cd /www/wwwroot/MarketAutoMailer.mj.publicvm.com/deployment-package/backend/
source venv/bin/activate

python init_db_tables.py
```

**Expected output:**
```
✅ Created tables
✅ Created default plans
✅ Created superadmin user
✅ Created default themes
```

**✅ Checkpoint:** Test database
```bash
psql -h localhost -U mjseo_user -d mjseo_db -c "SELECT COUNT(*) FROM users;"
# Should return at least 1 (superadmin)
```

---

#### Step 5: Start Backend

```bash
cd /www/wwwroot/MarketAutoMailer.mj.publicvm.com/deployment-package/backend/
source venv/bin/activate

# Kill any existing process
pkill -f "uvicorn server:app"

# Start backend
nohup uvicorn server:app --host 0.0.0.0 --port 9599 --workers 4 > backend.log 2>&1 &

# Verify running
ps aux | grep uvicorn
```

**✅ Checkpoint:** Test backend
```bash
curl http://localhost:9599/api/health
# Expected: {"status":"healthy",...}

curl http://localhost:9599/api/plans
# Expected: [{"name":"Free",...},{"name":"Basic",...},...]
```

---

#### Step 6: Update Nginx

```bash
# Backup current config
cp /www/server/panel/vhost/nginx/marketautomailer.mj.publicvm.com.conf /root/nginx-backup.conf

# Copy new config
cp nginx-production.conf /www/server/panel/vhost/nginx/marketautomailer.mj.publicvm.com.conf

# Test nginx
sudo nginx -t

# If test passes, reload
sudo systemctl reload nginx
```

**✅ Checkpoint:** Test nginx
```bash
curl -I https://marketautomailer.mj.publicvm.com/api/health
# Should return: HTTP/2 200
```

---

#### Step 7: Build & Deploy Frontend

**On your local machine:**

```bash
cd /app/frontend

# Copy production env
cp .env.production .env

# Install dependencies
yarn install

# Build
yarn build

# This creates 'build' folder
```

**Upload to server:**
```bash
# Upload contents of 'build' folder to:
/www/wwwroot/MarketAutoMailer.mj.publicvm.com/
```

**✅ Checkpoint:** Verify frontend files
```bash
ls -la /www/wwwroot/MarketAutoMailer.mj.publicvm.com/
# Should see: index.html, static/, manifest.json, etc.
```

---

## 🧪 Testing Checklist

### Backend Tests

```bash
# Test 1: Health check
curl http://localhost:9599/api/health
✅ Expected: {"status":"healthy"}

# Test 2: Plans list
curl http://localhost:9599/api/plans
✅ Expected: Array of 4 plans

# Test 3: CORS test (from browser console)
fetch('https://marketautomailer.mj.publicvm.com/api/health').then(r => r.json()).then(console.log)
✅ Expected: No CORS error, returns health data
```

### Frontend Tests

```
1. Open https://marketautomailer.mj.publicvm.com
   ✅ Landing page loads (not blank)
   ✅ No console errors (F12)

2. Click "Register" or "Login"
   ✅ Forms load correctly
   ✅ No 404 errors

3. Try to register new user
   ✅ No CORS errors
   ✅ Registration succeeds or shows validation errors

4. Check Network tab (F12 > Network)
   ✅ API calls go to https://marketautomailer.mj.publicvm.com/api/...
   ✅ Responses have status 200 or appropriate error codes
```

### Integration Tests

```bash
# Test registration
curl -X POST https://marketautomailer.mj.publicvm.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","full_name":"Test User"}'

✅ Expected: Returns JWT token or validation error (not CORS error)

# Test login
curl -X POST https://marketautomailer.mj.publicvm.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"superadmin@test.com","password":"test123"}'

✅ Expected: Returns JWT token
```

---

## 🔍 Troubleshooting

### Problem: Backend won't start

**Check logs:**
```bash
tail -f /www/wwwroot/MarketAutoMailer.mj.publicvm.com/deployment-package/backend/backend.log
```

**Common causes:**
1. Wrong DATABASE_URL format
   - ✅ Must be: `postgresql+asyncpg://user:pass@host:port/db`
2. PostgreSQL not running
   - ✅ Check: `sudo systemctl status postgresql`
3. Port 9599 already in use
   - ✅ Check: `lsof -i :9599`
   - ✅ Kill: `pkill -f "uvicorn server:app"`

---

### Problem: CORS errors persist

**Check nginx config:**
```bash
grep -n "Access-Control" /www/server/panel/vhost/nginx/marketautomailer.mj.publicvm.com.conf
```
- ✅ Should return NOTHING (no CORS headers in nginx)

**Check backend CORS:**
```bash
cd /www/wwwroot/MarketAutoMailer.mj.publicvm.com/deployment-package/backend/
cat .env | grep CORS_ORIGINS
```
- ✅ Must include BOTH http and https origins

**Restart services:**
```bash
pkill -f "uvicorn server:app"
cd /www/wwwroot/MarketAutoMailer.mj.publicvm.com/deployment-package/backend/
source venv/bin/activate
nohup uvicorn server:app --host 0.0.0.0 --port 9599 --workers 4 > backend.log 2>&1 &

sudo systemctl reload nginx
```

---

### Problem: 502 Bad Gateway

**Check if backend is running:**
```bash
ps aux | grep uvicorn
curl http://localhost:9599/api/health
```

**Check nginx can reach backend:**
```bash
sudo tail -f /www/wwwlogs/marketautomailer.mj.publicvm.com.error.log
```

---

### Problem: Frontend shows blank page

**Check browser console (F12):**
- Look for errors
- Check Network tab for failed requests

**Check build:**
```bash
ls -la /www/wwwroot/MarketAutoMailer.mj.publicvm.com/
```
- ✅ Must have: index.html, static/ folder

**Verify API URL in build:**
- Open: https://marketautomailer.mj.publicvm.com/static/js/main.*.js
- Search for: "marketautomailer.mj.publicvm.com/api"
- ✅ Should find the correct API URL

---

## 📊 Status Dashboard

### Check Service Status

```bash
# Backend status
ps aux | grep uvicorn
curl http://localhost:9599/api/health

# Nginx status
sudo systemctl status nginx

# PostgreSQL status
sudo systemctl status postgresql

# Check ports
sudo lsof -i :9599  # Backend
sudo lsof -i :443   # HTTPS
sudo lsof -i :80    # HTTP
```

### View Logs

```bash
# Backend logs
tail -f /www/wwwroot/MarketAutoMailer.mj.publicvm.com/deployment-package/backend/backend.log

# Nginx access log
tail -f /www/wwwlogs/marketautomailer.mj.publicvm.com.log

# Nginx error log
tail -f /www/wwwlogs/marketautomailer.mj.publicvm.com.error.log

# PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-*.log
```

---

## ✅ Production Ready Checklist

### Security
- [ ] Changed SECRET_KEY in .env
- [ ] Using strong PostgreSQL password
- [ ] Changed superadmin password from default
- [ ] Stripe webhook configured
- [ ] HSTS enabled (if HTTPS working)
- [ ] Firewall configured (ports 80, 443, 22 only)
- [ ] Database backups configured

### Performance
- [ ] Backend running with 4 workers
- [ ] Nginx caching enabled
- [ ] Frontend built with production optimizations
- [ ] Database indexes created (automatic)

### Monitoring
- [ ] Log rotation configured
- [ ] Error monitoring set up
- [ ] Uptime monitoring configured
- [ ] Database size monitoring

### Documentation
- [ ] API keys documented
- [ ] Backup procedures documented
- [ ] Recovery procedures tested

---

## 📞 Need Help?

### Quick Reference Docs

1. **PRODUCTION_DEPLOYMENT_GUIDE.md**
   - Complete step-by-step deployment guide
   - Detailed troubleshooting section
   - Common issues and solutions

2. **DEPLOYMENT_SUMMARY.md**
   - Analysis of current issues
   - Quick fix guide
   - What's been fixed

3. **BUILD_README.md**
   - Quick build instructions
   - Prerequisites
   - Troubleshooting build errors

### Test Commands

```bash
# Quick health check
curl https://marketautomailer.mj.publicvm.com/api/health

# Test database
psql -h localhost -U mjseo_user -d mjseo_db -c "SELECT COUNT(*) FROM users;"

# Test backend directly
curl http://localhost:9599/api/health

# Check if services running
ps aux | grep -E "uvicorn|nginx|postgres"
```

---

**Last Updated:** January 2025  
**Version:** 2.0.0  
**Status:** Ready for Deployment
