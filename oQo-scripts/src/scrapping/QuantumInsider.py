# src/scrapping/quantum_insider.py
from __future__ import annotations

from typing import Any, Optional
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

from .Scrapper import Scrapper
from core import DocumentData
from config import get_logger
from api import to_iso_date

logger = get_logger("Logger4ScrappingoQo")

class QuantumInsider(Scrapper):
    categories_data = {
        "category/daily": {
            "/page": 0,
            "params": {}
        }
    }

    def __init__(self, min_page: int, max_page: int, base_url:str = "https://thequantuminsider.com/", **kwargs):
        super().__init__(min_page, max_page, base_url, **kwargs)

    def __init__(self,min_page: int, max_page: int, base_url:str = "https://thequantuminsider.com", **kwargs):
        super().__init__(min_page, max_page, base_url, **kwargs)

    def list_all_articles(self, category:str, soup: BeautifulSoup) -> dict["title": str, "date":str, "article_url": str]:
        postslist_div = soup.find("div", class_="elementor-element elementor-element-282c7c06 e-flex e-con-boxed e-con e-child")
        posts_data: list[dict[str, Any]] = []

        for line in postslist_div.find_all("article", recursive=True):
            article_tag = line.select_one("h6.elementor-post__title a")
            title = article_tag.get_text(strip=True)
            article_url = article_tag["href"]
            date = line.select_one(".elementor-post-date").get_text(strip=True)

            posts_data.append({"title": title, "date": date, "article_url": article_url})

        return posts_data
    
    def parse_articles(self, category: str, soup: BeautifulSoup, article_data: dict["title": str, "date":str, "article_url": str]) -> DocumentData:

        authors = soup.find("span", class_="elementor-icon-list-text elementor-post-info__item elementor-post-info__item--type-author")
        content = soup.find("div", class_="elementor-element elementor-element-6fe52692 link-color margin-bottom elementor-widget elementor-widget-theme-post-content")
        # date = soup.find("span", class_="elementor-icon-list-text elementor-post-info__item elementor-post-info__item--type-date").text.strip()

        doc = DocumentData(
                title=article_data["title"],
                created=to_iso_date(article_data["date"]),
                added_via="scrapper-quantuminsider",
                authors=authors.text.strip(),
                article_url=article_data["article_url"],
                content=content.text.strip(),
                document_type="News-Article"
            )
        
        return doc
    
    def parse_number_pages(self, category:str, soup: BeautifulSoup) -> list[int]:
        number_pages: list[int] = []
        
        for item in soup.select("nav.elementor-pagination .page-numbers"):
            match = re.search(r"\d+", item.get_text(strip=True))
            if match:
                number_pages.append(int(match.group()))
        return number_pages
    
    def is_relevant_by_name(self, title: str) -> bool:
        return True
