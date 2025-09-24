import feedparser

from .APIClient import APIClient
from core import DocumentData

class ArxivClient(APIClient):
    base_url = "https://export.arxiv.org"

    def __init__(self, idle_time=3, **kwargs):
        super().__init__(idle_time=idle_time, parse_json=False, **kwargs)

    def search(
        self,
        query: str,
        *,
        max_results: int = 50,
        start: int = 0,
        sort_by: str = "submittedDate",
        sort_order: str = "descending",
    ) -> list[DocumentData]:
        params = {
            "search_query": query,
            "start": start,
            "max_results": max_results,
            "sortBy": sort_by,
            "sortOrder": sort_order,
        }

        feed_xml = self.get("/api/query", params=params)
        parsed = feedparser.parse(feed_xml)
        parsed_response: DocumentData = []

        for entry in parsed.entries:
            parsed_response.append(DocumentData(
                title=entry.title.strip(),
                created=entry.published[:10],
                authors=[author.name for author in entry.authors],
                download_url=next((l.href for l in entry.links if l.type == "application/pdf"), None),
                import_query=query,
                document_type="Scientific-Paper",
                source="https://arxiv.org/"
            ))
            
        return parsed_response
    