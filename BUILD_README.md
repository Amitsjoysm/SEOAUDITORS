# MJ SEO - Quick Production Build

## Prerequisites

- Node.js 18+ installed
- Yarn installed
- Python 3.10+ installed

## Quick Start

### For Linux/Mac:

```bash
# Make scripts executable
chmod +x build-production.sh
chmod +x setup-backend-production.sh

# Build frontend
./build-production.sh

# Setup backend
./setup-backend-production.sh
```

### For Windows:

```cmd
# Build frontend
build-production.bat
```

## What Gets Built

### Frontend Build
- Creates optimized production bundle in `frontend/build/`
- Includes all static assets (JS, CSS, images)
- Minified and optimized for performance
- Environment variables baked in from `.env.production`

### Backend Setup
- Creates Python virtual environment
- Installs all dependencies from `requirements.txt`
- Copies production environment file
- Initializes database (optional)

## After Building

1. **Frontend**: Upload `frontend/build/*` to your web server root
2. **Backend**: 
   - Upload entire `backend/` folder to server
   - Configure systemd service or use uvicorn directly
   - See `PRODUCTION_DEPLOYMENT_GUIDE.md` for details

## Environment Files

### Frontend (.env.production)
```env
REACT_APP_BACKEND_URL=https://marketautomailer.mj.publicvm.com/api
REACT_APP_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

### Backend (.env.production)
```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/mjseo_db
CORS_ORIGINS=http://domain.com,https://domain.com
SECRET_KEY=your-secret-key
```

## Troubleshooting

### Build Errors
- Clear node_modules: `rm -rf node_modules && yarn install`
- Clear yarn cache: `yarn cache clean`
- Check Node.js version: `node --version` (should be 18+)

### Backend Setup Errors
- Check Python version: `python3 --version` (should be 3.10+)
- Verify PostgreSQL is running: `systemctl status postgresql`
- Test database connection: `psql -h localhost -U user -d database`

## Production Deployment

For complete deployment instructions including:
- Nginx configuration
- SSL setup
- Database configuration
- Systemd services
- Common issues and solutions

See: **PRODUCTION_DEPLOYMENT_GUIDE.md**
