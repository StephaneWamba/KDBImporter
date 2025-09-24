from pathlib import Path
from typing import Any

from .APIClient import APIClient
from ..utils import create_tmp_import_file, clean_author_string, get_id_select_custom_field

from config import get_logger
from core import DocumentData
import json

logger = get_logger("Logger4ScrappingoQo")

class PaperlessClient(APIClient):
    id_tags: dict[str: int] = {}
    id_document_types: dict[str: int] = {}
    custom_fields: dict[str: dict[str: Any]] = {}

    def __init__(
        self,
        *,
        base_url: str,
        token: str,
        idle_time: float = 3,
        verify_ssl: bool | str = True,
        **kwargs,
    ) -> None:
        headers = {"Authorization": f"Token {token}"}
        super().__init__(base_url=base_url,idle_time=idle_time, headers=headers, **kwargs)
        self.verify_ssl = verify_ssl
        self.init_custom_fields()
        self.init_document_types()
        self.init_tags()

        logger.info("api/client/PaperlessClient: PP Init correctly.")

    def init_custom_fields(self):
        response = self.get_custom_fields()
        
        # Handle case where response might be a string (HTML error page)
        if isinstance(response, str):
            logger.error(f"Custom fields API returned string instead of JSON: {response[:200]}...")
            return
            
        if not isinstance(response, dict) or "results" not in response:
            logger.error(f"Custom fields API returned unexpected format: {type(response)} - {response}")
            return
            
        for field in response["results"]:
            field_data = {
                "id": field["id"],
                "type": field["data_type"]
            }

            if field_data["type"] == "select":
                field_data["select"]= [
                    {"id": choice["id"], "value": choice["label"]}
                    for choice in field.get("extra_data", []).get("select_options", [])
                ]
            
            self.custom_fields[field["name"]] = field_data


    def init_document_types(self):
        payload = self.get_document_types()
        
        # Handle case where response might be a string (HTML error page)
        if isinstance(payload, str):
            logger.error(f"Document types API returned string instead of JSON: {payload[:200]}...")
            return
            
        if not isinstance(payload, dict) or "results" not in payload:
            logger.error(f"Document types API returned unexpected format: {type(payload)} - {payload}")
            return

        for type in payload.get("results", []):
            name = type.get("name")
            type_id = type.get("id")
            if name and isinstance(type_id, int):
                self.id_document_types[name] = type_id

    def init_tags(self):
        page = 1
        response = self.get_tags(page)
        
        # Handle case where response might be a string (HTML error page)
        if isinstance(response, str):
            logger.error(f"Tags API returned string instead of JSON: {response[:200]}...")
            return
            
        if not isinstance(response, dict) or "results" not in response:
            logger.error(f"Tags API returned unexpected format: {type(response)} - {response}")
            return
            
        tags_list = []

        while  isinstance(response.get("next", None), str):
            response = self.get_tags(page)
            if isinstance(response, dict) and "results" in response:
                tags_list += response.get("results", [])
            page += 1

        if isinstance(response, dict) and "results" in response:
            tags_list += response.get("results", [])

        for tag in tags_list:
            name = tag.get("name")
            tag_id = tag.get("id")
            if name and isinstance(tag_id, int):
                self.id_tags[name] = tag_id

    def get_document_types(self, **filters) -> list[dict]:
        return self.get("/api/document_types/", params=filters)

    def get_documents(self, **filters) -> list[dict]:
        return self.get("/api/documents/", params=filters)

    def get_document(self, doc_id: int) -> dict:
        return self.get(f"/api/documents/{doc_id}/")

    def download_document(self, doc_id: int) -> bytes:
        return self.get(f"/api/documents/{doc_id}/download/", parse_json=False)

    def upload_document(
        self,
        file_path: str | Path,
        doc_data: DocumentData,
    ) -> dict:
        file_path = Path(file_path)

        if not file_path.is_file():
            logger.error(f"PaperlessClient.py/upload_document: Path doesn't exist: {file_path}")
            raise FileNotFoundError(file_path)
        
        data = doc_data.get_upload_data()

        if not data["document_type"] in self.id_document_types:
            logger.error(f"PaperlessClient.py/upload_document: Wrong Document_type: {data['document_type']}")
            raise ValueError("Wrong document_type")

        data["document_type"] = self.id_document_types[data["document_type"]]

        with file_path.open("rb") as fh:
            files = {"document": (file_path.name, fh, "application/pdf")}
            # logger.debug(f"PaperlessClient/upload: Data sended: {data}")
            return self.post(
                "/api/documents/post_document/",
                data=data,
                files=files,
            )

    def get_tags(self, page: int) -> list[dict]:
        return self.get(f"/api/tags/?page={page}&full_perms=true")
    
    def get_custom_fields(self) -> list[dict]:
        return self.get("/api/custom_fields/")

    def get_correspondents(self) -> list[dict]:
        return self.get("/api/correspondents/")

    def search_documents(self, query: str, **extra_filters) -> list[dict]:
        return self.list_documents(q=query, **extra_filters)
    
    def build_query_custom_fields(self, custom_fields: dict[str, Any]) -> list[dict[str, Any]]:
        resolved: list[dict[int, Any]] = []
        unknown: list[str] = []

        for name, val in custom_fields.items():
            field_data = self.custom_fields.get(name)
            field_id = field_data["id"]
            field_value_or_id: str = get_id_select_custom_field(val, field_data["select"]) if field_data["type"] == "select" else val

            if name == "Authors":
                field_value_or_id = clean_author_string(field_value_or_id)

            if field_id is None or field_value_or_id is None:
                unknown.append(name)
            else:
                resolved.append({"field": str(field_id), "value": field_value_or_id})

        if unknown:
            raise KeyError(
                f"Custom field(s) not found: {', '.join(unknown)}"
            )
        
        return resolved if len(resolved) != 0 else None
    
    def prepare_tags_list(self, tags: list[str]) -> list[int] :
        tags_id: list[int] = []
        unknown: list[str] = []
        known: list[str] = []

        for tag in tags:
            tag_id = self.id_tags.get(tag)
            if tag_id is None:
                unknown.append(tag)
            else:
                tags_id.append(tag_id)
                known.append(tag)

        if len(unknown) != 0:
            logger.warning(
                f"Tags(s) not found in Paperless: {', '.join(unknown)}"
            )
        

        logger.debug(
                f"Tags(s) found in Paperless: {', '.join(tag)}"
            )
        return tags_id

    def update_custom_fields(
        self,
        doc_id: int,
        field_values: dict[int, Any],
    ) -> dict:
        payload = {"custom_fields": self.build_query_custom_fields(field_values)}

        return self.patch(f"/api/documents/{doc_id}/?full_perms=true", json=payload)
    
    def update_metadata(
        self,
        doc_id: int,
        metadata: dict[str, Any],
    ) -> dict:
        payload = {}

        if metadata["custom_fields"]:
            payload["custom_fields"] = self.build_query_custom_fields(metadata["custom_fields"])
        if metadata["tags"]:
            payload["tags"] = self.prepare_tags_list(metadata["tags"])

        return self.patch(f"/api/documents/{doc_id}/?full_perms=true", json=payload) # TO TEST WIWITHOUT full_perm

    def import_entries(
        self,
        entries: list[DocumentData],
    ) -> list[dict]:
        results: list[dict] = []

        for entry in entries:
            try:
                if not entry.already_seen():
                    self.time_action(3)

                    tmp_path = create_tmp_import_file(
                        pdf_url = entry.download_url,
                        content = entry.content,
                        title = entry.title,
                        creation_date = entry.created,
                    )

                    entry.save_to_db()

                    try:
                        results.append(self.upload_document(tmp_path, entry))
                    finally:
                        try:
                            tmp_path.unlink(missing_ok=True)
                        except Exception:
                            pass
                else:
                    logger.info("PaperlessClient/import_entries: Entry already added.")

            except Exception as exc:
                logger.error(
                    "PaperlessClient/import_entries: failed to create temp doc for "
                    "'%s' — %s",
                    entry.title, exc,
                    exc_info=True,
                )
                continue


        return results
