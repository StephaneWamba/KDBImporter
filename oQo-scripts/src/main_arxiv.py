import os
from dotenv import load_dotenv

from automate import automate_arxiv
from config import get_logger
from api import PaperlessClient


arxiv_tags = [
    "quant-ph & cs.CR",
    "math.NT",
    "quant-ph & physics.atom-ph",
    "quant-ph & physics.optics",
    "cs.CR",
    "quant-ph & cond-mat.mes-hall",
    "cs.AR",
    "cs.CR & cs.NI",
    "physics.ed-ph & quant-ph",
    "cs.SE",
    "cs.CR & cs.CC & quant-ph",
    "cs.CR & cs.CY & cs.NI & stat.AP",
    "quant-ph, cs.AI, cs.CR, cs.LG",
    "cs.CR, q-fin.CP",
    "cs.CR, cs.LG, nlin.CD, physics.app-ph, physics.class-ph",
    "QKD, PQC",
]

logger = get_logger("Logger4ScrappingoQo", level="DEBUG")

if __name__ == "__main__":
    automate_arxiv(arxiv_tags)

    # load_dotenv()
    # paperless_url   = os.getenv("PAPERLESS_URL")
    # paperless_token = os.getenv("PAPERLESS_TOKEN")

    # pp    = PaperlessClient(base_url=paperless_url, token=paperless_token)

    # update_keywords(pp)
    # post_consume(555)



