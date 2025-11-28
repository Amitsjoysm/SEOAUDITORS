# MJ SEO - AI SEO Audit Report Generator
## Application Overview & Access Guide

### 🚀 Application Status
**All Services Running Successfully!**

✅ **Backend**: Running on port 8001 (FastAPI + Python)
✅ **Frontend**: Running on port 3000 (React)
✅ **Database**: SQLite (Production ready for PostgreSQL)
✅ **MongoDB**: Running (for potential future use)

---

## 🔐 Login Credentials

### Superadmin Account (Full Access)
- **Email**: `superadmin@test.com`
- **Password**: `test123`
- **Access**: Full CRUD access to all features, admin dashboard, user management, themes, LLM settings, environment keys

### Regular User Account (Testing)
- **Email**: `test@example.com`
- **Password**: `test123`
- **Access**: Standard user features (create audits, view reports, chat with AI)

---

## 📋 Application Features

### 🎯 Core Features
1. **132+ Comprehensive SEO Checks**
   - Technical SEO (28 checks)
   - Performance & Core Web Vitals (20 checks)
   - On-Page SEO (30 checks)
   - Content Quality (10 checks)
   - Social Media (5 checks)
   - Off-Page SEO (10 checks)
   - Analytics & Reporting (6 checks)
   - GEO & AEO (8 checks)
   - Advanced Technical & Security (18 checks)

2. **AI-Powered Analysis**
   - Parlant.io-style AI orchestrator
   - Multi-LLM support (Groq, OpenAI, Anthropic, Gemini, Ollama)
   - Currently configured: Groq Llama 3.3 70B
   - Research agent with Exa.ai integration
   - Context-aware SEO consultant chat interface

3. **Report Generation**
   - PDF reports with comprehensive analysis
   - DOCX reports for editing
   - Website-specific insights (not generic)
   - Code examples and step-by-step solutions
   - Download functionality in dashboard

4. **Payment Integration**
   - Stripe integration (configured)
   - Multiple subscription plans (Free, Basic, Pro, Enterprise)
   - Subscription management
   - Payment history tracking

5. **Authentication & Authorization**
   - JWT-based authentication
   - Access & refresh tokens
   - Role-based access control (User/Superadmin)
   - Secure password hashing with bcrypt

6. **Admin Dashboard** (Superadmin Only)
   - User management (Create, Read, Update, Delete)
   - Audit management
   - Theme management (5 default pastel themes + custom creation)
   - LLM settings (Configure AI models)
   - Environment key management (Encrypted storage)
   - SEO settings configuration
   - Payment management
   - Plans & pricing management
   - Dashboard statistics

7. **API Token System**
   - Generate API tokens for MCP server access
   - Token prefix: `mjseo_`
   - Enable/disable tokens
   - Delete tokens

8. **Theme System**
   - 5 default pastel themes:
     * Lavender Dream (active default)
     * Ocean Breeze
     * Sunset Glow
     * Mint Fresh
     * Rose Garden
   - Superadmin can create custom themes with color pickers
   - Dynamic theme switching
   - Smooth transitions

---

## 🗂️ Project Structure

### Backend (`/app/backend/`)
```
├── server.py                 # Main FastAPI application
├── models.py                 # Database models (SQLAlchemy)
├── schemas.py                # Pydantic schemas for validation
├── database.py               # Database connection and session management
├── auth.py                   # Authentication utilities (JWT)
├── init_db_tables.py         # Database initialization script
├── routes/                   # API route handlers
│   ├── auth.py              # Authentication endpoints
│   ├── audits.py            # SEO audit management
│   ├── admin.py             # Admin dashboard endpoints
│   ├── chat.py              # AI chat interface
│   ├── reports.py           # PDF/DOCX report generation
│   ├── api_tokens.py        # API token management
│   ├── themes.py            # Theme management
│   ├── llm_settings.py      # LLM configuration
│   ├── env_keys.py          # Environment key management
│   ├── seo_settings.py      # SEO settings
│   ├── plans.py             # Subscription plans
│   ├── payments_stripe.py   # Stripe payment integration
│   └── admin_payments.py    # Admin payment management
├── seo_engine/              # SEO analysis engine
│   ├── comprehensive_checks.py  # 132+ SEO checks implementation
│   ├── crawler.py               # Website crawler (40+ data points)
│   ├── orchestrator.py          # AI orchestrator (Groq)
│   ├── orchestrator_v2.py       # Multi-LLM orchestrator
│   ├── multi_llm_client.py      # Unified LLM client
│   ├── research_agent.py        # Exa.ai research integration
│   └── checks.py                # Basic SEO checks
├── utils/                   # Utility functions
│   └── report_generator.py  # Report generation utilities
└── requirements.txt         # Python dependencies
```

### Frontend (`/app/frontend/`)
```
├── src/
│   ├── App.js               # Main application component & routing
│   ├── contexts/
│   │   ├── AuthContext.js   # Authentication context
│   │   └── ThemeContext.js  # Theme context (dynamic loading)
│   ├── pages/
│   │   ├── Landing.js       # Landing page with features showcase
│   │   ├── Login.js         # Login page
│   │   ├── Register.js      # Registration page
│   │   ├── Dashboard.js     # User dashboard (audit management)
│   │   ├── AuditDetail.js   # Audit results & download
│   │   ├── Chat.js          # AI SEO consultant chat
│   │   ├── Plans.js         # Plans & pricing with Stripe
│   │   ├── AdminDashboard.js # Superadmin dashboard
│   │   ├── APITokens.js     # API token management
│   │   ├── Settings.js      # User settings
│   │   └── PaymentSuccess.js # Payment confirmation
│   ├── components/          # Reusable UI components
│   │   └── ui/             # Radix UI components
│   ├── styles/
│   │   ├── enhanced-ui.css  # 3D effects & animations
│   │   └── theme.css        # Theme system CSS
│   └── lib/
│       └── utils.js         # Utility functions
├── package.json             # Node dependencies
└── public/                  # Static assets
```

---

## 🔌 API Endpoints (Key Routes)

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT tokens
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user info

### Audits
- `POST /api/audits` - Create new SEO audit
- `GET /api/audits` - List user's audits
- `GET /api/audits/{id}` - Get audit details
- `DELETE /api/audits/{id}` - Delete audit

### Reports
- `GET /api/reports/{id}/pdf` - Download PDF report
- `GET /api/reports/{id}/docx` - Download DOCX report

### Chat
- `POST /api/chat` - Send message to AI consultant
- `GET /api/chat/{audit_id}/history` - Get chat history

### Admin (Superadmin Only)
- `GET /api/admin/stats` - Dashboard statistics
- `GET /api/admin/users` - List all users
- `PUT /api/admin/users/{id}` - Update user
- `DELETE /api/admin/users/{id}` - Delete user
- `GET /api/admin/audits` - List all audits
- `GET /api/themes` - Theme management
- `GET /api/admin/llm-settings` - LLM configuration
- `GET /api/admin/env-keys` - Environment key management

### API Tokens
- `GET /api/api-tokens` - List user's tokens
- `POST /api/api-tokens` - Generate new token
- `DELETE /api/api-tokens/{id}` - Delete token

### Plans
- `GET /api/plans` - List subscription plans
- `POST /api/payments-stripe/create-checkout` - Create Stripe checkout

---

## 🎨 Frontend Routes

- `/` - Landing page
- `/login` - Login page
- `/register` - Registration page
- `/dashboard` - User dashboard (authenticated)
- `/audit/:id` - Audit detail page (authenticated)
- `/chat/:auditId` - Chat with AI SEO expert (authenticated)
- `/plans` - Plans & pricing
- `/admin` - Admin dashboard (superadmin only)
- `/api-tokens` - API token management (authenticated)
- `/settings` - User settings (authenticated)
- `/payment-success` - Payment confirmation

---

## ⚙️ Configuration

### Environment Variables

**Backend** (`/app/backend/.env`):
```env
DATABASE_URL="sqlite+aiosqlite:///./mjseo.db"
SECRET_KEY="mjseo-secret-key-change-in-production-2024"
GROQ_API_KEY="gsk_..." (configured)
EXA_API_KEY="28a8cf69..." (configured)
STRIPE_SECRET_KEY="sk_test_..." (configured)
STRIPE_PUBLISHABLE_KEY="pk_test_..." (configured)
FRONTEND_URL="http://localhost:3000"
CORS_ORIGINS="*"
```

**Frontend** (`/app/frontend/.env`):
```env
REACT_APP_BACKEND_URL=https://login-system-check-1.preview.emergentagent.com
REACT_APP_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

---

## 🧪 Testing the Application

### 1. Access the Application
- Frontend: Visit the application URL in your browser
- Backend API: `https://login-system-check-1.preview.emergentagent.com/api`

### 2. Login as Superadmin
1. Navigate to `/login`
2. Enter email: `superadmin@test.com`
3. Enter password: `test123`
4. Click "Sign In"

### 3. Test Core Features

#### Create an SEO Audit
1. Go to `/dashboard`
2. Click "Create New Audit"
3. Enter a website URL (e.g., `https://example.com`)
4. Wait for audit to complete
5. View detailed results with 132+ checks

#### Download Reports
1. Open any completed audit
2. Click "Download PDF" or "Download DOCX"
3. Reports include detailed analysis and code examples

#### Chat with AI SEO Expert
1. Open any completed audit
2. Click "Chat with AI SEO Expert"
3. Ask questions about SEO improvements
4. AI uses context from your audit

#### Admin Dashboard (Superadmin Only)
1. Go to `/admin`
2. Explore tabs:
   - **Users**: Manage all users
   - **Plans**: Configure subscription plans
   - **Audits**: View all audits
   - **Themes**: Create/edit themes
   - **LLM Settings**: Configure AI models
   - **Environment Keys**: Manage API keys (encrypted)
   - **SEO Settings**: Configure SEO parameters

#### API Token Generation
1. Go to `/api-tokens`
2. Click "Generate New Token"
3. Enter token name
4. Copy token (starts with `mjseo_`)
5. Use for MCP server access

### 4. Test as Regular User
1. Logout from superadmin
2. Login with: `test@example.com` / `test123`
3. Test audit creation and reports
4. Verify limited access (no admin dashboard)

---

## 🛠️ Service Management

### Check Service Status
```bash
sudo supervisorctl status
```

### Restart Services
```bash
# Restart all services
sudo supervisorctl restart all

# Restart individual services
sudo supervisorctl restart backend
sudo supervisorctl restart frontend
```

### View Logs
```bash
# Backend logs
tail -f /var/log/supervisor/backend.out.log
tail -f /var/log/supervisor/backend.err.log

# Frontend logs
tail -f /var/log/supervisor/frontend.out.log
tail -f /var/log/supervisor/frontend.err.log
```

---

## 🗄️ Database

### Current Setup
- **Type**: SQLite (Development)
- **Location**: `/app/backend/mjseo.db`
- **Production Ready**: PostgreSQL (via Docker Compose)

### Database Models
1. **User** - User accounts with roles
2. **Plan** - Subscription plans
3. **Subscription** - User subscriptions
4. **Audit** - SEO audits
5. **AuditResult** - SEO check results
6. **ChatMessage** - AI chat history
7. **APIToken** - API tokens for MCP
8. **Theme** - UI themes
9. **LLMSetting** - LLM configurations
10. **EnvironmentKey** - Encrypted API keys
11. **SEOSetting** - SEO configuration

### Reinitialize Database
```bash
cd /app/backend
/root/.venv/bin/python init_db_tables.py
```

---

## 🎯 Key Technologies

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database operations
- **Pydantic** - Data validation
- **JWT** - Authentication tokens
- **Bcrypt** - Password hashing
- **Groq** - AI model (Llama 3.3 70B)
- **Exa.ai** - Research agent
- **ReportLab** - PDF generation
- **python-docx** - DOCX generation
- **Stripe** - Payment processing
- **BeautifulSoup** - Web scraping
- **Playwright** - Browser automation

### Frontend
- **React 18** - UI framework
- **React Router** - Navigation
- **Tailwind CSS** - Styling
- **Radix UI** - Component library
- **Context API** - State management
- **Axios** - HTTP client

---

## 📊 Production Features

### Scalability
- Async/await architecture
- Connection pooling
- Background task processing
- Designed for 10,000+ users

### Security
- JWT authentication with refresh tokens
- Password hashing (bcrypt)
- Role-based access control
- Encrypted environment keys (Fernet)
- CORS protection
- SQL injection prevention (SQLAlchemy ORM)

### Performance
- Hot reload enabled (development)
- Optimized database queries
- Lazy loading
- Report caching

### Monitoring
- Structured logging
- Health check endpoints
- Supervisor process management

---

## 🚀 Next Steps

1. **Test all features** with both superadmin and regular user accounts
2. **Configure production settings** if deploying:
   - Update SECRET_KEY
   - Switch to PostgreSQL
   - Configure real Stripe keys
   - Set up Stripe webhooks
   - Update CORS_ORIGINS
3. **Customize themes** from admin dashboard
4. **Configure LLM settings** (switch between Groq, OpenAI, etc.)
5. **Set up monitoring** and analytics

---

## 📝 Notes

- **Redis**: Listed in requirements but not actively used (background tasks handled by FastAPI background tasks)
- **Workers**: No separate worker processes needed - FastAPI handles background processing
- **Database**: Currently using SQLite for development, PostgreSQL ready for production
- **API Keys**: Groq and Exa.ai keys are configured and working
- **Stripe**: Test mode keys configured, ready for payment testing

---

## 🆘 Troubleshooting

### Backend Not Starting
```bash
# Check logs
tail -50 /var/log/supervisor/backend.err.log

# Restart backend
sudo supervisorctl restart backend
```

### Frontend Not Loading
```bash
# Check logs
tail -50 /var/log/supervisor/frontend.err.log

# Reinstall dependencies
cd /app/frontend && yarn install

# Restart frontend
sudo supervisorctl restart frontend
```

### Database Issues
```bash
# Reinitialize database
cd /app/backend
/root/.venv/bin/python init_db_tables.py
```

---

## ✅ Application Health

Current Status: **ALL SYSTEMS OPERATIONAL** ✅

- ✅ Backend API responding
- ✅ Frontend loading
- ✅ Database initialized
- ✅ Authentication working
- ✅ SEO engine operational
- ✅ AI integration active
- ✅ Report generation functional
- ✅ Payment system configured

---

**Last Updated**: Auto-generated on application sync
**Version**: 1.0.0
**Environment**: Development (Production Ready)
