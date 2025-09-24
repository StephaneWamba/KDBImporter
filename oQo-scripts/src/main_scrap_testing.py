from config import get_logger
from api import PaperlessClient
from dotenv import load_dotenv
import os

from scrapping import QuantumInsider, OpinionLibre, Nist

logger = get_logger("Logger4ScrappingoQo", level="DEBUG")

if __name__ == "__main__":
    load_dotenv()
    paperless_url = os.getenv("PAPERLESS_URL")
    paperless_token = os.getenv("PAPERLESS_TOKEN")

    pp = PaperlessClient(base_url=paperless_url, token=paperless_token)

    # print(pp.get_tags())
    # print(pp.get_custom_fields)

    # ==== Opinion Libre ====
    op_libre = OpinionLibre(2020, 2021)
    nist = Nist(0, 0)
    QI = QuantumInsider(1,1)


    # === Quantum Insider ===

    # op_libre.test_url_contruct()
    # nist.test_url_contruct()
    # QI.test_url_contruct()
    
    # c = nist.scrap_website()

    # c_opLibre = op_libre.scrap_website()
    # c_nist = nist.scrap_website()
    c_qi = QI.scrap_website()

    # pp.import_entries(c_opLibre)
    pp.import_entries(c_qi)
    # pp.import_entries(c_nist)


    # c = QI.scrap_website()
    # list_articles_html = QI.get_html("https://thequantuminsider.com/category/daily/")
    # soup_articles = BeautifulSoup(list_articles_html, "html.parser")
    # b = QI.list_all_articles(soup_articles)
    # for a in c:
    #     logger.debug(f"main articles: \n{a}")

    # pp.import_entries(c)

    # html_article = QI.get_html(b[0]["article_url"])
    # soup_article = BeautifulSoup(html_article, "html.parser")
    # c = QI.parse_articles(soup_article, b[0])


    # for a in c:
    #     logger.debug(a)

    # pp.import_entries(c)


    # aetl = AliceAndBob(2,2)

    # aetl.list_all_articles(aetl.build_endpoint_article_listing(2))


    # logger.debug(f"Founded {len(articles)} relevent articles")
    # for art in articles:
    #     logger.debug(f"main_scrap_testing: \n {art}\n")
