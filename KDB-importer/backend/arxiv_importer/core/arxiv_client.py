# backend/arxiv_importer/core/arxiv_client.py
import arxiv
import requests
from typing import List, Optional


class ArxivPaper:
    def __init__(self, entry: arxiv.Result):
        self.id = entry.get_short_id()
        self.title = entry.title
        self.authors = [a.name for a in entry.authors]
        self.summary = entry.summary
        self.pdf_url = entry.pdf_url
        self.published = entry.published.isoformat()
        self.updated = entry.updated.isoformat()
    
    def __repr__(self) -> str:
        return f"{self.id} — {self.title.strip()} by {', '.join(self.authors)}"


def is_valid_arxiv_id(arxiv_id: str) -> bool:
    """
    Check if the arXiv ID exists by sending a HEAD request.
    """
    url = f"https://arxiv.org/abs/{arxiv_id}"
    try:
        response = requests.head(url, timeout=3)
        return response.status_code == 200
    except requests.RequestException:
        return False

def fetch_by_id(arxiv_id: str) -> Optional[ArxivPaper]:
    try:
        search = arxiv.Search(id_list=[arxiv_id])
        results = list(search.results())
        if not results:
            return None
        return ArxivPaper(results[0])
    except Exception as e:
        print(f"Error fetching ID {arxiv_id}: {e}")
        return None


def fetch_by_query(
    query: str,
    max_results: int = 5,
    sort_by: str = "relevance"  # "relevance" or "submittedDate"
) -> List[ArxivPaper]:
    try:
        sort_criterion = arxiv.SortCriterion.Relevance
        if sort_by == "submittedDate":
            sort_criterion = arxiv.SortCriterion.SubmittedDate

        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=sort_criterion
        )
        return [ArxivPaper(result) for result in search.results()]

    except Exception as e:
        print(f"Error fetching query '{query}': {e}")
        return []
