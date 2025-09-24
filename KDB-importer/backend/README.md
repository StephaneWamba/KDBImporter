# arXiv Importer Platform — Backend

This is the backend service for the **arXiv Importer Platform**, a modular FastAPI-based API designed to import and enrich scientific papers from [arXiv.org](https://arxiv.org). The backend supports importing via arXiv IDs, URLs, or search queries, with optional user metadata.

---

## Features

- ✅ Parse inputs: arXiv IDs, URLs, and keyword-based queries
- ✅ Fetch metadata using the `arxiv` Python client
- ✅ Attach optional user metadata (`importance`, `tags`, etc.)
- ✅ Fully typed API with automatic validation (Pydantic)
- ✅ Interactive API docs at `/docs` via Swagger
- ✅ Minimal Docker support for local and portable deployment

---

## Project Structure

```
backend/
├── arxiv_importer/
│   ├── api/               # FastAPI app logic
│   ├── core/              # Core business logic (arXiv, parser, metadata)
│   ├── config.py          # (Optional) Environment config
│   └── constants.py       # Shared constants/enums
├── tests/                 # Pytest unit and integration tests
├── Dockerfile             # Backend container image
├── pyproject.toml         # Project dependencies and metadata
└── README.md
````

---

## Requirements

- Python 3.9+
- [arxiv](https://pypi.org/project/arxiv/)
- FastAPI
- Uvicorn
- (Optional) Docker and Docker Compose

Install dependencies locally:

```bash
cd backend
pip install -e .[dev]
````

---

## Running the Backend

### Local (Development)

```bash
uvicorn arxiv_importer.api.main:app --reload
```

Then open: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### Docker

To build and run the backend container:

```bash
# From project root
docker build -t arxiv-importer-backend ./backend
docker run -p 8000:8000 arxiv-importer-backend
```

Or with Docker Compose:

```bash
docker-compose up --build
```

---

## API Overview

### `POST /api/import`

Import arXiv papers using a list of inputs (URLs, IDs, or a search query).

#### Example Request

```json
{
  "inputs": [
    "https://arxiv.org/abs/2301.12345",
    "2311.99999",
    "deep learning climate change"
  ],
  "metadata": [
    { "importance": "high", "tag": "NLP" },
    { "importance": "low" },
    { "importance": "medium", "tag": "ML" }
  ]
}
```

#### Response Format

```json
{
  "results": [
    {
      "input": "https://arxiv.org/abs/2301.12345",
      "success": true,
      "reason": null,
      "data": {
        "paper": { ... },
        "metadata": {
          "importance": "high",
          "tag": "NLP",
          "_raw": { "importance": "high", "tag": "NLP" }
        }
      }
    },
    ...
  ]
}
```

---

## Testing

To run all unit tests:

```bash
pytest
```

You can add fixtures and mocks to test arXiv queries without calling the real API.

---

## [Maybe] Roadmap (Post-MVP)

* [ ] Add persistence (database, cache)
* [ ] Support async background processing
* [ ] Rate limiting / deduplication
* [ ] LLM summarization / enrichment
* [ ] User-level tagging and saved imports

---

## License

MIT — feel free to use, fork, or adapt this project.
