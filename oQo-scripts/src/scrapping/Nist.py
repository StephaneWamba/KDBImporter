from bs4 import BeautifulSoup
import re

from .Scrapper import Scrapper
from config import get_logger
from core import DocumentData
from api import to_iso_date, europeanize

logger = get_logger("Logger4ScrappingoQo", level="DEBUG")

class Nist(Scrapper):
    categories_data = {
        "news": {       # DONE
            "document_type": "News-Article",
            "params": {
                "sortBy-lg": "NewsDateTime+DESC",
                "ipp-lg" : "all",
                "topics-lg":"27651%7Cpost-quantum+cryptography",
                "topicsMatch-lg": "ANY",
            },
        },
        # "projects": {
        #     "params": {
        #         "sortBy-lg" : "Name+ASC", # TODO set by 
        #         "ipp-lg" : "all",
        #         "topics-lg":"27651%7Cpost-quantum+cryptography",
        #         "topicsMatch-lg": "ANY",
        #     },
        # },
        # "events": {
        #     "params": {
        #         "sortBy-lg": "StartDateTime+DESC",
        #         "ipp-lg" : "all",
        #         "topics-lg":"27651%7Cpost-quantum+cryptography",
        #         "topicsMatch-lg": "ANY",
        #     },
        # },
        "publications": {     # DONE 
            "document_type": "Scientific-Paper",
            "params": {
                # "sortBy-sm": "relevance", No sort to get the newest
                "ipp-sm" : "all",
                "topics-lg":"27651%7Cpost-quantum+cryptography",
                "topicsMatch-sm": "ANY",
                "controlsMatch-sm": "ANY",
                "status-sm": "Final,Draft",
            },
        },
        # "search": {
        #     "params": {
        #         "sortBy": "date+desc",
        #         "ipp" : "100",
        #         "topics-lg":"27651%7Cpost-quantum+cryptography",
        #         "showOnly":"presentations",
        #         "page": 0,
        #     },
        # },
    }
    # PQC news and updates
    # https://csrc.nist.gov/news?sortBy-lg=NewsDateTime+DESC&ipp-lg=all&topics-lg=27651%7Cpost-quantum+cryptography&topicsMatch-lg=ANY
    # PQC Project
    # https://csrc.nist.gov/projects?sortBy-lg=Name+ASC&ipp-lg=all&topics-lg=27651%7Cpost-quantum+cryptography&topicsMatch-lg=ANY
    # PQC Related Events
    # https://csrc.nist.gov/events?sortBy-lg=StartDateTime+DESC&ipp-lg=all&topics-lg=27651%7Cpost-quantum+cryptography&topicsMatch-lg=ANY
    # PQC Related publications
    # https://csrc.nist.gov/publications/search?ipp-sm=all&status-sm=Final,Draft&topics-sm=27651%7Cpost-quantum+cryptography&topicsMatch-sm=ANY&controlsMatch-sm=ANY
    # PQC Presentation
    # https://csrc.nist.gov/search?ipp=100&sortBy=relevance&showOnly=presentations&topicsMatch=ANY&topics=27651%7Cpost-quantum+cryptography&page=2

    def __init__(self,min_page: int, max_page: int, base_url:str = "https://csrc.nist.gov", **kwargs):
        super().__init__(min_page, max_page, base_url, **kwargs)

    def list_all_articles(self, category: str, soup: BeautifulSoup) -> dict["title": str, "date":str, "article_url": str]:
        posts_data: list[dict["title": str, "date":str, "article_url": str]] = []
    
        result_container = soup.find("div", id="results-container")
        if not result_container:
            result_container = soup.find("table", id="publications-results-table")

        if not result_container:
            logger.debug("OULA BELEK c'est NON")

        if category == "news":
            for article in result_container.select("div.news-list-item"):
                title = article.select_one(".news-list-title a")
                date_tag = article.select_one("strong[id^=news-date-]")

                posts_data.append({
                    "title": title.get_text(strip=True),
                    "article_url": self.base_url + title["href"],
                    "date": date_tag.get_text(strip=True),
                })
        elif category == "projects":
            for article in result_container.select("div.project-list-item"):
                title = article.select_one("h5 a")
                # date_tag = article.select_one("strong[id^=news-date-]")

                posts_data.append({
                    "title": title.get_text(strip=True),
                    "article_url": self.base_url + title["href"],
                    "date": None,
                })
        elif category == "events":
            for article in soup.select("div.event-list-item"):
                title = article.select_one("div.event-list-title a")
                date_tag = article.select_one("span[id^=e-starts-]")

                posts_data.append({
                    "title": title.get_text(strip=True),
                    "article_url": self.base_url + title["href"],
                    "date": date_tag.get_text(strip=True),
                })
        elif category == "publications":
            for article in soup.select("tr[id^=result-]"):
                title = article.select_one("a[id^=pub-title-link-]")
                date_tag = article.select_one("td[id^=pub-release-date-]")

                posts_data.append({
                    "title": title.get_text(strip=True),
                    "article_url": self.base_url + title["href"],
                    "date": date_tag.get_text(strip=True),
                })

        return posts_data

    
    def parse_articles(self, category: str, soup: BeautifulSoup, article_data: dict["title": str, "date":str, "article_url": str]) -> DocumentData:
        title = article_data["title"]
        article_url = article_data["article_url"]
        creation_date = article_data["date"]
        
        document_type = self.categories_data[category]["document_type"]
        content = None
        pdf_url_tag = None

        if category == "news":
            content = soup.select_one("#news-content").get_text(separator="\n", strip=True)
            authors_tag = None
        elif category == "publications":
            if not creation_date:
                creation_date = soup.select_one("#pub-release-date").get_text(strip=True)
            
            pdf_url_tag = soup.select_one("#pub-local-download-link")
            authors_tag = soup.select_one("#pub-authors-container")

            if not pdf_url_tag:
                content = soup.select_one("div.publication-panel").get_text(separator="\n", strip=True)
            else:
                pdf_url_tag = pdf_url_tag["href"]
                

            if not authors_tag:
                authors_tag = soup.select_one("#pub-editors-container")

            if authors_tag:
                authors_tag = authors_tag.get_text(strip=True)

        return DocumentData(
                title=title,
                created=to_iso_date(europeanize(article_data["date"])),
                affiliated_organization="NIST",
                source="https://nist.gov/",
                authors=authors_tag,
                download_url=pdf_url_tag,
                content=content,
                article_url=article_url,
                document_type=document_type,
            )
    
    def parse_number_pages(self,category: str, soup: BeautifulSoup) -> list[int]:
        span = soup.find("span", class_="pagination-links")
        if span is None:
            return []
        
        raw_numbers = []
        for tag in span.find_all(["a", "strong"]):
            raw_numbers.append(tag.get_text(strip=True))
            raw_numbers.append(tag.get("aria-label", ""))

        numbers = {
            int(match)
            for txt in raw_numbers
            for match in re.findall(r"\b\d+\b", txt)
        }

        return sorted(numbers)

    def is_relevant_by_name(self, title: str) -> bool:
        return True