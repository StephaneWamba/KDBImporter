from bs4 import BeautifulSoup
from .Scrapper import Scrapper

from typing import Any
from core import DocumentData
from api import to_iso_date

class AliceAndBob(Scrapper):
    categories: list[str] = ["blog", "publication", "newrooms", "roadmap/#whitepaper-think-inside-the-box"]

    def __init__(self,min_page: int, max_page: int, base_url:str = "https://alice-bob.com", **kwargs):
        super().__init__(min_page, max_page, base_url, **kwargs)

    def build_endpoint_article_listing(self, page: int) -> str:
        category = "blog"
        # https://alice-bob.com/blog/page/2/#blog-filter
        return f"{self.base_url}/{category}/page/{page}/#blog-filter"

    def list_all_articles(self, url: str) -> dict["title": str, "date":str, "article_url": str]:
        html = self.get(url)
        soup = BeautifulSoup(html, "html.parser")
        # postslist_div = soup.find("ul", class_="c-archive__list")
        postslist_div = soup.select("ul.c-archive__list")

        posts_data: list[dict[str, Any]] = []

        posts = []
        for li in postslist_div.find_all("li", class_="c-archive__article"):
            # 1) le lien (il enveloppe toute la carte)
            a = li.select_one("a[href]")
            if not a:
                continue                                   # carte malformée : on saute
            url = a["href"]

            # 2) le titre (balise <h4> dans la carte)
            h = a.select_one(".c-post-card__title, h4")    # deux variantes possibles
            title = h.get_text(strip=True) if h else "(sans titre)"

            posts.append({"title": title, "url": url})

        # posts est une liste de dicts prêts à l'emploi
        for p in posts:
            print(f"- {p['title']} → {p['url']}")

        # for line in postslist_div.find_all("a", title="Lire le post en entier"):
        #     parent_text = line.previous_sibling.strip() if line.previous_sibling else ""
            
        #     date = parent_text.split("-")[0].strip()
        #     title = line.text.strip()
        #     article_url = line['href'].strip()
            
        #     posts_data.append({
        #             "title": title,
        #             "date": date,
        #             "article_url":article_url,
        #     })

        return posts_data
    
    def parse_articles(self, article_data: dict["title": str, "date":str, "article_url": str]) -> DocumentData:
        article_html = self.get(article_data["article_url"])
        soup = BeautifulSoup(article_html, "html.parser")

        author_tag = soup.find("meta", attrs={"name": "author"})
        authors = author_tag["content"] if author_tag else "Olivier Ezratty"

        pdf_btn = soup.select_one("a.pdfbutton")
        pdf_url = pdf_btn["href"] if pdf_btn else None

        return DocumentData(
                title=article_data["title"],
                created=to_iso_date(article_data["date"]),
                added_via="scraper-opinionlibre",
                authors=authors,
                pdf_url=pdf_url,
                article_url=article_data["article_url"],
            )
    
    def is_relevant_by_name(self, title: str) -> bool:
        return any(n in title for n in ["quantum", "Quantum", "Quantique", "Quantique"])