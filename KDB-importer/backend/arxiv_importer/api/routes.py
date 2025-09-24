from fastapi import APIRouter, HTTPException, Query
from datetime import date
from ..core import import_manager, search_manager
from ..core.keyword_manager import keyword_manager
from ..core.paperless_integration import paperless_integration
from ..core.metrics_tracker import metrics_tracker
from ..api.schemas.import_models import (
    ImportRequest, ImportResponse,
    SearchRequest, SearchResponse,
    PaperlessUploadRequest, PaperlessUploadResponse,
    KeywordExtractionRequest, KeywordExtractionResponse,
    KeywordValidationRequest, KeywordValidationResponse
)

router = APIRouter()


@router.post("/import", response_model=ImportResponse)
async def import_papers(payload: ImportRequest):
    """
    Import a list of arXiv IDs or URLs with optional metadata per item.
    """
    metadata = [m.model_dump()
                for m in payload.metadata] if payload.metadata else []
    results = import_manager.import_ids_or_urls(payload.inputs, metadata)

    # Track successful imports
    for result in results:
        if isinstance(result, dict) and result.get("success") and result.get("data", {}).get("paper"):
            metrics_tracker.track_paper_import(
                paper_title=result["data"]["paper"]["title"],
                success=True
            )

    return {"results": results}


@router.post("/search", response_model=SearchResponse)
async def search_papers(payload: SearchRequest):
    """
    Search arXiv by query and return multiple matching papers, enriched with shared metadata.
    """
    metadata = payload.metadata.model_dump() if payload.metadata else {}
    results = search_manager.search_with_metadata(
        query=payload.query,
        sort_by=payload.sort_by,
        max_results=payload.max_results,
        metadata=metadata
    )
    return {"results": results}


@router.post("/paperless/upload", response_model=PaperlessUploadResponse)
async def upload_to_paperless(payload: PaperlessUploadRequest):
    """
    Upload a paper to Paperless-ngx with metadata.
    """
    try:
        task_id = await paperless_integration.upload_paper_to_paperless(
            paper=payload.paper,
            metadata=payload.metadata
        )

        # Track successful upload
        from ..core.metrics_tracker import PaperlessUpload
        from datetime import datetime
        metrics_tracker.track_paperless_upload(
            PaperlessUpload(
                timestamp=datetime.now().isoformat(),
                paper_title=payload.paper.title,
                task_id=task_id,
                status="success",
                metadata=payload.metadata.model_dump() if payload.metadata else {}
            )
        )

        return {"task_id": task_id, "status": "queued"}
    except Exception as e:
        # Track failed upload
        from ..core.metrics_tracker import PaperlessUpload
        from datetime import datetime
        metrics_tracker.track_paperless_upload(
            PaperlessUpload(
                timestamp=datetime.now().isoformat(),
                paper_title=payload.paper.title,
                task_id="",
                status="error",
                metadata={"error": str(e)}
            )
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to upload to Paperless: {str(e)}")


@router.post("/keywords/extract", response_model=KeywordExtractionResponse)
async def extract_keywords(payload: KeywordExtractionRequest):
    """
    Extract keywords from paper data using AI and statistical methods.
    """
    try:
        result = keyword_manager.suggest_keywords_for_paper(payload.paper_data)

        # Track keyword extraction
        from ..core.metrics_tracker import KeywordExtraction
        from datetime import datetime
        metrics_tracker.track_keyword_extraction(
            KeywordExtraction(
                timestamp=datetime.now().isoformat(),
                paper_title=payload.paper_data.title,
                primary_keywords=result.primary_keywords,
                secondary_keywords=result.secondary_keywords,
                technical_terms=result.technical_terms,
                domain_tags=result.domain_tags,
                confidence_score=result.confidence_score,
                extraction_method=result.extraction_method
            )
        )

        return {
            "primary_keywords": result.primary_keywords,
            "secondary_keywords": result.secondary_keywords,
            "technical_terms": result.technical_terms,
            "domain_tags": result.domain_tags,
            "confidence_score": result.confidence_score,
            "extraction_method": result.extraction_method
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to extract keywords: {str(e)}")


@router.post("/keywords/validate", response_model=KeywordValidationResponse)
async def validate_keywords(payload: KeywordValidationRequest):
    """
    Validate and normalize a list of keywords.
    """
    try:
        result = keyword_manager.validate_keywords(payload.keywords)
        return {
            "valid_keywords": result["valid_keywords"],
            "invalid_keywords": result["invalid_keywords"],
            "suggestions": result["suggestions"],
            "normalized_keywords": result["normalized_keywords"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to validate keywords: {str(e)}")


@router.get("/keywords/domains")
async def get_available_domains():
    """
    Get list of available quantum computing domains for keyword classification.
    """
    return {
        "domains": keyword_manager.quantum_domains,
        "technical_terms": list(keyword_manager.technical_terms)
    }


# ---------- Dashboard Analytics Endpoints ----------

@router.get("/dashboard/stats")
async def get_dashboard_stats():
    """
    Get comprehensive dashboard statistics and analytics.
    """
    try:
        # Get real metrics from metrics tracker
        stats = metrics_tracker.get_dashboard_stats()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get dashboard stats: {str(e)}")


@router.get("/dashboard/analytics")
async def get_dashboard_analytics():
    """
    Get detailed analytics for the dashboard.
    """
    try:
        # Get real analytics from metrics tracker
        analytics = metrics_tracker.get_dashboard_analytics()
        return analytics
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get analytics: {str(e)}")


# ---------- Document History Endpoints ----------

@router.get("/history/dates")
async def get_available_dates():
    """
    Get list of dates that have activity data.
    """
    try:
        dates = metrics_tracker.get_available_dates()
        return {"dates": dates}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get available dates: {str(e)}")


@router.get("/history/date/{target_date}")
async def get_document_history_by_date(target_date: str):
    """
    Get all documents processed on a specific date.
    """
    try:
        # Parse date string
        parsed_date = date.fromisoformat(target_date)
        history = metrics_tracker.get_document_history_by_date(parsed_date)
        return history
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get document history: {str(e)}")


@router.get("/history/range")
async def get_document_summary_by_range(
    start_date: str = Query(...,
                            description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format")
):
    """
    Get summary of documents processed in a date range.
    """
    try:
        # Parse date strings
        start_parsed = date.fromisoformat(start_date)
        end_parsed = date.fromisoformat(end_date)

        if start_parsed > end_parsed:
            raise HTTPException(
                status_code=400, detail="Start date must be before end date")

        summary = metrics_tracker.get_document_summary_by_date_range(
            start_parsed, end_parsed)
        return summary
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get document summary: {str(e)}")
