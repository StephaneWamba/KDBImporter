# backend/arxiv_importer/core/query_parser.py
import re
from typing import Literal, NamedTuple, List


class ParsedQuery(NamedTuple):
    type: Literal["id", "url", "search"]
    value: str


ARXIV_ID_PATTERN = re.compile(r"^\d{4}\.\d{4,5}(v\d+)?$")
ARXIV_URL_PATTERN = re.compile(
    r"^(?:https?://)?(?:www\.)?arxiv\.org/(abs|pdf)/(\d{4}\.\d{4,5}(v\d+)?)(?:\.pdf)?$"
)

def parse_input(input_str: str) -> ParsedQuery:
    input_str = input_str.strip()

    # Direct arXiv ID
    if ARXIV_ID_PATTERN.match(input_str):
        return ParsedQuery("id", input_str)

    # arXiv URL
    url_match = ARXIV_URL_PATTERN.match(input_str)
    if url_match:
        arxiv_id = url_match.group(2)
        return ParsedQuery("url", arxiv_id)

    # Fallback to search
    return ParsedQuery("search", input_str)


def is_valid_id_or_url(input_str: str) -> bool:
    parsed = parse_input(input_str)
    return parsed.type in ("id", "url")


def filter_importable(inputs: List[str]) -> List[ParsedQuery]:
    """
    Return only parsed inputs that are arXiv IDs or URLs.
    Discards search-type inputs.
    """
    return [parse_input(s) for s in inputs if is_valid_id_or_url(s)]
