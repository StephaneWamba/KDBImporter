from api import PaperlessClient
from dotenv import load_dotenv
# from post_consume import get_document_upload_data, get_metadata
from post_consume import get_metadata
from core import DocumentData
from config import get_logger

import sys
import os

def post_consume(doc_id: int):

    logger = get_logger("Logger4ScrappingoQo", level="DEBUG")

    load_dotenv()
    paperless_url = os.getenv("PAPERLESS_URL")
    paperless_token = os.getenv("PAPERLESS_TOKEN")

    logger.info("post_consume/webhook_paperless: Starting post-processing")

    pp = PaperlessClient(base_url=paperless_url, token=paperless_token)

    # document_paperless = get_document_upload_data(pp, doc_id)
    # pp.update_custom_fields(doc_id, {"Keywords": document_paperless.keywords})

    # document_paperless.update_paperless_custom_fields(pp, doc_id)

    response_doc = pp.get_document(doc_id)
    document_data = DocumentData.from_db(response_doc["title"])

    if document_data == None:
        logger.info(f"Document {response_doc["title"]} has been added Manualy.")

        document_data = DocumentData(title= response_doc["title"],
                                     created= response_doc["created_date"],
                                     added_via="Manual",
                                     )

    metadata = get_metadata(response_doc, document_data)
    document_data.tags = metadata["Tags"]
    document_data.keywords = metadata["Keywords"]

    # logger.debug(f"Metadata generaed:\n\n{metadata}\n")

    # pp.update_metadata(id, metadata)
    # document_data.update_paperless_metadata(pp, doc_id)
    
    try:
        document_data.update_paperless_metadata(pp, doc_id=doc_id)
        
        logger.info(f"webhook_paperless: Inserted metadata for doc id: {doc_id}. Metadata:\n{metadata}\n")

    except:
        logger.error(f"Failed to push metadata: metadata:\n{metadata}\nFor doc id: {doc_id}\n")


if __name__ == "__main__":
    doc_id = sys.argv[1]
    post_consume(doc_id)