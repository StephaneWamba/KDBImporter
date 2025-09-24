from .arxiv_client import fetch_by_query
from .metadata_handler import process_metadata
from typing import List, Dict, Any

def search_with_metadata(
    query: str,
    sort_by: str = "relevance",
    max_results: int = 5,
    metadata: Dict[str, Any] = {}
) -> List[Dict[str, Any]]:
    """
    Performs a search query with metadata enrichment.

    Args:
        query (str): The arXiv search query string.
        sort_by (str): Either "relevance" or "submittedDate".
        max_results (int): Max number of papers to fetch.
        metadata (dict): Optional user metadata to enrich results.

    Returns:
        List[Dict[str, Any]]: A list of paper + metadata objects.
    """
    papers = fetch_by_query(query, max_results=max_results, sort_by=sort_by)
    enriched = process_metadata(metadata)

    return [
        {
            "query": query,
            "paper": paper.__dict__,
            "metadata": enriched
        }
        for paper in papers
    ]
