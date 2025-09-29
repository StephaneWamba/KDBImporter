from pydantic import BaseModel, Field, HttpUrl, constr
from typing import List, Optional, Literal, Dict, Any


# ---------- Input Models ----------

class MetadataInput(BaseModel):
    importance: Optional[Literal["low", "medium", "high"]] = Field(
        None, description="Level of importance (low, medium, high)"
    )
    tag: Optional[constr(strip_whitespace=True, min_length=1)] = Field(
        None, description="Optional user-defined tag"
    )


class ImportRequest(BaseModel):
    inputs: List[str] = Field(..., description="List of arXiv URLs or IDs")
    metadata: Optional[List[MetadataInput]] = Field(
        None, description="List of metadata objects (same order as inputs)"
    )


class SearchRequest(BaseModel):
    query: str
    sort_by: Optional[Literal["relevance", "submittedDate"]] = "relevance"
    max_results: Optional[int] = 10
    metadata: Optional[MetadataInput] = None


# ---------- Output Models ----------

class PaperInfo(BaseModel):
    id: str
    title: str
    authors: List[str]
    summary: str
    pdf_url: Optional[HttpUrl]
    published: str
    updated: str


class MetadataOutput(BaseModel):
    importance: Optional[str] = None
    tag: Optional[str] = None
    raw_data: Dict[str, Any] = Field(default_factory=dict)


class ImportResult(BaseModel):
    input: str
    success: bool
    reason: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class ImportResponse(BaseModel):
    results: List[ImportResult]


class SearchResult(BaseModel):
    query: str
    paper: PaperInfo
    metadata: MetadataOutput


class SearchResponse(BaseModel):
    results: List[SearchResult]


# ---------- Paperless Integration Models ----------

class PaperlessUploadRequest(BaseModel):
    paper: PaperInfo
    metadata: Optional[MetadataOutput] = None


class PaperlessUploadResponse(BaseModel):
    task_id: str
    status: str


# ---------- Keyword Management Models ----------

class KeywordExtractionRequest(BaseModel):
    paper_data: PaperInfo


class KeywordExtractionResponse(BaseModel):
    primary_keywords: List[str]
    secondary_keywords: List[str]
    technical_terms: List[str]
    domain_tags: List[str]
    confidence_score: float
    extraction_method: str


class KeywordValidationRequest(BaseModel):
    keywords: List[str]


class KeywordValidationResponse(BaseModel):
    valid_keywords: List[str]
    invalid_keywords: List[str]
    suggestions: List[Dict[str, Any]]
    normalized_keywords: List[str]
