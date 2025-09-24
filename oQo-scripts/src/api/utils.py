from __future__ import annotations
from pathlib import Path
from tempfile import NamedTemporaryFile
import requests
import os
from datetime import datetime, date
import re
import unicodedata
from typing import Sequence, Optional
from dateutil import parser as dtparser

from config import get_logger

logger = get_logger("Logger4ScrappingoQo")

INVALID_CHARS = r'[^A-Za-z0-9._-]'
MAX_PREFIX_LEN = 40

def safe_file_prefix(text: str, max_len: int = MAX_PREFIX_LEN) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(INVALID_CHARS, "_", text)

    return text[:max_len] or "tmp"

def create_tmp_import_file(
    *,
    title: str,
    creation_date: str,
    pdf_url: Optional[str] = None,
    content: Optional[str] = None,
) -> Path:
    try:
        dt = datetime.fromisoformat(creation_date)
    except ValueError:
        error_message = "Date is not ISO format. (ex: 2023-10-04T15:00:00)"
        logger.error(f"src/api/utils/created_tmp_doc_from_arxiv: {error_message}")
        raise ValueError(error_message)
    
    # if not pdf_url and content is None:
    #     raise ValueError("Should give either a pdf_url or a content.")

    prefix = safe_file_prefix(title) + "_"

    if pdf_url:
        with requests.get(pdf_url, stream=True, timeout=60) as r:
            r.raise_for_status()
            with NamedTemporaryFile(prefix=prefix, suffix=".pdf", delete=False) as tmp:
                for chunk in r.iter_content(chunk_size=8192):
                    tmp.write(chunk)
                tmp_path = Path(tmp.name)
    else:
        with NamedTemporaryFile(prefix=prefix, suffix=".txt",
                                 delete=False, mode="w", encoding="utf-8") as tmp:
            tmp.write(content or "")
            tmp_path = Path(tmp.name)
    
    mod_time = dt.timestamp()
    os.utime(tmp_path, (mod_time, mod_time))

    return tmp_path

def europeanize(date):
    """
    Converts various US-style date formats to EU format: DD/MM/YYYY
    print(europeanize("5/23/25"))        # 23/05/2025
    print(europeanize("05/23/2025"))     # 23/05/2025
    print(europeanize("June 21, 2018"))  # 21/06/2018
    print(europeanize("Jun 5 99"))       # 05/06/1999
    """
    parsed_date = dtparser.parse(date)
    return parsed_date.strftime('%d/%m/%Y')
    
def to_iso_date(raw: str | date | datetime) -> str:  # → "YYYY-MM-DD"
    """
    Convertit *raw* (date, datetime ou chaîne) en chaîne ISO 8601.

    Exemples
    --------
    >>> to_iso_date("12/05/2025")
    '2025-05-12'
    >>> to_iso_date("May 12 2025")
    '2025-05-12'
    >>> to_iso_date(date(2025, 5, 12))
    '2025-05-12'
    """
    # ── déjà un objet date/datetime ───────────────────────────────────────
    if isinstance(raw, (date, datetime)):
        return raw.isoformat()[:10]

    s: str = raw.strip()

    # ── essai python-dateutil si dispo (gère presque tout) ────────────────
    if dtparser:
        try:
            return dtparser.parse(s, dayfirst=True).date().isoformat()
        except (ValueError, OverflowError):
            pass

    # ── formats courants à essayer (sans dépendances externes) ────────────
    _PATTERNS: Sequence[str] = (
        "%Y-%m-%d",          # 2025-05-12
        "%d/%m/%Y",          # 12/05/2025
        "%d/%m/%y",          # 12/05/25
        "%d-%m-%Y",
        "%d %b %Y",          # 12 May 2025
        "%b %d %Y",          # May 12 2025
        "%d %B %Y",          # 12 May 2025 (long mois)
        "%B %d %Y",          # May 12 2025 (long mois)
        "%d %b, %Y",         # 12 May, 2025
        "%d %B, %Y",
    )
    for fmt in _PATTERNS:
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            continue

    # ── dernier recours : extraire trois nombres avec regex ───────────────
    m = re.search(r"(\\d{1,4}).*(\\d{1,2}).*(\\d{1,4})", s)
    if m:
        a, b, c = (int(g) for g in m.groups())
        # heuristique : l'année est la valeur à 4 chiffres la plus haute
        year = max(x for x in (a, b, c) if x > 31)
        others = [x for x in (a, b, c) if x != year]
        day, month = sorted(others) if others[0] > 12 else others
        try:
            return date(year, month, day).isoformat()
        except ValueError:
            pass

    raise ValueError(f"Impossible de convertir « {raw} » en date ISO.")

def clean_author_string(author_str: str | list[str]) -> str:
    if isinstance(author_str, list):
        # Joindre les éléments par ", " si c’est une liste
        author_str = ', '.join(author_str)

    cleaned = author_str.translate(str.maketrans('', '', "[]'"))
    cleaned = cleaned.replace(',', ';')
    return cleaned.strip()

def get_id_select_custom_field(value_to_match: str, possible_values: list[dict[str,str]]) -> str:
    for value in possible_values:
        if value["value"] == value_to_match:
            return value["id"]
        
    raise ValueError(f"No label named {value_to_match}")
