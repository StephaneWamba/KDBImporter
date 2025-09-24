from __future__ import annotations
import os
import psycopg2
import json
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Any
from dotenv import load_dotenv
from .utils import _clean_title, running_in_docker
from config import get_logger

logger = get_logger("Logger4ScrappingoQo", level="DEBUG")

# Load .env
load_dotenv(Path(__file__).parents[2] / ".env")

if running_in_docker():
    PG_HOST = "postgres"
else:
    PG_HOST = os.getenv("PG_HOST", "localhost")

PG_PORT = os.getenv("PG_PORT", "5432")

# Connexion PostgreSQL
PG_USER = os.getenv("PG_USER", "myuser")
PG_PASSWORD = os.getenv("PG_PASSWORD", "mypassword")
PG_DB = os.getenv("PG_DB", "mydatabase")

@contextmanager
def _get_db() -> Generator[psycopg2.extensions.connection, None, None]:
    conn = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        user=PG_USER,
        password=PG_PASSWORD,
        dbname=PG_DB,
    )
    cur = conn.cursor()

    # Créer la table si elle n'existe pas
    cur.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            title TEXT PRIMARY KEY,
            date_iso TEXT NOT NULL,
            source TEXT NOT NULL,
            custom_fields_json TEXT,
            custom_fields_synced INTEGER NOT NULL DEFAULT 0
        )
    """)
    conn.commit()

    try:
        yield cur
    finally:
        conn.commit()
        cur.close()
        conn.close()

def already_seen(title: str) -> bool:
    title = _clean_title(title)
    with _get_db() as cur:
        cur.execute(
            "SELECT 1 FROM articles WHERE title = %s LIMIT 1", (title,)
        )
        return cur.fetchone() is not None

def remember(title: str, date_iso: str, source: str, custom_fields: dict[str, Any] | None = None) -> None:
    title = _clean_title(title)
    with _get_db() as cur:
        cur.execute(
            """
            INSERT INTO articles (title, date_iso, source, custom_fields_json, custom_fields_synced)
            VALUES (%s, %s, %s, %s, 0)
            ON CONFLICT (title) DO NOTHING
            """,
            (
                title,
                date_iso,
                source,
                json.dumps(custom_fields, ensure_ascii=False) if custom_fields else None
            )
        )

def mark_synced(title: str) -> None:
    title = _clean_title(title)
    with _get_db() as cur:
        cur.execute(
            "UPDATE articles SET custom_fields_synced = 1 WHERE title = %s",
            (title,)
        )

def load_custom_fields(title: str) -> dict[str, Any] | None:
    title = _clean_title(title)
    with _get_db() as cur:
        cur.execute(
            "SELECT custom_fields_json FROM articles WHERE title = %s",
            (title,)
        )
        row = cur.fetchone()
        if row and row[0]:
            return json.loads(row[0])
    return None

def fetch_article_row(title: str) -> dict[str, Any] | None:
    title = _clean_title(title)
    with _get_db() as cur:
        cur.execute(
            "SELECT title, date_iso, source, custom_fields_json, custom_fields_synced FROM articles WHERE title = %s LIMIT 1",
            (title,)
        )
        row = cur.fetchone()
        if row:
            return {
                "title": row[0],
                "date_iso": row[1],
                "source": row[2],
                "custom_fields_json": json.loads(row[3]) if row[3] else None,
                # "custom_fields_json": row[3],
                "custom_fields_synced": row[4]
            }
    return None
