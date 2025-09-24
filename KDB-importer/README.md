# arXiv Importer Platform

A modular web application for importing and managing scientific papers from [arXiv.org](https://arxiv.org) via URLs, IDs, or search queries. Designed for researchers, engineers, and knowledge workers who want a clean way to enrich, store, and work with paper metadata.

Built with:
- **FastAPI** for the backend (Python)
- **React** + **Tailwind CSS** for the frontend (JavaScript)
- Dockerized for easy local development and deployment

---

## Features

- ✅ Import papers via arXiv URLs, IDs, or search queries
- ✅ Enrich each entry with metadata (importance level, tags, etc.)
- ✅ Batch and bulk import support
- ✅ Dashboard (coming soon)
- ✅ Assistant view (planned for future NLP tasks)

---

## Project Structure

```

arxiv-importer-platform/
│
├── backend/                    # FastAPI backend
│   ├── arxiv\_importer/         # Python package
│   │   ├── api/                # Routes, schemas, FastAPI logic
│   │   ├── core/               # Core logic (arxiv client, parsing, import)
│   │   ├── config.py           # Pydantic settings
│   │   └── constants.py        # Shared enums or values
│   ├── tests/                  # Pytest test suite
│   ├── Dockerfile              # Backend container
│   └── pyproject.toml          # Python package config
│
├── frontend/                   # React + Tailwind frontend
│   ├── src/                    # App logic
│   ├── Dockerfile              # (optional) Frontend container
│   └── package.json
│
├── docker-compose.yml          # Unified dev setup (optional)
└── README.md

````

---

## Getting Started

### Prerequisites

- [Python 3.9+](https://www.python.org/)
- [Node.js v18+](https://nodejs.org/)
- [Docker](https://www.docker.com/) *(optional for containerized run)*

---

### Backend Setup (FastAPI)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .   # Uses pyproject.toml
uvicorn arxiv_importer.api.main:app --reload
````

Access the backend at: [http://localhost:8000](http://localhost:8000)

View API docs at: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### Frontend Setup (React + Vite + Tailwind)

```bash
cd frontend
npm install
npm run dev
```

Access the frontend at: [http://localhost:5173](http://localhost:5173)

---

### Docker (Optional Unified Setup)

```bash
docker-compose up --build
```

---

## Example API Usage

#### POST `/api/import`

```json
{
  "inputs": [
    "https://arxiv.org/abs/2301.12345",
    "2304.56789",
    "transformer-based vision model"
  ],
  "metadata": [
    { "importance": "high", "tag": "vision" },
    { "importance": "low" },
    { "importance": "medium", "tag": "NLP" }
  ]
}
```

Returns a list of results with success flags and fetched paper metadata.

---

## Testing

```bash
cd backend
pytest
```

---

## Roadmap

* [x] Import via URL, ID, or query
* [x] Bulk support + metadata tagging
* [x] Swagger-based API docs
* [x] React UI with sidebar navigation
* [ ] KPI Dashboard (progress tracking)
* [ ] Paperless Assistant (LLM/NLP interface)
* [ ] Auth system & DB integration (optional)


---

## License

MIT License — see `LICENSE` for details.
