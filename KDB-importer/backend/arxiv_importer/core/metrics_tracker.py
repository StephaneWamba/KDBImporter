# backend/arxiv_importer/core/metrics_tracker.py
import os
import json
import time
from datetime import datetime, timedelta, date
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()


@dataclass
class ActivityEvent:
    """Represents a single activity event"""
    timestamp: str
    event_type: str  # 'import', 'keyword_extraction', 'paperless_upload', 'search'
    title: str
    status: str  # 'success', 'error'
    details: Dict[str, Any]


@dataclass
class KeywordExtraction:
    """Represents a keyword extraction event"""
    timestamp: str
    paper_title: str
    primary_keywords: List[str]
    secondary_keywords: List[str]
    technical_terms: List[str]
    domain_tags: List[str]
    confidence_score: float
    extraction_method: str


@dataclass
class PaperlessUpload:
    """Represents a Paperless upload event"""
    timestamp: str
    paper_title: str
    task_id: str
    status: str
    metadata: Dict[str, Any]


class MetricsTracker:
    """Tracks and manages system metrics with PostgreSQL persistence"""

    def __init__(self):
        self.db_config = {
            'host': os.getenv('PG_HOST', 'postgres'),
            'port': os.getenv('PG_PORT', '5432'),
            'user': os.getenv('PG_USER', 'myuser'),
            'password': os.getenv('PG_PASSWORD', 'mypassword'),
            'database': os.getenv('PG_DB', 'mydatabase')
        }
        self._ensure_tables_exist()

    def _get_connection(self):
        """Get database connection"""
        return psycopg2.connect(**self.db_config)

    def _ensure_tables_exist(self):
        """Ensure all required tables exist"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    # Check if tables exist
                    cur.execute("""
                        SELECT table_name FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name IN ('daily_metrics', 'activity_events', 'keyword_extractions', 'paperless_uploads')
                    """)
                    existing_tables = [row[0] for row in cur.fetchall()]

                    if len(existing_tables) < 4:
                        print(
                            "Warning: Some metrics tables are missing. Please run database_schema.sql")
        except Exception as e:
            print(f"Warning: Could not verify database tables: {e}")

    def track_paper_import(self, paper_title: str, success: bool = True):
        """Track a paper import event"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO activity_events (timestamp, event_type, title, status, details)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        datetime.now(),
                        "import",
                        f"Imported: {paper_title}",
                        "success" if success else "error",
                        json.dumps({"paper_title": paper_title})
                    ))
                    conn.commit()
                    self._update_daily_metrics(date.today())
        except Exception as e:
            print(f"Error tracking paper import: {e}")

    def track_keyword_extraction(self, extraction: KeywordExtraction):
        """Track a keyword extraction event"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    # Insert keyword extraction
                    cur.execute("""
                        INSERT INTO keyword_extractions 
                        (timestamp, paper_title, primary_keywords, secondary_keywords, 
                         technical_terms, domain_tags, confidence_score, extraction_method)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        datetime.now(),
                        extraction.paper_title,
                        extraction.primary_keywords,
                        extraction.secondary_keywords,
                        extraction.technical_terms,
                        extraction.domain_tags,
                        extraction.confidence_score,
                        extraction.extraction_method
                    ))

                    # Insert activity event
                    cur.execute("""
                        INSERT INTO activity_events (timestamp, event_type, title, status, details)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        datetime.now(),
                        "keyword_extraction",
                        f"Extracted keywords: {extraction.paper_title}",
                        "success",
                        json.dumps({
                            "paper_title": extraction.paper_title,
                            "confidence_score": extraction.confidence_score,
                            "keyword_count": len(extraction.primary_keywords)
                        })
                    ))
                    conn.commit()
                    self._update_daily_metrics(date.today())
        except Exception as e:
            print(f"Error tracking keyword extraction: {e}")

    def track_paperless_upload(self, upload: PaperlessUpload):
        """Track a Paperless upload event"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    # Insert upload record
                    cur.execute("""
                        INSERT INTO paperless_uploads (timestamp, paper_title, task_id, status, metadata)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        datetime.now(),
                        upload.paper_title,
                        upload.task_id,
                        upload.status,
                        json.dumps(upload.metadata)
                    ))

                    # Insert activity event
                    cur.execute("""
                        INSERT INTO activity_events (timestamp, event_type, title, status, details)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        datetime.now(),
                        "paperless_upload",
                        f"Uploaded to Paperless: {upload.paper_title}",
                        upload.status,
                        json.dumps({
                            "paper_title": upload.paper_title,
                            "task_id": upload.task_id
                        })
                    ))
                    conn.commit()
                    self._update_daily_metrics(date.today())
        except Exception as e:
            print(f"Error tracking paperless upload: {e}")

    def _update_daily_metrics(self, target_date: date):
        """Update daily metrics for a specific date"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT update_daily_metrics(%s)",
                                (target_date,))
                    conn.commit()
        except Exception as e:
            print(f"Error updating daily metrics: {e}")

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get current dashboard statistics"""
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Get today's metrics
                    cur.execute("""
                        SELECT * FROM daily_metrics 
                        WHERE date = %s
                    """, (date.today(),))
                    today_metrics = cur.fetchone()

                    # Get recent activities (last 10)
                    cur.execute("""
                        SELECT event_type as type, title, timestamp, status
                        FROM activity_events 
                        ORDER BY timestamp DESC 
                        LIMIT 10
                    """)
                    recent_activities = cur.fetchall()

                    # Format activities
                    formatted_activities = []
                    for activity in recent_activities:
                        formatted_activities.append({
                            "type": activity['type'],
                            "title": activity['title'],
                            "timestamp": activity['timestamp'].isoformat(),
                            "status": activity['status']
                        })

                    return {
                        "total_papers_imported": today_metrics['papers_imported'] if today_metrics else 0,
                        "papers_uploaded_to_paperless": today_metrics['papers_uploaded'] if today_metrics else 0,
                        "total_keywords_extracted": today_metrics['keywords_extracted'] if today_metrics else 0,
                        "average_confidence_score": float(today_metrics['avg_confidence_score']) if today_metrics else 0.0,
                        "most_common_domains": [],  # Will be populated from keyword analytics
                        "recent_activity": formatted_activities,
                        "system_health": {
                            "backend_status": "healthy",
                            "paperless_connection": "connected",
                            "openai_api": "active"
                        }
                    }
        except Exception as e:
            print(f"Error getting dashboard stats: {e}")
            return {
                "total_papers_imported": 0,
                "papers_uploaded_to_paperless": 0,
                "total_keywords_extracted": 0,
                "average_confidence_score": 0.0,
                "most_common_domains": [],
                "recent_activity": [],
                "system_health": {
                    "backend_status": "healthy",
                    "paperless_connection": "connected",
                    "openai_api": "active"
                }
            }

    def get_dashboard_analytics(self) -> Dict[str, Any]:
        """Get detailed analytics for dashboard"""
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Get keyword analytics
                    cur.execute("""
                        SELECT 
                            unnest(primary_keywords) as keyword,
                            COUNT(*) as count
                        FROM keyword_extractions 
                        WHERE date >= %s
                        GROUP BY keyword
                        ORDER BY count DESC
                        LIMIT 10
                    """, (date.today() - timedelta(days=30),))
                    keyword_counts = cur.fetchall()

                    # Get domain distribution
                    cur.execute("""
                        SELECT 
                            unnest(domain_tags) as domain,
                            COUNT(*) as count
                        FROM keyword_extractions 
                        WHERE date >= %s
                        GROUP BY domain
                        ORDER BY count DESC
                    """, (date.today() - timedelta(days=30),))
                    domain_distribution = {
                        row['domain']: row['count'] for row in cur.fetchall()}

                    # Get confidence trends (last 20 extractions)
                    cur.execute("""
                        SELECT timestamp, confidence_score as confidence
                        FROM keyword_extractions 
                        ORDER BY timestamp DESC 
                        LIMIT 20
                    """)
                    confidence_trends = cur.fetchall()

                    # Get upload success rate
                    cur.execute("""
                        SELECT 
                            COUNT(*) as total,
                            COUNT(CASE WHEN status = 'success' THEN 1 END) as successful
                        FROM paperless_uploads 
                        WHERE date >= %s
                    """, (date.today() - timedelta(days=30),))
                    upload_stats = cur.fetchone()

                    success_rate = 0.0
                    if upload_stats['total'] > 0:
                        success_rate = upload_stats['successful'] / \
                            upload_stats['total']

                    return {
                        "import_trends": {
                            "daily": [],  # Could be enhanced with time-based analysis
                            "weekly": [],
                            "monthly": []
                        },
                        "keyword_analytics": {
                            "most_used_keywords": [{"keyword": row['keyword'], "count": row['count']} for row in keyword_counts],
                            "domain_distribution": domain_distribution,
                            "confidence_trends": [{"timestamp": row['timestamp'].isoformat(), "confidence": float(row['confidence'])} for row in confidence_trends]
                        },
                        "paperless_analytics": {
                            "upload_success_rate": success_rate,
                            "processing_times": [],  # Could be enhanced
                            "error_rates": []
                        }
                    }
        except Exception as e:
            print(f"Error getting dashboard analytics: {e}")
            return {
                "import_trends": {
                    "daily": [],
                    "weekly": [],
                    "monthly": []
                },
                "keyword_analytics": {
                    "most_used_keywords": [],
                    "domain_distribution": {},
                    "confidence_trends": []
                },
                "paperless_analytics": {
                    "upload_success_rate": 0.0,
                    "processing_times": [],
                    "error_rates": []
                }
            }

    def get_document_history_by_date(self, target_date: date) -> Dict[str, Any]:
        """Get all documents processed on a specific date"""
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Get all activities for the date
                    cur.execute("""
                        SELECT event_type, title, timestamp, status, details
                        FROM activity_events 
                        WHERE date = %s
                        ORDER BY timestamp DESC
                    """, (target_date,))
                    activities = cur.fetchall()

                    # Get keyword extractions for the date
                    cur.execute("""
                        SELECT paper_title, primary_keywords, secondary_keywords, 
                               technical_terms, domain_tags, confidence_score, 
                               extraction_method, timestamp
                        FROM keyword_extractions 
                        WHERE date = %s
                        ORDER BY timestamp DESC
                    """, (target_date,))
                    keyword_extractions = cur.fetchall()

                    # Get paperless uploads for the date
                    cur.execute("""
                        SELECT paper_title, task_id, status, metadata, timestamp
                        FROM paperless_uploads 
                        WHERE date = %s
                        ORDER BY timestamp DESC
                    """, (target_date,))
                    uploads = cur.fetchall()

                    # Get daily metrics for the date
                    cur.execute("""
                        SELECT * FROM daily_metrics 
                        WHERE date = %s
                    """, (target_date,))
                    daily_metrics = cur.fetchone()

                    return {
                        "date": target_date.isoformat(),
                        "daily_metrics": {
                            "papers_imported": daily_metrics['papers_imported'] if daily_metrics else 0,
                            "papers_uploaded": daily_metrics['papers_uploaded'] if daily_metrics else 0,
                            "keywords_extracted": daily_metrics['keywords_extracted'] if daily_metrics else 0,
                            "avg_confidence_score": float(daily_metrics['avg_confidence_score']) if daily_metrics else 0.0
                        },
                        "activities": [
                            {
                                "type": activity['event_type'],
                                "title": activity['title'],
                                "timestamp": activity['timestamp'].isoformat(),
                                "status": activity['status'],
                                "details": activity['details']
                            } for activity in activities
                        ],
                        "keyword_extractions": [
                            {
                                "paper_title": ke['paper_title'],
                                "primary_keywords": ke['primary_keywords'],
                                "secondary_keywords": ke['secondary_keywords'],
                                "technical_terms": ke['technical_terms'],
                                "domain_tags": ke['domain_tags'],
                                "confidence_score": float(ke['confidence_score']),
                                "extraction_method": ke['extraction_method'],
                                "timestamp": ke['timestamp'].isoformat()
                            } for ke in keyword_extractions
                        ],
                        "paperless_uploads": [
                            {
                                "paper_title": upload['paper_title'],
                                "task_id": upload['task_id'],
                                "status": upload['status'],
                                "metadata": upload['metadata'],
                                "timestamp": upload['timestamp'].isoformat()
                            } for upload in uploads
                        ]
                    }
        except Exception as e:
            print(f"Error getting document history: {e}")
            return {
                "date": target_date.isoformat(),
                "daily_metrics": {"papers_imported": 0, "papers_uploaded": 0, "keywords_extracted": 0, "avg_confidence_score": 0.0},
                "activities": [],
                "keyword_extractions": [],
                "paperless_uploads": []
            }

    def get_available_dates(self) -> List[str]:
        """Get list of dates that have activity data"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT DISTINCT date 
                        FROM activity_events 
                        ORDER BY date DESC
                        LIMIT 30
                    """)
                    dates = [row[0].isoformat() for row in cur.fetchall()]
                    return dates
        except Exception as e:
            print(f"Error getting available dates: {e}")
            return []

    def get_document_summary_by_date_range(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Get summary of documents processed in a date range"""
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Get aggregated metrics for the date range
                    cur.execute("""
                        SELECT 
                            SUM(papers_imported) as total_imports,
                            SUM(papers_uploaded) as total_uploads,
                            SUM(keywords_extracted) as total_keywords,
                            AVG(avg_confidence_score) as avg_confidence
                        FROM daily_metrics 
                        WHERE date BETWEEN %s AND %s
                    """, (start_date, end_date))
                    summary = cur.fetchone()

                    # Get unique papers processed
                    cur.execute("""
                        SELECT DISTINCT 
                            CASE 
                                WHEN event_type = 'import' THEN details->>'paper_title'
                                WHEN event_type = 'keyword_extraction' THEN details->>'paper_title'
                                WHEN event_type = 'paperless_upload' THEN details->>'paper_title'
                            END as paper_title,
                            MIN(timestamp) as first_seen
                        FROM activity_events 
                        WHERE date BETWEEN %s AND %s
                        AND details->>'paper_title' IS NOT NULL
                        GROUP BY paper_title
                        ORDER BY first_seen DESC
                    """, (start_date, end_date))
                    unique_papers = cur.fetchall()

                    return {
                        "date_range": {
                            "start_date": start_date.isoformat(),
                            "end_date": end_date.isoformat()
                        },
                        "summary": {
                            "total_imports": summary['total_imports'] or 0,
                            "total_uploads": summary['total_uploads'] or 0,
                            "total_keywords": summary['total_keywords'] or 0,
                            "avg_confidence": float(summary['avg_confidence'] or 0.0)
                        },
                        "unique_papers": [
                            {
                                "title": paper['paper_title'],
                                "first_seen": paper['first_seen'].isoformat()
                            } for paper in unique_papers
                        ]
                    }
        except Exception as e:
            print(f"Error getting document summary: {e}")
            return {
                "date_range": {"start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
                "summary": {"total_imports": 0, "total_uploads": 0, "total_keywords": 0, "avg_confidence": 0.0},
                "unique_papers": []
            }


# Create global instance
metrics_tracker = MetricsTracker()
