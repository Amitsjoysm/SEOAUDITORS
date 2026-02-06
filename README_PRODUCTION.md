# MJ SEO - Production Deployment Package

## 📦 What's Included

This package contains everything you need to deploy MJ SEO to production on aaPanel with PostgreSQL.

### 🎯 Your Current Issues - SOLVED ✅

1. **CORS Error** ❌ → ✅ Fixed with updated nginx config + backend CORS settings
2. **Database Connection Error** ❌ → ✅ Fixed with PostgreSQL setup guide + proper DATABASE_URL
3. **Backend Crashes** ❌ → ✅ Fixed by resolving database connection

---

## 📚 Documentation Files

| File | Purpose | When to Use |
|------|---------|-------------|
| **DEPLOYMENT_CHECKLIST.md** | Step-by-step deployment checklist | Start here - your main guide |
| **PRODUCTION_DEPLOYMENT_GUIDE.md** | Detailed deployment instructions | Reference for specific steps |
| **DEPLOYMENT_SUMMARY.md** | Issue analysis & quick fixes | Understand what went wrong |
| **BUILD_README.md** | Build instructions | When building frontend locally |
| **README_PRODUCTION.md** | This file - overview | Get oriented |

---

## 🚀 Quick Start (3 Options)

### Option 1: Automated Setup ⚡ (Fastest)

**For the backend on your server:**

```bash
# 1. Upload 'backend' folder and 'server-quick-setup.sh' to server
# 2. Run the setup script:

cd /www/wwwroot/MarketAutoMailer.mj.publicvm.com/deployment-package/
chmod +x server-quick-setup.sh
./server-quick-setup.sh
```

This will:
- ✅ Create PostgreSQL database
- ✅ Set up Python virtual environment
- ✅ Install all dependencies
- ✅ Create .env file with correct settings
- ✅ Initialize database with default data
- ✅ Test backend server

**For the frontend:**

```bash
# On your local machine:
cd /app
chmod +x build-production.sh
./build-production.sh

# Upload contents of 'frontend/build/*' to:
# /www/wwwroot/MarketAutoMailer.mj.publicvm.com/
```

---

### Option 2: Step-by-Step Manual Setup 📋 (Recommended if you want control)

Follow **DEPLOYMENT_CHECKLIST.md** for detailed steps with checkpoints.

---

### Option 3: Quick Fix (If everything is already uploaded) 🔧

If you just need to fix the current issues:

1. **Fix Database Connection:**
```bash
cd /www/wwwroot/MarketAutoMailer.mj.publicvm.com/deployment-package/backend/
nano .env

# Update this line:
DATABASE_URL="postgresql+asyncpg://mjseo_user:YourPassword@localhost:5432/mjseo_db"
CORS_ORIGINS="http://marketautomailer.mj.publicvm.com,https://marketautomailer.mj.publicvm.com"
```

2. **Create Database:**
```bash
sudo -u postgres psql
CREATE DATABASE mjseo_db;
CREATE USER mjseo_user WITH PASSWORD 'YourPassword';
GRANT ALL PRIVILEGES ON DATABASE mjseo_db TO mjseo_user;
\q
```

3. **Initialize Database:**
```bash
cd /www/wwwroot/MarketAutoMailer.mj.publicvm.com/deployment-package/backend/
source venv/bin/activate
python init_db_tables.py
```

4. **Restart Backend:**
```bash
pkill -f "uvicorn server:app"
cd /www/wwwroot/MarketAutoMailer.mj.publicvm.com/deployment-package/backend/
source venv/bin/activate
nohup uvicorn server:app --host 0.0.0.0 --port 9599 --workers 4 > backend.log 2>&1 &
```

5. **Update Nginx:**
```bash
# Copy the nginx-production.conf to your nginx config
# Then:
sudo nginx -t
sudo systemctl reload nginx
```

---

## 📁 File Structure

```
/app/
├── backend/
│   ├── .env.production          ⭐ NEW - Production environment config
│   ├── .env.template           ⭐ NEW - Environment template
│   ├── .env                     ⚠️ UPDATE THIS on server
│   ├── requirements.txt
│   ├── server.py
│   ├── database.py
│   ├── models.py
│   └── ...
│
├── frontend/
│   ├── .env.production          ⭐ NEW - Production environment config
│   ├── .env                     ⚠️ UPDATE THIS for build
│   ├── package.json
│   └── ...
│
├── build-production.sh          ⭐ NEW - Frontend build script (Linux/Mac)
├── build-production.bat         ⭐ NEW - Frontend build script (Windows)
├── setup-backend-production.sh  ⭐ NEW - Backend setup script
├── server-quick-setup.sh        ⭐ NEW - Server quick setup
├── nginx-production.conf        ⭐ NEW - Fixed nginx config
│
├── DEPLOYMENT_CHECKLIST.md      ⭐ START HERE
├── PRODUCTION_DEPLOYMENT_GUIDE.md
├── DEPLOYMENT_SUMMARY.md
├── BUILD_README.md
└── README_PRODUCTION.md         ⭐ This file
```

---

## 🔑 Critical Configuration

### Backend Environment Variables (.env)

```bash
# ⚠️ MUST UPDATE THESE:
DATABASE_URL="postgresql+asyncpg://mjseo_user:PASSWORD@localhost:5432/mjseo_db"
CORS_ORIGINS="http://marketautomailer.mj.publicvm.com,https://marketautomailer.mj.publicvm.com"
SECRET_KEY="generate-new-secure-key-here"

# ✅ Verify these exist:
GROQ_API_KEY="your_groq_key"
EXA_API_KEY="your_exa_key"
STRIPE_SECRET_KEY="your_stripe_key"
```

### Frontend Environment Variables (.env)

```bash
# ⚠️ MUST BE CORRECT:
REACT_APP_BACKEND_URL=https://marketautomailer.mj.publicvm.com/api

# ✅ Verify:
REACT_APP_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

### Nginx Configuration

**Key changes from your original config:**
- ❌ Removed all `add_header 'Access-Control-*'` directives
- ✅ Let FastAPI handle CORS completely
- ✅ Added React Router support with `try_files`

---

## ✅ Verification Steps

### 1. Test Backend

```bash
# Health check
curl http://localhost:9599/api/health
# Expected: {"status":"healthy",...}

# Plans list
curl http://localhost:9599/api/plans
# Expected: [{"name":"Free",...},...]

# From browser console
fetch('https://marketautomailer.mj.publicvm.com/api/health')
  .then(r => r.json())
  .then(console.log)
# Expected: No CORS error, returns health data
```

### 2. Test Frontend

1. Open https://marketautomailer.mj.publicvm.com
2. Should see landing page (not blank)
3. Open browser console (F12) - no errors
4. Try to register - should work without CORS error

### 3. Test Database

```bash
psql -h localhost -U mjseo_user -d mjseo_db -c "SELECT COUNT(*) FROM users;"
# Expected: At least 1 user (superadmin)
```

---

## 🐛 Common Issues & Solutions

### Issue: "Could not parse SQLAlchemy URL"

**Solution:**
```bash
# Check DATABASE_URL format in .env
cat /www/wwwroot/.../backend/.env | grep DATABASE_URL

# Must be:
DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/dbname"
#             ^^^^^^^^^^^^^^^^ REQUIRED!
```

### Issue: CORS errors

**Solution:**
1. Remove CORS headers from nginx config
2. Update backend CORS_ORIGINS to include both http and https
3. Restart backend and reload nginx

### Issue: Backend won't start

**Check logs:**
```bash
tail -f /www/wwwroot/.../backend/backend.log
```

**Common causes:**
- Wrong DATABASE_URL
- PostgreSQL not running
- Port 9599 already in use
- Missing dependencies

### Issue: Frontend blank page

**Solutions:**
1. Check browser console for errors
2. Verify build files uploaded correctly
3. Check REACT_APP_BACKEND_URL in build
4. Rebuild frontend if needed

---

## 📊 Service Management

### Start Backend

```bash
cd /www/wwwroot/MarketAutoMailer.mj.publicvm.com/deployment-package/backend/
source venv/bin/activate
nohup uvicorn server:app --host 0.0.0.0 --port 9599 --workers 4 > backend.log 2>&1 &
```

### Stop Backend

```bash
pkill -f "uvicorn server:app"
```

### Restart Services

```bash
# Backend
pkill -f "uvicorn server:app"
cd /www/wwwroot/MarketAutoMailer.mj.publicvm.com/deployment-package/backend/
source venv/bin/activate
nohup uvicorn server:app --host 0.0.0.0 --port 9599 --workers 4 > backend.log 2>&1 &

# Nginx
sudo systemctl reload nginx

# PostgreSQL
sudo systemctl restart postgresql
```

### Check Status

```bash
# Is backend running?
ps aux | grep uvicorn
curl http://localhost:9599/api/health

# Is nginx running?
sudo systemctl status nginx

# Is PostgreSQL running?
sudo systemctl status postgresql
```

### View Logs

```bash
# Backend logs
tail -f /www/wwwroot/.../backend/backend.log

# Nginx access log
tail -f /www/wwwlogs/marketautomailer.mj.publicvm.com.log

# Nginx error log
tail -f /www/wwwlogs/marketautomailer.mj.publicvm.com.error.log
```

---

## 🔐 Security Checklist

Before going live:

- [ ] Change SECRET_KEY in backend .env
- [ ] Use strong PostgreSQL password
- [ ] Change superadmin password from default (test123)
- [ ] Configure Stripe webhook URL
- [ ] Enable HSTS (ENABLE_HSTS="true" in .env)
- [ ] Configure firewall (allow only 80, 443, 22)
- [ ] Set up database backups
- [ ] Set up log rotation
- [ ] Configure uptime monitoring

---

## 📈 Performance Optimization

Already configured:

✅ Backend with 4 workers  
✅ Nginx GZIP compression  
✅ Static file caching (1 year)  
✅ Frontend production build (minified)  
✅ Async database operations  
✅ Connection pooling  

---

## 🎓 Learning Resources

### Understanding the Stack

- **FastAPI Backend**: Async Python web framework
- **React Frontend**: Single-page application
- **PostgreSQL**: Relational database
- **Nginx**: Reverse proxy and static file server
- **aaPanel**: Server management panel

### Architecture

```
User Browser
    ↓
Nginx (Port 443 HTTPS)
    ↓
    ├─→ Static Files (/www/wwwroot/.../)  [Frontend]
    │
    └─→ /api/* → FastAPI (Port 9599)      [Backend]
            ↓
        PostgreSQL (Port 5432)             [Database]
```

---

## 📞 Getting Help

### First Steps

1. Check **DEPLOYMENT_CHECKLIST.md** for step-by-step guide
2. Review **PRODUCTION_DEPLOYMENT_GUIDE.md** for detailed instructions
3. Look at **DEPLOYMENT_SUMMARY.md** for issue analysis

### Debug Process

1. Check service status:
   ```bash
   ps aux | grep -E "uvicorn|nginx|postgres"
   ```

2. Check logs:
   ```bash
   tail -f backend.log
   tail -f /www/wwwlogs/marketautomailer*.error.log
   ```

3. Test components individually:
   ```bash
   # Database
   psql -h localhost -U mjseo_user -d mjseo_db
   
   # Backend
   curl http://localhost:9599/api/health
   
   # Nginx
   sudo nginx -t
   ```

---

## 🎯 Next Steps

After successful deployment:

1. **Test thoroughly**
   - Register new user
   - Create SEO audit
   - Download reports
   - Test all features

2. **Configure monitoring**
   - Set up uptime monitoring
   - Configure error alerts
   - Monitor database size

3. **Optimize**
   - Tune database queries
   - Add caching where needed
   - Monitor performance

4. **Secure**
   - Change default passwords
   - Enable HSTS
   - Configure backups
   - Set up SSL renewal

---

## 📝 Default Credentials

**Superadmin Account:**
- Email: `superadmin@test.com`
- Password: `test123`

⚠️ **CHANGE THIS IMMEDIATELY AFTER FIRST LOGIN!**

---

## 🚀 Quick Commands Reference

```bash
# Build frontend
cd /app && ./build-production.sh

# Setup backend
cd /app && ./setup-backend-production.sh

# Server setup (on production server)
./server-quick-setup.sh

# Restart backend
pkill -f uvicorn && cd backend && source venv/bin/activate && \
nohup uvicorn server:app --host 0.0.0.0 --port 9599 --workers 4 > backend.log 2>&1 &

# Check all services
ps aux | grep -E "uvicorn|nginx|postgres" && \
curl http://localhost:9599/api/health && \
sudo systemctl status nginx
```

---

**Version:** 2.0.0  
**Last Updated:** January 2025  
**Status:** Production Ready ✅

---

## 🙏 Support

For issues or questions, refer to:
- DEPLOYMENT_CHECKLIST.md (step-by-step guide)
- PRODUCTION_DEPLOYMENT_GUIDE.md (detailed reference)
- DEPLOYMENT_SUMMARY.md (issue analysis)

**All documentation is in /app/ directory**
