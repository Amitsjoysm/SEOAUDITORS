# aaPanel Deployment Guide - MJ SEO Application

## 📦 What's Included

This production build includes:
- ✅ **Fixed Text Visibility Issue** - All input fields now have proper black text color with good contrast
- ✅ Frontend production build (optimized and minified)
- ✅ Backend configured for localhost:9599
- ✅ Complete deployment instructions
- ✅ Nginx configuration
- ✅ Database setup guide

---

## 🔧 Fixed Issues

### Text Visibility Fix ✅
**Problem:** Users couldn't see text they typed in input fields (invisible text)

**Solution Applied:**
1. Added explicit `color: #111827 !important` to all inputs and textareas
2. Updated `.apollo-input` class with proper text color
3. Added global CSS rules to ensure all form elements have dark text
4. Set placeholder color to gray (#9ca3af) for better UX

**Files Modified:**
- `/frontend/src/styles/apollo-theme.css` - Added color properties to .apollo-input
- `/frontend/src/components/ui/input.jsx` - Added inline style for text color
- `/frontend/src/components/ui/textarea.jsx` - Added inline style for text color  
- `/frontend/src/index.css` - Added global input color rules

---

## 📋 Prerequisites

1. **Server Requirements:**
   - Ubuntu 20.04+ or CentOS 7+
   - aaPanel installed
   - Python 3.10+
   - Node.js 18+ (for backend dependencies only)

2. **Database:**
   - SQLite (included) OR
   - PostgreSQL (recommended for production)

3. **Domain:**
   - Your domain pointed to the server
   - SSL certificate (Let's Encrypt via aaPanel)

---

## 🚀 Deployment Steps

### Step 1: Upload Files to aaPanel

1. **Create Website in aaPanel:**
   ```
   - Go to Website → Add Site
   - Domain: yourdomain.com
   - Root Directory: /www/wwwroot/yourdomain.com
   - PHP Version: Pure Static (we'll use Nginx only)
   ```

2. **Upload Frontend Build:**
   ```bash
   # Upload everything from /app/frontend/build/* to:
   /www/wwwroot/yourdomain.com/
   
   # Your directory structure should be:
   /www/wwwroot/yourdomain.com/
   ├── index.html
   ├── static/
   │   ├── css/
   │   └── js/
   ├── manifest.json
   └── favicon.ico
   ```

3. **Upload Backend:**
   ```bash
   # Create backend directory:
   mkdir -p /www/wwwroot/yourdomain.com/backend
   
   # Upload entire /app/backend/ folder to:
   /www/wwwroot/yourdomain.com/backend/
   ```

---

### Step 2: Setup Backend

1. **SSH into your server:**
   ```bash
   ssh root@your-server-ip
   cd /www/wwwroot/yourdomain.com/backend
   ```

2. **Create Python Virtual Environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   # Install core packages
   pip install fastapi uvicorn sqlalchemy aiosqlite asyncpg pyjwt bcrypt passlib python-dotenv pydantic requests beautifulsoup4 lxml groq openai reportlab python-docx stripe
   
   # Install additional packages
   pip install pydantic-settings email-validator python-multipart cryptography python-jose aiohttp anthropic google-generativeai
   ```

4. **Configure Environment:**
   ```bash
   # Copy production env file
   cp .env.production .env
   
   # Edit .env with your settings
   nano .env
   ```

   **Update these values in .env:**
   ```bash
   # If using PostgreSQL (recommended):
   DATABASE_URL="postgresql+asyncpg://username:password@localhost:5432/mjseo_db"
   
   # If using SQLite (for testing):
   DATABASE_URL="sqlite+aiosqlite:///./mjseo.db"
   
   # Update CORS with your domain:
   CORS_ORIGINS="http://yourdomain.com,https://yourdomain.com"
   
   # Update frontend URL:
   FRONTEND_URL="https://yourdomain.com"
   
   # Keep your API keys as-is (they're already configured)
   ```

5. **Initialize Database:**
   ```bash
   source venv/bin/activate
   python init_db_tables.py
   ```

   **This will create:**
   - 4 default plans (Free, Basic, Pro, Enterprise)
   - Superadmin account: `superadmin@test.com / test123`
   - 5 default themes
   - Default LLM settings

6. **Test Backend:**
   ```bash
   # Start backend temporarily to test
   uvicorn server:app --host 0.0.0.0 --port 9599
   
   # In another terminal, test:
   curl http://localhost:9599/api/health
   # Should return: {"status":"healthy"}
   
   # Stop with Ctrl+C
   ```

---

### Step 3: Setup Backend as Service

1. **Create Systemd Service:**
   ```bash
   sudo nano /etc/systemd/system/mjseo-backend.service
   ```

   **Add this content:**
   ```ini
   [Unit]
   Description=MJ SEO Backend Service
   After=network.target
   
   [Service]
   Type=simple
   User=www
   Group=www
   WorkingDirectory=/www/wwwroot/yourdomain.com/backend
   Environment="PATH=/www/wwwroot/yourdomain.com/backend/venv/bin"
   ExecStart=/www/wwwroot/yourdomain.com/backend/venv/bin/uvicorn server:app --host 127.0.0.1 --port 9599 --workers 4
   Restart=always
   RestartSec=10
   
   [Install]
   WantedBy=multi-user.target
   ```

2. **Enable and Start Service:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable mjseo-backend
   sudo systemctl start mjseo-backend
   
   # Check status:
   sudo systemctl status mjseo-backend
   ```

---

### Step 4: Configure Nginx in aaPanel

1. **Go to Website → Your Site → Settings → Config File**

2. **Replace the entire config with this:**

```nginx
server {
    listen 80;
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL Configuration (aaPanel will add this automatically)
    # ssl_certificate /path/to/cert.pem;
    # ssl_certificate_key /path/to/key.pem;
    
    root /www/wwwroot/yourdomain.com;
    index index.html;
    
    # Frontend - Serve static files
    location / {
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "public, max-age=31536000";
    }
    
    # Backend API - Reverse proxy to port 9599
    location /api {
        proxy_pass http://127.0.0.1:9599;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        proxy_busy_buffers_size 8k;
    }
    
    # Cache static assets
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json application/javascript;
    
    # Error pages
    error_page 404 /index.html;
}
```

3. **Replace `yourdomain.com` with your actual domain**

4. **Save and reload Nginx:**
   - Click "Save"
   - aaPanel will automatically reload Nginx

---

### Step 5: Setup SSL Certificate

1. **In aaPanel:**
   - Go to Website → Your Site → SSL
   - Click "Let's Encrypt"
   - Check your domain names
   - Click "Apply"
   - Wait for certificate to be issued

2. **Enable Force HTTPS:**
   - In SSL settings, enable "Force HTTPS"

---

### Step 6: Verify Deployment

1. **Test Frontend:**
   ```
   Visit: https://yourdomain.com
   - Should see landing page
   - No console errors
   ```

2. **Test Backend:**
   ```bash
   curl https://yourdomain.com/api/health
   # Should return: {"status":"healthy"}
   ```

3. **Test Full Flow:**
   - Register new user
   - Login
   - Create SEO audit
   - Check if text is visible in all input fields ✅

4. **Test Superadmin:**
   - Login with: `superadmin@test.com / test123`
   - Access admin dashboard
   - Verify all features work

---

## 🔐 Security Checklist

After deployment:

- [ ] Change superadmin password immediately
- [ ] Update SECRET_KEY in backend .env
- [ ] Enable HTTPS force redirect
- [ ] Configure firewall (allow only 80, 443, 22)
- [ ] Set up database backups
- [ ] Enable aaPanel security features
- [ ] Add your production API keys (if not using test keys)
- [ ] Review CORS_ORIGINS in backend .env

---

## 📊 Monitoring

1. **Check Backend Logs:**
   ```bash
   sudo journalctl -u mjseo-backend -f
   ```

2. **Check Nginx Access Logs:**
   ```bash
   tail -f /www/wwwlogs/yourdomain.com.log
   ```

3. **Check Nginx Error Logs:**
   ```bash
   tail -f /www/wwwlogs/yourdomain.com.error.log
   ```

4. **Backend Status:**
   ```bash
   sudo systemctl status mjseo-backend
   ```

---

## 🔄 Restart Services

```bash
# Restart backend
sudo systemctl restart mjseo-backend

# Restart Nginx
sudo nginx -t && sudo systemctl reload nginx

# Restart all
sudo systemctl restart mjseo-backend && sudo systemctl reload nginx
```

---

## 🐛 Troubleshooting

### Issue: Backend not starting
```bash
# Check logs
sudo journalctl -u mjseo-backend -n 50

# Check if port 9599 is in use
sudo netstat -tlnp | grep 9599

# Test manually
cd /www/wwwroot/yourdomain.com/backend
source venv/bin/activate
uvicorn server:app --host 127.0.0.1 --port 9599
```

### Issue: API calls failing (404)
```bash
# Check Nginx config
sudo nginx -t

# Verify backend is running
curl http://localhost:9599/api/health

# Check Nginx reverse proxy
curl -H "Host: yourdomain.com" http://localhost/api/health
```

### Issue: Database errors
```bash
# Re-initialize database
cd /www/wwwroot/yourdomain.com/backend
source venv/bin/activate
python init_db_tables.py
```

### Issue: Text still not visible in inputs
- Clear browser cache (Ctrl+Shift+Del)
- Hard reload (Ctrl+Shift+R)
- Check if old CSS is cached
- Verify build was uploaded correctly

---

## 📦 Quick Deploy Script

Save this as `/root/deploy-mjseo.sh`:

```bash
#!/bin/bash

DOMAIN="yourdomain.com"
WEBROOT="/www/wwwroot/$DOMAIN"

echo "🚀 Deploying MJ SEO Application..."

# Create directories
mkdir -p $WEBROOT/backend

# Backend setup
cd $WEBROOT/backend
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn sqlalchemy aiosqlite pyjwt bcrypt passlib python-dotenv pydantic requests beautifulsoup4 groq openai reportlab python-docx stripe pydantic-settings email-validator python-multipart

# Initialize database
python init_db_tables.py

# Create systemd service
sudo tee /etc/systemd/system/mjseo-backend.service > /dev/null <<EOF
[Unit]
Description=MJ SEO Backend
After=network.target

[Service]
Type=simple
User=www
Group=www
WorkingDirectory=$WEBROOT/backend
Environment="PATH=$WEBROOT/backend/venv/bin"
ExecStart=$WEBROOT/backend/venv/bin/uvicorn server:app --host 127.0.0.1 --port 9599 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable mjseo-backend
sudo systemctl start mjseo-backend

echo "✅ Deployment complete!"
echo "🔐 Default superadmin: superadmin@test.com / test123"
echo "🌐 Visit: https://$DOMAIN"
```

---

## 📞 Support

**Default Credentials:**
- Superadmin: `superadmin@test.com / test123`
- Test User: `test@example.com / test123`

**⚠️ CHANGE THESE IMMEDIATELY IN PRODUCTION!**

---

## ✅ Success Criteria

Your deployment is successful when:

✅ Frontend loads at https://yourdomain.com  
✅ Backend health check returns `{"status":"healthy"}`  
✅ Users can type and see text in all input fields (black text, good contrast)  
✅ Can register new user  
✅ Can login with superadmin account  
✅ Can create SEO audit  
✅ No CORS errors in browser console  
✅ Database has data (users, plans, themes)  
✅ SSL certificate is active  

---

**Version:** 1.0.0  
**Build Date:** February 2025  
**Text Visibility:** ✅ FIXED  
**Production Ready:** ✅ YES
