# 🚀 MJ SEO - Ready-to-Upload Deployment Package

## 📦 What's This?

This is a **complete deployment package** ready to be uploaded to your aaPanel server at `marketautomailer.mj.publicvm.com`.

---

## 📁 Package Structure

```
deployment-ready/
├── backend/                  ← Upload to /www/wwwroot/MarketAutoMailer.mj.publicvm.com/backend/
├── frontend-source/          ← Build locally, then upload build output
├── nginx/                    ← Nginx configuration
├── scripts/                  ← Deployment scripts (run in order)
├── docs/                     ← Documentation
├── .env.production           ← Production environment file
└── README.md                 ← This file
```

---

## 🎯 Quick Deployment Guide

### Step 1: Upload to Server

Upload this entire `deployment-ready` folder to your server:

```bash
# Upload to:
/www/wwwroot/MarketAutoMailer.mj.publicvm.com/

# Final structure should be:
/www/wwwroot/MarketAutoMailer.mj.publicvm.com/
├── deployment-ready/
│   ├── backend/
│   ├── frontend-source/
│   ├── nginx/
│   ├── scripts/
│   └── .env.production
```

### Step 2: Run Deployment Scripts (In Order)

SSH into your server and run:

```bash
cd /www/wwwroot/MarketAutoMailer.mj.publicvm.com/deployment-ready/scripts

# Make scripts executable
chmod +x *.sh

# Run in order:
./1-setup-database.sh       # Creates PostgreSQL database
./2-setup-backend.sh        # Sets up Python backend
./3-build-frontend.sh       # Build frontend (run on LOCAL machine)
./4-start-services.sh       # Start all services
```

### Step 3: Access Your Application

Open: https://marketautomailer.mj.publicvm.com

Login with:
- Email: `superadmin@test.com`
- Password: `test123`

⚠️ **Change password immediately!**

---

## 📝 Detailed Steps

### Script 1: Setup Database

```bash
./1-setup-database.sh
```

This will:
- Check PostgreSQL installation
- Create database `mjseo_db`
- Create user `mjseo_user`
- Grant permissions
- Test connection

**You'll need:**
- PostgreSQL admin password
- Choose database name (default: mjseo_db)
- Choose username (default: mjseo_user)
- Set password for database user

**Save the connection string!** You'll need it for the backend .env file.

---

### Script 2: Setup Backend

```bash
./2-setup-backend.sh
```

This will:
- Copy .env.production to backend/.env
- Open .env for you to edit (nano editor)
- Create Python virtual environment
- Install dependencies
- Initialize database tables
- Test backend server

**Important:** When the script opens `.env`, update:
1. `DATABASE_URL` (use connection string from step 1)
2. `SECRET_KEY` (generate a secure key)

**To generate SECRET_KEY:**
```bash
openssl rand -hex 32
```

---

### Script 3: Build Frontend (Run on LOCAL machine)

```bash
./3-build-frontend.sh
```

⚠️ **Run this on your LOCAL computer, NOT on the server!**

This will:
- Copy .env.production
- Install dependencies (yarn)
- Build production bundle
- Create `frontend-source/build/` folder

**After building:**
Upload contents of `frontend-source/build/*` to:
```
/www/wwwroot/MarketAutoMailer.mj.publicvm.com/
```

The server root should have:
```
/www/wwwroot/MarketAutoMailer.mj.publicvm.com/
├── index.html
├── static/
│   ├── css/
│   ├── js/
│   └── media/
└── manifest.json
```

---

### Script 4: Start Services

```bash
./4-start-services.sh
```

This will:
- Update nginx configuration
- Test nginx config
- Reload nginx
- Start backend server (4 workers)
- Test backend health
- Display access information

---

## 🔍 Verification

### Test Backend

```bash
# Health check
curl http://localhost:9599/api/health

# Should return:
{"status":"healthy","service":"MJ SEO Backend",...}
```

### Test Frontend

1. Open https://marketautomailer.mj.publicvm.com
2. Should see landing page
3. No CORS errors in browser console (F12)
4. Can register/login

### Test Database

```bash
psql -h localhost -U mjseo_user -d mjseo_db -c "SELECT COUNT(*) FROM users;"

# Should return 1 (superadmin)
```

---

## 🐛 Troubleshooting

### Backend won't start

```bash
# Check logs
tail -f /www/wwwroot/MarketAutoMailer.mj.publicvm.com/backend/backend.log

# Check if port is in use
lsof -i :9599

# Check if PostgreSQL is running
sudo systemctl status postgresql
```

### CORS errors

```bash
# Check backend CORS settings
cd /www/wwwroot/MarketAutoMailer.mj.publicvm.com/backend
cat .env | grep CORS_ORIGINS

# Should be:
CORS_ORIGINS="http://marketautomailer.mj.publicvm.com,https://marketautomailer.mj.publicvm.com"

# Restart backend
pkill -f "uvicorn server:app"
cd /www/wwwroot/MarketAutoMailer.mj.publicvm.com/backend
source venv/bin/activate
nohup uvicorn server:app --host 0.0.0.0 --port 9599 --workers 4 > backend.log 2>&1 &
```

### 502 Bad Gateway

```bash
# Check if backend is running
ps aux | grep uvicorn

# Check nginx error log
tail -f /www/wwwlogs/marketautomailer.mj.publicvm.com.error.log

# Test backend directly
curl http://localhost:9599/api/health
```

---

## 📊 Service Management

### Start Backend

```bash
cd /www/wwwroot/MarketAutoMailer.mj.publicvm.com/backend
source venv/bin/activate
nohup uvicorn server:app --host 0.0.0.0 --port 9599 --workers 4 > backend.log 2>&1 &
```

### Stop Backend

```bash
pkill -f "uvicorn server:app"
```

### Restart Backend

```bash
pkill -f "uvicorn server:app"
cd /www/wwwroot/MarketAutoMailer.mj.publicvm.com/backend
source venv/bin/activate
nohup uvicorn server:app --host 0.0.0.0 --port 9599 --workers 4 > backend.log 2>&1 &
```

### Reload Nginx

```bash
sudo nginx -t                 # Test config
sudo systemctl reload nginx   # Reload
```

### Check Status

```bash
# Backend
ps aux | grep uvicorn
curl http://localhost:9599/api/health

# Nginx
sudo systemctl status nginx

# PostgreSQL
sudo systemctl status postgresql
```

---

## 🔐 Security Checklist

- [ ] Change DATABASE_URL password
- [ ] Generate new SECRET_KEY
- [ ] Change superadmin password
- [ ] Configure Stripe webhook
- [ ] Enable HSTS (in .env: ENABLE_HSTS="true")
- [ ] Set up firewall (ports 80, 443, 22 only)
- [ ] Configure database backups
- [ ] Set up log rotation

---

## 📞 Need Help?

Check the `docs/` folder for:
- DEPLOYMENT_CHECKLIST.md - Step-by-step guide
- PRODUCTION_DEPLOYMENT_GUIDE.md - Detailed instructions
- DEPLOYMENT_SUMMARY.md - Issue fixes

---

## ✅ Success Checklist

Deployment is successful when:

- [ ] Backend health check returns `{"status":"healthy"}`
- [ ] Frontend loads at https://marketautomailer.mj.publicvm.com
- [ ] No CORS errors in browser console
- [ ] Can register new user
- [ ] Can login with superadmin
- [ ] Can create SEO audit
- [ ] Database has data (check with psql)

---

**Version:** 2.0.0  
**Created:** January 2025  
**Status:** Ready to Deploy ✅
