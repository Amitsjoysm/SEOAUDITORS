@echo off
REM MJ SEO - Frontend Production Build Script for Windows

echo =====================================
echo MJ SEO - Frontend Production Build
echo =====================================
echo.

cd frontend

echo Step 1: Checking Node.js and Yarn...
node --version
if errorlevel 1 (
    echo Error: Node.js is not installed
    pause
    exit /b 1
)

yarn --version
if errorlevel 1 (
    echo Yarn not found. Installing yarn...
    npm install -g yarn
)
echo.

echo Step 2: Setting up production environment...
if exist .env.production (
    copy /Y .env.production .env
    echo Production environment file copied
) else (
    echo Warning: .env.production not found. Using existing .env
)
echo.

echo Step 3: Installing dependencies...
yarn install --frozen-lockfile
if errorlevel 1 (
    echo Failed to install dependencies
    pause
    exit /b 1
)
echo.

echo Step 4: Building production bundle...
echo This may take a few minutes...
yarn build

if errorlevel 1 (
    echo.
    echo =====================================
    echo Build failed!
    echo =====================================
    echo.
    echo Please check the error messages above and fix any issues.
    pause
    exit /b 1
) else (
    echo.
    echo =====================================
    echo Build completed successfully!
    echo =====================================
    echo.
    echo Build output directory: frontend\build
    echo.
    echo Next steps:
    echo 1. Upload the contents of 'build' folder to your web server
    echo 2. Configure nginx to serve the static files
    echo 3. Ensure backend API is running and accessible
    echo.
    echo For detailed deployment instructions, see:
    echo PRODUCTION_DEPLOYMENT_GUIDE.md
    echo.
    pause
)
