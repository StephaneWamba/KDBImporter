@echo off
REM KDB-importer + Paperless-ngx Startup Script for Windows
REM This script helps you get started quickly with the local development environment

echo 🚀 Starting KDB-importer + Paperless-ngx Development Environment
echo ================================================================

REM Check if .env exists
if not exist ".env" (
    echo ⚠️  .env file not found!
    echo 📋 Copying env.template to .env...
    copy env.template .env
    echo ✅ Please edit .env and add your API keys:
    echo    - PAPERLESS_TOKEN (get from Paperless-ngx admin)
    echo    - OPENAI_API_KEY (get from OpenAI platform)
    echo.
    echo Press Enter when ready to continue...
    pause
)

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker and try again.
    pause
    exit /b 1
)

echo 🐳 Building Docker images...
docker-compose build

echo 🚀 Starting core services...
docker-compose up -d postgres redis paperless kdb-backend kdb-frontend

echo ⏳ Waiting for services to be ready...
timeout /t 10 /nobreak >nul

echo ✅ Services started successfully!
echo.
echo 🌐 Access your applications:
echo    • KDB-importer Frontend: http://localhost:5173
echo    • KDB-importer Backend:  http://localhost:8000/docs
echo    • Paperless-ngx:          http://localhost:8001
echo.
echo 📋 Next steps:
echo    1. Go to http://localhost:8001 and create a Paperless-ngx admin account
echo    2. Generate an API token in the admin interface
echo    3. Update PAPERLESS_TOKEN in your .env file
echo    4. Test the KDB-importer at http://localhost:5173
echo.
echo 🔧 Useful commands:
echo    • View logs:           docker-compose logs -f
echo    • Start automation:     docker-compose --profile automation up -d
echo    • Stop services:        docker-compose down
echo    • Reset everything:     docker-compose down -v
echo.
echo Happy coding! 🎉
pause

