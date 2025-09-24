from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional, Any
from requests.exceptions import HTTPError

import json

from config import get_logger
from .Database import fetch_article_row, remember, mark_synced, already_seen
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from api import PaperlessClient

logger = get_logger("Logger4ScrappingoQo", level="DEBUG")

paperlessCS_to_databaseCS: dict[str, str] = {
    "Authors": "authors",
    "Keywords": "keywords",
    "Affiliated-Organization": "affiliated_organization",
    "Source": "source",
    "Download-URL": "download_url",
    "Added-Via": "added_via",
    "Scope": "scope",
    "oQo-Theme": "oqo_theme",
    "Qurisk-Relevance": "qurisk_relevence",
    "Import-Query": "import_query",
}

databaseCS_to_paperlessCS: dict[str, str] = { 
    v: k for k, v in paperlessCS_to_databaseCS.items()
}

@dataclass
class DocumentData:
    # --- Mandatory fields ---
    title: str
    created: date | str
    document_type: Optional[str] = None

    download_url: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[list[str]] = None
    
    # ----- Custom fields ----
    authors: str = "Not-Specified"
    keywords: Optional[str] = None
    affiliated_organization: Optional[str] = None
    source: str = "Not-Specified"
    added_via: str = "Script"
    scope: Optional[str] = None
    oqo_theme: Optional[str] = None
    qurisk_relevence: int = 4
    import_query: Optional[str] = None

    # ------ Others ------
    article_url: Optional[str] = None
    storage_path: Optional[str] = None
    correspondant: Optional[str] = None

    def __post_init__(self):
        if self.created:
            if isinstance(self.created, datetime):
                self.create = self.created.isoformat()
            else:
                try:
                    date.fromisoformat(self.created)
                    self.create = str(date.fromisoformat(self.created))
                except ValueError:
                    logger.error(f"Document_UploadInvalid/__init__: Invalid format: {self.created}")

        if self.added_via == "Script" and not self.content and not self.download_url:
            logger.error(f"DocumentData/Init: no pdf_url and no content.")
            raise ValueError("No pdf_url and no content.")
        

    @classmethod
    def from_db(cls, title: str) -> Optional["DocumentData"]:
        db_row = fetch_article_row(title)

        if db_row is None:
            logger.error(f"DocumentData.from_db: aucun enregistrement pour « {title} »")
            return None

        kwargs: dict[str, Any] = {
            "title": db_row["title"],
            "created": db_row.get("date_iso") or db_row.get("created") or date.today().isoformat(),
            "source": db_row.get("source", "Not-Specified"),
            "document_type": db_row.get("document_type"),
        }

        raw_json = db_row.get("custom_fields_json")
        if raw_json:
            try:
                custom_fields: dict[str, Any] = raw_json
                for k, v in custom_fields.items():
                    attr = paperlessCS_to_databaseCS.get(k)
                    if attr:
                        kwargs[attr] = v
            except json.JSONDecodeError as exc:
                logger.error("Invalid JSON for %s: %s", title, exc)

        obj = cls.__new__(cls)
        for k, v in kwargs.items():
            setattr(obj, k, v)
        obj.create = str(date.fromisoformat(str(obj.created)))

        return obj

    def get_upload_data(self):
        return {k: v for k, v in {
            "title": self.title,
            "created": self.created,
            "document_type": self.document_type,
            "correspondant": self.correspondant,
            "storage_path": self.storage_path
        }.items() if v is not None}

    def save_to_db(self) -> None:
        remember(self.title, self.create, self.source, self.get_custom_fields_data())

    def already_seen(self) -> bool:
        return already_seen(self.title)
    
    def update_paperless_metadata(self, paperless_client: "PaperlessClient", doc_id: int):
        try:
            metadata = {"custom_fields": self.get_custom_fields_data(), "tags": self.tags}
            response = paperless_client.update_metadata(doc_id, metadata)

            if self.tags:
                response["Tags"] = self.tags
        except HTTPError as exc:
            status = exc.response.status_code if exc.response else "???"
            raise RuntimeError(
                f"DocumentData/update_custom_fields: HTTP error {status}"
            ) from exc

        mark_synced(self.title)
        # logger.info(
        #     "DocumentData/update_paperless_custom_fields: "
        #     "Updated custom fields in Paperless for id %s",
        #     doc_id,
        # )
        
    def get_custom_fields_data(self, include_none: bool = False):
        paperless_labeled_custom_fields = {
            cf_label: getattr(self, attr_name) for cf_label, attr_name in paperlessCS_to_databaseCS.items()
            }
        return (paperless_labeled_custom_fields 
                if include_none 
                else {
                    k: v for k, v in paperless_labeled_custom_fields.items() 
                    if v is not None
                    }
                )

    def pretty_str(self) -> str:
        """Print document informations"""
        fields = [
            ("Title",           self.title),
            ("Created",         self.created),
            ("Added via",       self.added_via),
            ("Authors",         self.authors),
            ("Document type",   self.document_type),
            ("Organisme",       self.affiliated_organization),
            ("content",         self.content),
            ("PDF URL",         self.download_url),
            ("Article URL",     self.article_url),
            ("Query",           self.import_query),
        ]

        width = max(len(label) for label, _ in fields)

        lines = [
            f"{label:<{width}} : {value}"
            for label, value in fields
            if value not in (None, "", [])
        ]
        return "\n".join(lines) + "\n" or "<vide>"

    __str__ = pretty_str
