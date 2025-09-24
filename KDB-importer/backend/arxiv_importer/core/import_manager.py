# backend/arxiv_importer/core/import_manager.py
from typing import List, Dict, Any
from .query_parser import parse_input, ParsedQuery
from .arxiv_client import fetch_by_id, fetch_by_query
from .metadata_handler import process_metadata

class ImportResult:
    def __init__(self, success: bool, input_value: str, reason: str = "", data: dict = None):
        self.success = success
        self.input_value = input_value
        self.reason = reason
        self.data = data or {}

    def to_dict(self):
        return {
            "input": self.input_value,
            "success": self.success,
            "reason": self.reason,
            "data": self.data
        }


def import_ids_or_urls(inputs: List[str], metadata_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Import arXiv papers by ID or URL.
    Rejects search queries — they should be routed to /search instead.
    """
    results = []

    for i, input_str in enumerate(inputs):
        parsed: ParsedQuery = parse_input(input_str)

        if parsed.type not in ("id", "url"):
            results.append(ImportResult(
                False,
                input_str,
                reason="Search queries must be sent to the /search endpoint."
            ).to_dict())
            continue

        user_metadata = metadata_list[i] if i < len(metadata_list) else {}

        try:
            paper = fetch_by_id(parsed.value)
            if paper is None:
                results.append(ImportResult(False, input_str, reason="Not found").to_dict())
                continue

            enriched_metadata = process_metadata(user_metadata)

            results.append(ImportResult(True, input_str, data={
                "paper": paper.__dict__,
                "metadata": enriched_metadata
            }).to_dict())

        except Exception as e:
            results.append(ImportResult(False, input_str, reason=str(e)).to_dict())

    return results
