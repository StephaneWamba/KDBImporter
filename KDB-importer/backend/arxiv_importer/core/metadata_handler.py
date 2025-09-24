# backend/arxiv_importer/core/metadata_handler.py
from typing import Dict, Any, Literal, Optional

# Allowed values for standard fields
VALID_IMPORTANCE = {"low", "medium", "high"}


def normalize_importance(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    value = value.strip().lower()
    return value if value in VALID_IMPORTANCE else None


def process_metadata(user_metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize and validate user-supplied metadata.
    """
    normalized = {}

    # Normalize importance
    importance = user_metadata.get("importance")
    normalized["importance"] = normalize_importance(importance)

    # Optional: additional fields can be added here
    if "tag" in user_metadata:
        normalized["tag"] = str(user_metadata["tag"]).strip()

    # Store raw metadata as fallback or debug info if needed
    normalized["_raw"] = user_metadata

    return normalized
