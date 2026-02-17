# SEOAUDITORS Production Build Fix

## Problem Statement
Fix connection errors when frontend tries to connect to backend on `localhost:9599`. The frontend was showing:
- `Failed to fetch theme: AxiosError: Network Error`
- `POST http://localhost:9599/api/auth/login net::ERR_CONNECTION_REFUSED`

## Solution Implemented
1. Updated `/app/frontend/.env.production` to set `REACT_APP_BACKEND_URL=http://localhost:9599`
2. Created production build with explicit environment variable to ensure correct API URL

## Technical Details
- Frontend uses axios with baseURL from `REACT_APP_BACKEND_URL + '/api'`
- Backend API routes are prefixed with `/api` (via FastAPI APIRouter)
- Production build connects to `http://localhost:9599/api`

## Files Modified
- `/app/frontend/.env.production` - Changed REACT_APP_BACKEND_URL from `/api` to `http://localhost:9599`

## Build Output
- Location: `/app/frontend/build/`
- Zip: `/app/frontend/build.zip`
- Size: ~3.3MB (810KB zipped)

## Deployment Instructions
1. Upload the `build/` folder contents to your web server root on aaPanel
2. Ensure backend is running on `localhost:9599`
3. Configure web server (nginx/apache) to serve static files and handle SPA routing

## Date
February 17, 2026
