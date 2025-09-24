#!/bin/bash

# KDB-importer + Paperless-ngx Startup Script
# This script helps you get started quickly with the local development environment

set -e

echo "🚀 Starting KDB-importer + Paperless-ngx Development Environment"
echo "================================================================"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "📋 Copying env.template to .env..."
    cp env.template .env
    echo "✅ Please edit .env and add your API keys:"
    echo "   - PAPERLESS_TOKEN (get from Paperless-ngx admin)"
    echo "   - OPENAI_API_KEY (get from OpenAI platform)"
    echo ""
    echo "Press Enter when ready to continue..."
    read
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "🐳 Building Docker images..."
docker-compose build

echo "🚀 Starting core services..."
docker-compose up -d postgres redis paperless kdb-backend kdb-frontend

echo "⏳ Waiting for services to be ready..."
sleep 10

echo "✅ Services started successfully!"
echo ""
echo "🌐 Access your applications:"
echo "   • KDB-importer Frontend: http://localhost:5173"
echo "   • KDB-importer Backend:  http://localhost:8000/docs"
echo "   • Paperless-ngx:          http://localhost:8001"
echo ""
echo "📋 Next steps:"
echo "   1. Go to http://localhost:8001 and create a Paperless-ngx admin account"
echo "   2. Generate an API token in the admin interface"
echo "   3. Update PAPERLESS_TOKEN in your .env file"
echo "   4. Test the KDB-importer at http://localhost:5173"
echo ""
echo "🔧 Useful commands:"
echo "   • View logs:           docker-compose logs -f"
echo "   • Start automation:     docker-compose --profile automation up -d"
echo "   • Stop services:        docker-compose down"
echo "   • Reset everything:     docker-compose down -v"
echo ""
echo "Happy coding! 🎉"

