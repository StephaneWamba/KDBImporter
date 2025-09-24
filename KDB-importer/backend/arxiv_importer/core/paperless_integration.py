# backend/arxiv_importer/core/paperless_integration.py
import os
import requests
import asyncio
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class PaperlessIntegration:
    def __init__(self):
        self.paperless_url = os.getenv("PAPERLESS_BASE_URL")
        self.paperless_token = os.getenv("PAPERLESS_API_TOKEN")

        if not self.paperless_url or not self.paperless_token:
            raise ValueError(
                "PAPERLESS_BASE_URL and PAPERLESS_API_TOKEN must be set")

    def _get_headers(self):
        """Get headers for Paperless-ngx API"""
        return {"Authorization": f"Token {self.paperless_token}"}

    def _get_document_types(self):
        """Get available document types from Paperless-ngx"""
        response = requests.get(
            f"{self.paperless_url}/document_types/", headers=self._get_headers())
        if response.status_code == 200:
            data = response.json()
            return {dt["name"]: dt["id"] for dt in data.get("results", [])}
        return {}

    def _get_tags(self):
        """Get available tags from Paperless-ngx"""
        response = requests.get(
            f"{self.paperless_url}/tags/", headers=self._get_headers())
        if response.status_code == 200:
            data = response.json()
            return {tag["name"]: tag["id"] for tag in data.get("results", [])}
        return {}

    def _download_pdf(self, pdf_url: str) -> Optional[bytes]:
        """Download PDF from arXiv"""
        try:
            response = requests.get(pdf_url, timeout=30)
            if response.status_code == 200:
                return response.content
        except Exception as e:
            print(f"Error downloading PDF from {pdf_url}: {e}")
        return None

    async def upload_paper_to_paperless(self, paper: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Upload a paper to Paperless-ngx with metadata.
        Returns the task ID for async processing.
        """
        try:
            # Convert Pydantic model to dict if needed
            if hasattr(paper, 'model_dump'):
                paper_dict = paper.model_dump()
            elif hasattr(paper, 'dict'):
                paper_dict = paper.dict()
            else:
                paper_dict = paper

            # Convert metadata if needed
            if metadata and hasattr(metadata, 'model_dump'):
                metadata_dict = metadata.model_dump()
            elif metadata and hasattr(metadata, 'dict'):
                metadata_dict = metadata.dict()
            else:
                metadata_dict = metadata or {}

            # Get document types and tags
            doc_types = self._get_document_types()
            tags = self._get_tags()

            # Download PDF
            pdf_content = self._download_pdf(paper_dict["pdf_url"])
            if not pdf_content:
                raise ValueError(
                    f"Failed to download PDF from {paper_dict['pdf_url']}")

            # Prepare upload data
            upload_data = {
                "title": paper_dict["title"],
                "created": paper_dict["published"][:10],  # Extract date part
            }

            # Add document type (convert name to ID)
            doc_type_name = "Scientific-Paper"  # Default
            if doc_type_name in doc_types:
                upload_data["document_type"] = doc_types[doc_type_name]

            # Add tags if provided (convert names to IDs)
            if metadata_dict and metadata_dict.get("tag"):
                tag_name = metadata_dict.get("tag")
                if tag_name in tags:
                    upload_data["tags"] = [tags[tag_name]]

            # Prepare files
            files = {
                "document": (f"{paper_dict['id']}.pdf", pdf_content, "application/pdf")
            }

            # Upload to Paperless-ngx
            response = requests.post(
                f"{self.paperless_url}/documents/post_document/",
                data=upload_data,
                files=files,
                headers=self._get_headers()
            )

            if response.status_code == 200:
                task_id = response.text.strip('"')  # Remove quotes from UUID
                return task_id
            else:
                raise ValueError(
                    f"Paperless-ngx upload failed: {response.status_code} - {response.text}")

        except Exception as e:
            raise Exception(
                f"Failed to upload paper '{paper_dict.get('title', 'Unknown')}' to Paperless: {str(e)}")


# Create a global instance
paperless_integration = PaperlessIntegration()
