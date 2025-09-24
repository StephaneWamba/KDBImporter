# KDB-importer + Paperless-ngx Local Development Setup

This setup provides a complete local development environment for testing the KDB-importer system integrated with Paperless-ngx and Florian's oQo-scripts.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   KDB-Frontend  │    │   KDB-Backend   │    │   oQo-Scripts   │
│   (React:5173)  │◄──►│  (FastAPI:8000) │    │  (Automation)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                │                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Paperless-ngx  │◄───│   PostgreSQL    │
                       │    (Port:8001)  │    │   (Port:5432)   │
                       └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │     Redis       │
                       │   (Port:6379)   │
                       └─────────────────┘
```

## 🚀 Quick Start

### 1. Prerequisites

- Docker and Docker Compose installed
- Git (to clone repositories)

### 2. Environment Setup

1. **Copy the environment template:**

   ```bash
   cp env.template .env
   ```

2. **Edit `.env` and fill in your API keys:**

   ```bash
   # Get your Paperless-ngx API token from the admin interface
   PAPERLESS_TOKEN=your_actual_token_here

   # Get your OpenAI API key from https://platform.openai.com/api-keys
   OPENAI_API_KEY=your_actual_openai_key_here
   ```

### 3. Start the Services

**Start core services (KDB-importer + Paperless-ngx):**

```bash
docker-compose up -d postgres redis paperless kdb-backend kdb-frontend
```

**Start with automation scripts:**

```bash
docker-compose --profile automation up -d
```

### 4. Access the Applications

- **KDB-importer Frontend**: http://localhost:5173
- **KDB-importer Backend API**: http://localhost:8000/docs
- **Paperless-ngx**: http://localhost:8001
- **PostgreSQL**: localhost:5432

## 📋 Services Details

### KDB-importer Backend (Port 8000)

- **Technology**: FastAPI + Python 3.11
- **Features**: arXiv import, search, metadata management
- **API Docs**: http://localhost:8000/docs

### KDB-importer Frontend (Port 5173)

- **Technology**: React + Vite + Tailwind CSS
- **Features**: Modern UI for paper import and management
- **Build**: Production build served via Vite preview

### Paperless-ngx (Port 8001)

- **Technology**: Django-based document management
- **Features**: Document storage, OCR, tagging, custom fields
- **Admin**: Create API tokens in admin interface

### oQo-scripts (Automation)

- **Technology**: Python automation scripts
- **Features**: arXiv scraping, Paperless integration, OpenAI metadata generation
- **Profile**: Only starts with `--profile automation`

### PostgreSQL (Port 5432)

- **Purpose**: Stores article tracking and custom fields sync data
- **Database**: `mydatabase` (oQo-scripts), `paperless` (Paperless-ngx)

### Redis (Port 6379)

- **Purpose**: Caching and task queue for Paperless-ngx

## 🔧 Development Commands

### Build and Start

```bash
# Build all services
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### Individual Service Management

```bash
# Start only KDB-importer
docker-compose up -d kdb-backend kdb-frontend

# Start with automation
docker-compose --profile automation up -d

# Restart a specific service
docker-compose restart kdb-backend
```

### Database Management

```bash
# Access PostgreSQL
docker-compose exec postgres psql -U myuser -d mydatabase

# Backup database
docker-compose exec postgres pg_dump -U myuser mydatabase > backup.sql
```

## 🧪 Testing the Integration

### 1. Test KDB-importer

1. Go to http://localhost:5173
2. Try importing an arXiv paper by ID (e.g., `2301.12345`)
3. Check the API docs at http://localhost:8000/docs

### 2. Test Paperless-ngx

1. Go to http://localhost:8001
2. Create an admin account
3. Generate an API token in admin settings
4. Update `.env` with the token

### 3. Test oQo-scripts Integration

1. Start with automation profile: `docker-compose --profile automation up -d`
2. Check logs: `docker-compose logs oqo-scripts`
3. Verify documents appear in Paperless-ngx

## 📁 File Structure

```
├── docker-compose.yml          # Main orchestration file
├── env.template               # Environment variables template
├── KDB-importer/
│   ├── backend/
│   │   └── Dockerfile        # FastAPI backend container
│   └── frontend/
│       └── Dockerfile        # React frontend container
├── oQo-scripts/
│   ├── Dockerfile            # Automation scripts container
│   └── include/
│       ├── tags.txt          # Available tags for metadata
│       └── categories.txt    # Document categories
└── volumes/                  # Persistent data storage
```

## 🔍 Troubleshooting

### Common Issues

1. **Port conflicts**: Make sure ports 8000, 8001, 5173, 5432, 6379 are available
2. **API token issues**: Verify PAPERLESS_TOKEN is correct in `.env`
3. **OpenAI errors**: Check OPENAI_API_KEY is valid and has credits
4. **Database connection**: Ensure PostgreSQL is running before other services

### Debug Commands

```bash
# Check service status
docker-compose ps

# View specific service logs
docker-compose logs kdb-backend
docker-compose logs paperless

# Access service shell
docker-compose exec kdb-backend bash
docker-compose exec oqo-scripts bash
```

### Reset Everything

```bash
# Stop and remove all containers, networks, and volumes
docker-compose down -v

# Rebuild and start fresh
docker-compose build
docker-compose up -d
```

## 🔄 Next Steps

1. **Test individual components** to ensure they work correctly
2. **Configure Paperless-ngx** with custom fields matching oQo-scripts
3. **Test the integration** between KDB-importer and Paperless-ngx
4. **Develop the bridge** between the two systems
5. **Deploy to production** when ready

## 📚 Additional Resources

- [Paperless-ngx Documentation](https://docs.paperless-ngx.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [arXiv API Documentation](https://arxiv.org/help/api)
- [OpenAI API Documentation](https://platform.openai.com/docs)

