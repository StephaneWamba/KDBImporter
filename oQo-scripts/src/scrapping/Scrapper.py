from abc import abstractmethod
from bs4 import BeautifulSoup
from typing import Optional
from playwright.sync_api import sync_playwright


from config import get_logger
from core import DocumentData
from api import Sleeper

logger = get_logger("Logger4ScrappingoQo")

class Scrapper(Sleeper):
    categories_data: dict[str, any]

    def __init__(self, min_page: int, max_page:int, base_url:str, **kwargs):
        super().__init__(
            idle_time=5,
            random_idle_time=True
        )
        
        self.min_page = min_page
        self.max_page = max_page
        self.base_url = base_url

    def get_html(self, url: str, timeout: float = 20_000)-> str:
        self.time_action()

        logger.info(f"Scrapper: Opening {url}")

        with sync_playwright() as playwright:
            # browser = p.chromium.launch(headless=False)             # ou False pour voir
            # browser = p.firefox.launch(headless=False)             # ou False pour voir
            browser = playwright.webkit.launch(headless=True)
            context = browser.new_context()                        # cookies isolés
            page = context.new_page()
            page.goto(url, timeout=timeout)
            html = page.content()
            browser.close()
    
            return html
        
    def add_params_to_url(self, params: dict[str, str | int], page: int)-> str:
        params_url = ""
        separator = "?"

        for key, value in params.items():
            # logger.debug(f"\nkey\n{key}\nvalue\n{value}\npage={page}")
            param_to_add = f"{separator}{key}="

            if isinstance(value, int):
                if page == -1:
                    continue
                params_url += param_to_add + f"{page}"
            else:
                params_url += param_to_add + f"{value}"
            
            separator = "&"

        return params_url

    def build_endpoint_article_listing(self, category:str,  page: Optional[int]) -> str:
        url = self.base_url + f"/{category}"

        # logger.debug(f"{category}")
        params = self.categories_data[category]["params"]
        
        if "/page" in self.categories_data[category]:
            if isinstance(self.categories_data[category]["/page"], int) and page != -1:
                url += f"/page/{page}"

        # logger.debug(f"{params}")

        url += self.add_params_to_url(params, page)            
        
        return url

    @abstractmethod
    def list_all_articles(self, category: str, soup: BeautifulSoup) -> dict["title": str, "date":str, "article_url": str]:
        pass
    
    @abstractmethod
    def parse_articles(self, category: str, soup: BeautifulSoup, article_data: dict["title": str, "date":str, "article_url": str]) -> DocumentData:
        pass

    @abstractmethod
    def is_relevant_by_name(self, title: str) -> bool:
        pass

    @abstractmethod
    def parse_number_pages(self, category: str, soup: BeautifulSoup) -> list[int]:
        pass

    def scrap_website(self) -> list[DocumentData]:
        documents: list[DocumentData] = []


        for category, data in self.categories_data.items():
            basic_url = self.get_html(self.build_endpoint_article_listing(category, page = -1))
            number_pages: list[int] = self.parse_number_pages(category, BeautifulSoup(basic_url, "html.parser"))

            if len(number_pages) == 0:
                number_pages = [-1]

            for page in number_pages:
                articles_url = self.build_endpoint_article_listing(category, page)
                list_articles_html = self.get_html(articles_url)
                soup_articles = BeautifulSoup(list_articles_html, "html.parser")

                articles_infos = self.list_all_articles(category, soup_articles)

                for article_data in articles_infos:
                    if not self.is_relevant_by_name(article_data["title"]):
                        continue

                    article_html = self.get_html(article_data["article_url"])
                    soup_article = BeautifulSoup(article_html, "html.parser")
                    document = self.parse_articles(category, soup_article, article_data)

                    documents.append(document)

        return documents
    
    def test_url_contruct(self):
        for category, data in self.categories_data.items():
            basic_url = self.build_endpoint_article_listing(category, -1)
            soup = BeautifulSoup(self.get_html(basic_url), "html.parser")
            pages = self.parse_number_pages(category, soup)

            logger.debug(f"URL:\n{basic_url}\nnumber pages:\n{pages}")

            test = self.list_all_articles(category, soup)
            for ar in test:
                print(f"\n{ar}\n")

