from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router as api_router

app = FastAPI(
    title="arXiv Importer Platform",
    description="Import and manage scientific papers via arXiv.",
    version="0.1.0"
)

# (Optional) CORS if frontend is on different domain/port during dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")
