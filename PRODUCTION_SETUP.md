# MJ SEO - Production Setup Guide

## 🚀 Production-Ready AI SEO Audit Report Generator

### Features
- ✅ 135 Comprehensive SEO Checks (exceeds 132 requirement)
- ✅ AI-Powered Insights with Groq Llama 3.3 70B
- ✅ Real-time Website Crawling (up to 20 pages)
- ✅ Detailed PDF & DOCX Reports
- ✅ AI SEO Consultant Chat Interface
- ✅ JWT Authentication & Role-Based Access Control
- ✅ Super Admin Dashboard with Full CRUD
- ✅ API Token System for External Access
- ✅ Dual Payment Integration (Stripe + Razorpay)
- ✅ PostgreSQL + Redis Support
- ✅ Scalable Architecture for 10,000+ Users
- ✅ Modern 3D UI with Pastel Themes

---

## 📋 Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for development)
- Python 3.11+ (for development)
- Domain name (for production)

---

## 🔧 Environment Configuration

### Backend Environment Variables (`/app/backend/.env`)

```env
# Database - PostgreSQL for Production
DATABASE_URL=postgresql+asyncpg://mjseo_user:mjseo_secure_pass_2024@postgres:5432/mjseo_db

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# AI Services
GROQ_API_KEY=gsk_your_groq_api_key_here
EXA_API_KEY=your_exa_api_key_here

# Payment Providers
STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
RAZORPAY_KEY_ID=rzp_live_your_key_id
RAZORPAY_KEY_SECRET=your_razorpay_secret

# Redis (for caching and queue)
REDIS_URL=redis://redis:6379/0
```

### Frontend Environment Variables (`/app/frontend/.env`)

```env
REACT_APP_BACKEND_URL=https://api.yourdomain.com
REACT_APP_STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_publishable_key
```

---

## 🐳 Docker Deployment

### 1. Start PostgreSQL and Redis

```bash
cd /app
docker-compose up -d
```

This starts:
- PostgreSQL on port 5432
- Redis on port 6379

### 2. Initialize Database

```bash
# Update DATABASE_URL in backend/.env to use PostgreSQL
cd /app/backend
python init_db_tables.py
```

This creates:
- All database tables
- 4 default plans (Free, Basic, Pro, Enterprise)
- 5 pastel color themes
- Superadmin account: `superadmin@test.com` / `test123`

### 3. Install Dependencies

Backend:
```bash
cd /app/backend
pip install -r requirements.txt
```

Frontend:
```bash
cd /app/frontend
yarn install
```

### 4. Start Services

Backend:
```bash
cd /app/backend
uvicorn server:app --host 0.0.0.0 --port 8001 --workers 4
```

Frontend:
```bash
cd /app/frontend
yarn build
# Serve with nginx or any static file server
```

---

## 🔐 Default Accounts

### Superadmin
- Email: `superadmin@test.com`
- Password: `test123`
- Access: Full admin dashboard, all user data, plan management

### Test User
- Email: `test@example.com`
- Password: `test123`
- Access: Regular user features

**⚠️ IMPORTANT: Change these credentials in production!**

---

## 📊 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh JWT token

### Audits
- `POST /api/audits/` - Create new audit
- `GET /api/audits/` - List user's audits
- `GET /api/audits/{id}` - Get audit details

### Reports
- `GET /api/reports/{audit_id}/pdf` - Download PDF report
- `GET /api/reports/{audit_id}/docx` - Download DOCX report

### Chat
- `POST /api/chat/{audit_id}` - Chat with AI SEO consultant
- `GET /api/chat/{audit_id}/messages` - Get chat history

### API Tokens
- `POST /api/api-tokens/` - Create new API token
- `GET /api/api-tokens/` - List tokens
- `DELETE /api/api-tokens/{id}` - Delete token

### Admin (Superadmin only)
- `GET /api/admin/dashboard` - Admin dashboard stats
- `GET /api/admin/users` - List all users
- `GET /api/admin/audits` - List all audits
- `PUT /api/admin/users/{id}` - Update user
- `DELETE /api/admin/users/{id}` - Delete user

### Plans
- `GET /api/plans/` - List all plans
- `POST /api/plans/` - Create plan (admin)
- `PUT /api/plans/{id}` - Update plan (admin)

### Payments
- `POST /api/payments/create-checkout` - Create payment session
- `POST /api/payments/webhook` - Payment webhook

---

## 🎨 Theme System

The app includes 5 default pastel themes:
1. Lavender Dream (default)
2. Ocean Breeze
3. Sunset Glow
4. Mint Fresh
5. Rose Garden

Superadmin can activate/manage themes globally from the admin dashboard.

---

## 📈 Scaling Considerations

### For 10,000+ Users:

1. **Database**: Use PostgreSQL with connection pooling
2. **Caching**: Redis for session management and API rate limiting
3. **Queue**: Celery with Redis for background audit processing
4. **Load Balancing**: Use nginx or cloud load balancer
5. **CDN**: CloudFront, Cloudflare for static assets
6. **Monitoring**: Sentry for error tracking, Prometheus for metrics

### Horizontal Scaling:
- Multiple backend instances behind load balancer
- Shared PostgreSQL database
- Shared Redis instance
- Separate Celery workers for audit processing

---

## 🔒 Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Change default admin credentials
- [ ] Enable HTTPS only
- [ ] Set up rate limiting
- [ ] Configure CORS properly
- [ ] Use environment-specific API keys
- [ ] Enable database backups
- [ ] Set up monitoring and alerts
- [ ] Implement input validation
- [ ] Enable SQL injection protection (already built-in with SQLAlchemy)

---

## 🧪 Testing

Backend tests:
```bash
cd /app/backend
pytest
```

Frontend tests:
```bash
cd /app/frontend
yarn test
```

---

## 📝 API Token Usage (MCP Server)

API tokens are prefixed with `mjseo_` and can be used for:
- External API access
- MCP server integration
- Third-party integrations

Example:
```bash
curl -H "Authorization: Bearer mjseo_your_token_here" \
  https://api.yourdomain.com/api/audits/
```

---

## 🐛 Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL status
docker-compose ps

# View PostgreSQL logs
docker-compose logs postgres

# Test connection
docker exec -it mjseo_postgres psql -U mjseo_user -d mjseo_db
```

### Backend Issues
```bash
# Check backend logs
tail -f /var/log/supervisor/backend.*.log

# Restart backend
sudo supervisorctl restart backend
```

### Frontend Build Issues
```bash
# Clear cache
rm -rf node_modules
yarn install

# Rebuild
yarn build
```

---

## 📧 Support

For issues or questions:
1. Check logs in `/var/log/supervisor/`
2. Review error messages in browser console
3. Check database connection
4. Verify API keys are set correctly

---

## 🎯 Production Deployment Checklist

- [ ] Environment variables configured
- [ ] PostgreSQL running and initialized
- [ ] Redis running
- [ ] Database tables created
- [ ] Default plans created
- [ ] Superadmin account created and password changed
- [ ] API keys (Groq, Exa) configured
- [ ] Payment providers configured (optional)
- [ ] HTTPS enabled
- [ ] Domain configured
- [ ] CORS settings updated
- [ ] Backups configured
- [ ] Monitoring set up
- [ ] Rate limiting enabled
- [ ] Security headers configured

---

## 🚀 Quick Start (Development)

```bash
# 1. Clone and navigate
cd /app

# 2. Start Docker services
docker-compose up -d

# 3. Install backend dependencies
cd backend
pip install -r requirements.txt

# 4. Initialize database
python init_db_tables.py

# 5. Start backend
sudo supervisorctl restart backend

# 6. Install frontend dependencies
cd ../frontend
yarn install

# 7. Start frontend
sudo supervisorctl restart frontend

# 8. Access the app
# Frontend: http://localhost:3000
# Backend: http://localhost:8001
```

---

## 📚 Documentation

- API Documentation: http://localhost:8001/docs (Swagger UI)
- ReDoc: http://localhost:8001/redoc

---

**Built with ❤️ using FastAPI, React, PostgreSQL, and AI**
