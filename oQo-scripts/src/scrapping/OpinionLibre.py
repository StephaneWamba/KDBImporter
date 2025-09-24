from bs4 import BeautifulSoup

from typing import Any
from .Scrapper import Scrapper
from core import DocumentData
from api import to_iso_date

class OpinionLibre(Scrapper):
    categories_data = {
        "archives-complete": {
            "params": {
                "y": 0,
                "t": "1",
                "f": "1",
            }
        }
    }

    def __init__(self,min_page: int, max_page: int, base_url:str = "https://www.oezratty.net/wordpress", **kwargs):
        super().__init__(min_page, max_page, base_url, **kwargs)

    def list_all_articles(self, category:str, soup: BeautifulSoup) -> dict["title": str, "date":str, "article_url": str]:
        postslist_div = soup.find("div", id="postslist")

        posts_data: list[dict[str, Any]] = []

        for line in postslist_div.find_all("a", title="Lire le post en entier"):
            parent_text = line.previous_sibling.strip() if line.previous_sibling else ""
            
            date = parent_text.split("-")[0].strip()
            title = line.text.strip()
            article_url = line['href'].strip()
            
            posts_data.append({
                    "title": title,
                    "date": date,
                    "article_url":article_url,
            })

        return posts_data
    
    def parse_articles(self, category: str, soup: BeautifulSoup, article_data: dict["title": str, "date":str, "article_url": str]) -> DocumentData:
        author_tag = soup.find("meta", attrs={"name": "author"})
        authors = author_tag["content"] if author_tag else "Olivier Ezratty"
        pdf_btn = soup.select_one("a.pdfbutton")
        pdf_url = pdf_btn["href"] if pdf_btn else None

        return DocumentData(
                title=article_data["title"],
                created=to_iso_date(article_data["date"]),
                authors=authors,
                download_url=pdf_url,
                source="https://oezratty.net/wordpress",
                article_url=article_data["article_url"],
                document_type="News-Article"
            )
    
    def parse_number_pages(self, category:str, soup: BeautifulSoup) -> list[int]:
        # TODO include in result page like 1,2,3,4,5... as to be years...
        number_pages: list[int] = []
        
        for item in soup.select("fieldset input[type=Radio][id]"):
            id_value = item["id"]
            if id_value.isdigit() and id_value != "0":
                number_pages.append(int(id_value))

        # return number_pages
        return ["2025"]

    
    def is_relevant_by_name(self, title: str) -> bool:
        return any(n in title for n in ["quantum", "Quantum", "quantique", "Quantique"])