# 🚀 Quick Reference - MJ SEO Deployment

## 📦 Files Location
```
/app/production-package/
├── frontend-build/          → Upload to /www/wwwroot/yourdomain.com/
├── backend/                 → Upload to /www/wwwroot/yourdomain.com/backend/
├── nginx.conf              → Copy to aaPanel nginx config
├── setup.sh                → Run on server to auto-setup
└── docs/                   → Full deployment guide
```

## ⚡ Quick Deploy (3 Steps)

### Step 1: Upload
```bash
# Frontend → /www/wwwroot/yourdomain.com/
# Backend  → /www/wwwroot/yourdomain.com/backend/
```

### Step 2: Run Setup
```bash
cd /www/wwwroot/yourdomain.com
chmod +x backend/setup.sh
sudo ./backend/setup.sh
# Enter your domain when prompted
```

### Step 3: Configure Nginx
```
1. aaPanel → Website → Config
2. Copy content from nginx.conf
3. Replace 'yourdomain.com' with YOUR domain
4. Save and reload
```

**✅ Done! Visit https://yourdomain.com**

---

## 🔑 Default Credentials
```
Superadmin: superadmin@test.com / test123
Test User:  test@example.com / test123

⚠️  CHANGE IMMEDIATELY IN PRODUCTION!
```

---

## ⚙️ Service Commands

### Backend Service
```bash
sudo systemctl start mjseo-backend      # Start
sudo systemctl stop mjseo-backend       # Stop
sudo systemctl restart mjseo-backend    # Restart
sudo systemctl status mjseo-backend     # Status
sudo journalctl -u mjseo-backend -f     # Logs
```

### Nginx
```bash
sudo nginx -t                           # Test config
sudo systemctl reload nginx             # Reload
sudo systemctl restart nginx            # Restart
```

---

## 🧪 Quick Tests

### Backend Health
```bash
curl http://localhost:9599/api/health
# Expected: {"status":"healthy"}
```

### Full Test
```
1. Visit https://yourdomain.com
2. Try typing in login fields
3. ✅ Text should be black and visible
4. Register new user
5. Create SEO audit
```

---

## 🐛 Quick Troubleshooting

### Text Not Visible?
```bash
# Clear browser cache
Ctrl + Shift + Del

# Hard reload
Ctrl + Shift + R
```

### Backend Not Working?
```bash
# Check status
sudo systemctl status mjseo-backend

# Check logs
sudo journalctl -u mjseo-backend -n 50

# Restart
sudo systemctl restart mjseo-backend
```

### API 404 Errors?
```bash
# Test backend directly
curl http://localhost:9599/api/health

# Check nginx config
sudo nginx -t

# Check nginx logs
tail -f /www/wwwlogs/yourdomain.com.error.log
```

---

## 📁 Important Files

### On Server
```
/www/wwwroot/yourdomain.com/
├── index.html               # Frontend
├── static/                  # Assets
└── backend/
    ├── server.py           # Main app
    ├── .env                # Config
    └── mjseo.db            # Database
```

### Service File
```
/etc/systemd/system/mjseo-backend.service
```

### Nginx Config
```
aaPanel → Website → yourdomain.com → Settings → Config
```

---

## 🔐 Post-Deploy Security

```bash
# 1. Change passwords
Visit: /settings

# 2. Update SECRET_KEY
nano /www/wwwroot/yourdomain.com/backend/.env
# Change SECRET_KEY value

# 3. Restart backend
sudo systemctl restart mjseo-backend

# 4. Enable firewall
sudo ufw allow 22,80,443/tcp
sudo ufw enable

# 5. Setup SSL
aaPanel → Website → SSL → Let's Encrypt
```

---

## 🎯 Success Checklist

- [ ] Frontend loads at https://yourdomain.com
- [ ] Backend health check returns healthy
- [ ] **Text visible in all input fields** ✅
- [ ] Can register new user
- [ ] Can login
- [ ] Can create SEO audit
- [ ] No console errors
- [ ] SSL certificate active
- [ ] Changed default passwords

---

## 📊 Configuration

### Backend
```
Port: 9599 (localhost)
API: https://yourdomain.com/api
Workers: 4
```

### Database
```
Type: SQLite (default) or PostgreSQL
Location: backend/mjseo.db
```

### Features
```
✅ 132 SEO checks
✅ AI insights (Groq, OpenAI, etc.)
✅ PDF/DOCX reports
✅ Admin dashboard
✅ Multi-theme support
✅ Text visibility FIXED
```

---

## 📞 Need Help?

**Full Documentation:**
```
/app/production-package/docs/AAPANEL_DEPLOYMENT_GUIDE.md
```

**Package README:**
```
/app/production-package/README.md
```

**Build Summary:**
```
/app/PRODUCTION_BUILD_SUMMARY.md
```

---

## 🎉 Quick Stats

- **Deployment Time:** 15-30 min
- **Text Visibility:** ✅ FIXED
- **Production Ready:** ✅ YES
- **Frontend Size:** 180 KB (gzipped)
- **Backend Port:** 9599
- **SSL:** Via Let's Encrypt

---

**Version:** 1.0.0 | **Build:** Feb 2025 | **Status:** READY ✅
