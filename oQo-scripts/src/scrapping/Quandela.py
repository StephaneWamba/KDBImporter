# from bs4 import BeautifulSoup
# from .Scrapper import Scrapper

# from typing import Any
# from ..DocumentData import DocumentData
# from ..api.utils import to_iso_date

# class Quandela(Scrapper):

#     def __init__(self,min_page: int, max_page: int, base_url:str = "https://www.oezratty.net/wordpress/", **kwargs):
#         super().__init__(min_page, max_page, base_url, **kwargs)

#     def build_endpoint_article_listing(self, page: int) -> str:
#         return f"{self.base_url}/archives-complete/?y={page}&t=1&f=1"

#     def list_all_articles(self, url: str) -> dict["title": str, "date":str, "article_url": str]:
#         html = self.get(url)
#         soup = BeautifulSoup(html, "html.parser")
#         postslist_div = soup.find("div", id="postslist")

#         posts_data: list[dict[str, Any]] = []

#         for line in postslist_div.find_all("a", title="Lire le post en entier"):
#             parent_text = line.previous_sibling.strip() if line.previous_sibling else ""
            
#             date = parent_text.split("-")[0].strip()
#             title = line.text.strip()
#             article_url = line['href'].strip()
            
#             posts_data.append({
#                     "title": title,
#                     "date": date,
#                     "article_url":article_url,
#             })

#         return posts_data
    
#     def parse_articles(self, article_data: dict["title": str, "date":str, "article_url": str]) -> DocumentData:
#         article_html = self.get(article_data["article_url"])
#         soup = BeautifulSoup(article_html, "html.parser")

#         author_tag = soup.find("meta", attrs={"name": "author"})
#         authors = author_tag["content"] if author_tag else "Olivier Ezratty"

#         pdf_btn = soup.select_one("a.pdfbutton")
#         pdf_url = pdf_btn["href"] if pdf_btn else None

#         return DocumentData(
#                 title=article_data["title"],
#                 created=to_iso_date(article_data["date"]),
#                 added_via="scraper-opinionlibre",
#                 authors=authors,
#                 pdf_url=pdf_url,
#                 article_url=article_data["article_url"],
#             )
    
#     def is_relevant_by_name(self, title: str) -> bool:
#         return any(n in title for n in ["quantum", "Quantum", "Quantique", "Quantique"])