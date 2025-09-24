-- Database schema for persistent metrics storage
-- This file creates the necessary tables for date-based metrics tracking

-- Daily aggregated metrics
CREATE TABLE IF NOT EXISTS daily_metrics (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    papers_imported INTEGER DEFAULT 0,
    papers_uploaded INTEGER DEFAULT 0,
    keywords_extracted INTEGER DEFAULT 0,
    avg_confidence_score DECIMAL(3,2) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Individual activity events
CREATE TABLE IF NOT EXISTS activity_events (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    title TEXT NOT NULL,
    status VARCHAR(20) NOT NULL,
    details JSONB,
    date DATE GENERATED ALWAYS AS (timestamp::DATE) STORED
);

-- Keyword extraction history
CREATE TABLE IF NOT EXISTS keyword_extractions (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    paper_title TEXT NOT NULL,
    primary_keywords TEXT[],
    secondary_keywords TEXT[],
    technical_terms TEXT[],
    domain_tags TEXT[],
    confidence_score DECIMAL(3,2),
    extraction_method VARCHAR(50),
    date DATE GENERATED ALWAYS AS (timestamp::DATE) STORED
);

-- Paperless upload history
CREATE TABLE IF NOT EXISTS paperless_uploads (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    paper_title TEXT NOT NULL,
    task_id VARCHAR(100),
    status VARCHAR(20) NOT NULL,
    metadata JSONB,
    date DATE GENERATED ALWAYS AS (timestamp::DATE) STORED
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_activity_events_date ON activity_events(date);
CREATE INDEX IF NOT EXISTS idx_activity_events_type ON activity_events(event_type);
CREATE INDEX IF NOT EXISTS idx_keyword_extractions_date ON keyword_extractions(date);
CREATE INDEX IF NOT EXISTS idx_paperless_uploads_date ON paperless_uploads(date);
CREATE INDEX IF NOT EXISTS idx_daily_metrics_date ON daily_metrics(date);

-- Function to update daily metrics
CREATE OR REPLACE FUNCTION update_daily_metrics(target_date DATE)
RETURNS VOID AS $$
BEGIN
    INSERT INTO daily_metrics (date, papers_imported, papers_uploaded, keywords_extracted, avg_confidence_score)
    SELECT 
        target_date,
        COALESCE(SUM(CASE WHEN event_type = 'import' AND status = 'success' THEN 1 ELSE 0 END), 0),
        COALESCE(SUM(CASE WHEN event_type = 'paperless_upload' AND status = 'success' THEN 1 ELSE 0 END), 0),
        COALESCE(COUNT(DISTINCT ke.id), 0),
        COALESCE(AVG(ke.confidence_score), 0.0)
    FROM activity_events ae
    LEFT JOIN keyword_extractions ke ON ke.date = target_date
    WHERE ae.date = target_date
    ON CONFLICT (date) DO UPDATE SET
        papers_imported = EXCLUDED.papers_imported,
        papers_uploaded = EXCLUDED.papers_uploaded,
        keywords_extracted = EXCLUDED.keywords_extracted,
        avg_confidence_score = EXCLUDED.avg_confidence_score,
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;
