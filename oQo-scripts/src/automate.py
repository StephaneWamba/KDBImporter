from api import PaperlessClient, ArxivClient

import logging
import os
from dotenv import load_dotenv

logger = logging.getLogger("Logger4ScrappingoQo")
MAX_RESULTS = 10

def automate_arxiv(tags: list[str]) -> None:
    logger.debug("Start automate_arxiv")

    sent_titles: set[str] = set()

    load_dotenv()
    paperless_url   = os.getenv("PAPERLESS_URL")
    paperless_token = os.getenv("PAPERLESS_TOKEN")

    arxiv = ArxivClient(idle_time=1)
    pp    = PaperlessClient(base_url=paperless_url, token=paperless_token)

    total_imported = 0

    try:
        for tag in tags:
            start = 0
            while True:
                response = arxiv.search(tag, max_results=MAX_RESULTS, start=start)
                if not response:
                    break

                fresh = [doc for doc in response if doc.title not in sent_titles]
                if fresh:
                    pp.import_entries(fresh)
                    sent_titles.update(doc.title for doc in fresh)
                    total_imported += len(fresh)

                start += MAX_RESULTS

    except KeyboardInterrupt:
        logger.info("Stopped automate_arxiv")

    logger.info("Imported %d new documents from arXiv", total_imported)
    logger.info("Unique titles in memory: %d", len(sent_titles))

