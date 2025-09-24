import os
import sys
from dotenv import load_dotenv
from typing import Any
from core import DocumentData
from api import PaperlessClient

from config import get_logger
from .metagen import metadata_generator

load_dotenv("../../.env")
BASE_URL = os.environ.get("PAPERLESS_URL", "http://localhost:8000").rstrip("/")
INCLUDE_PATH = os.environ.get("INCLUDE_PATH")

logger = get_logger("Logger4ScrappingoQo", level="DEBUG")

available_tags =[
    "Quantum Algorithm",
    "Quantum Key Distribution (QKD)",
    "Regulatory",
    "Standards",
    "Quantum Computing",
    "Quantum Hardware",
    "Quantum Communication",
    "Post Quantum Cryptography (PQC)",
    "Cybersecurity",
    "Cryptography",
    "Quantum Benchmarking",
    "Noisy Intermediate-Scale Quantum (NISQ)",
    "Quantum Error Correction",
    "IBM Qiskit",
    "Google Cirq",
    "Rigetti Forest, Quil",
    "Microsoft Q#, QDK",
    "Xanadu PennyLane",
    "Amazon Braket",
    "D-Wave Ocean SDK",
    "QuTiP",
    "ProjectQ",
    "OpenFermion",
    "Quantum Cloud Computing",
    "Quantum Networking",
    "Quantum AI",
    "Quantum Blockchain",
    "Quantum Ethics",
    "Quantum Supremacy and Advantage",
    "Quantum Programming Languages",
    "Quantum Operating Systems"
]

def read_lines_to_list(file_path: str) -> list[str]:
    """
    Reads the given text file and returns a list where each entry
    is one line from the file (without the trailing newline).
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return [line.rstrip('\n') for line in f]
    except FileNotFoundError:
        logger.error(f"WARNING: file not found: {file_path}")
        return []

# def get_metadata(paperless_client: PaperlessClient, doc_id: int) -> dict[str, Any]:
#     INCLUDE_PATH = os.environ.get("INCLUDE_PATH")
#     l_tag = tags
#     # l_tag = read_lines_to_list(os.path.join(INCLUDE_PATH,"../tags.txt"))
#     # l_cat = read_lines_to_list(os.path.join(INCLUDE_PATH,"categories.txt"))

#     response_doc = paperless_client.get_document(doc_id)
#     document_data: DocumentData = DocumentData.from_db(response_doc["title"])

#     if not document_data:
#         logger.error(f"post_consume/get_metadata: Didn't find any document data, Abort post consume")
#         return

#     need_tags = document_data.tags is not None
#     need_keywords = document_data.keywords is not None
#     need_categories = False
#     content_doc = response_doc["content"]

#     metadata: dict[str, Any] = metadata_generator(
#         content_doc,
#         need_keywords,
#         need_tags,
#         need_categories,
#         l_tag,
#     )

#     return metadata

def get_metadata(response_paperless_document: dict[Any, Any], document_data: DocumentData) -> dict[str, Any]:
    INCLUDE_PATH = os.environ.get("INCLUDE_PATH")
    l_tag = available_tags
    # l_tag = read_lines_to_list(os.path.join(INCLUDE_PATH,"../tags.txt"))

    # document_data: DocumentData = DocumentData.from_db(response_paperless_document["title"])

    # if not document_data:
    #     logger.error(f"post_consume/get_metadata: Didn't find any document data, Abort post consume")
    #     return

    need_tags = document_data.tags is not None
    need_keywords = document_data.keywords is not None
    need_categories = False
    content_doc = response_paperless_document["content"]

    metadata: dict[str, Any] = metadata_generator(
        content_doc,
        need_keywords,
        need_tags,
        need_categories,
        l_tag,
    )

    return metadata