-- ATROZ Dashboard Database Schema
-- Optimized for read-heavy analytical queries

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Reference Tables (Metadata)

CREATE TABLE IF NOT EXISTS pdet_subregions (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    department_list TEXT[]
);

CREATE TABLE IF NOT EXISTS policy_areas (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    dimension_id TEXT
);

CREATE TABLE IF NOT EXISTS dimensions (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL
);

-- 2. Core Entity: Regions (Municipalities)

CREATE TABLE IF NOT EXISTS regions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dane_code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    subregion_id TEXT, -- Can reference pdet_subregions
    population INTEGER,
    area_km2 FLOAT,
    latitude FLOAT,
    longitude FLOAT,

    -- Metadata from Pipeline
    latest_job_id TEXT,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Macro Scores (denormalized for performance)
    macro_score FLOAT,
    macro_band TEXT,
    macro_coherence FLOAT,
    macro_alignment FLOAT
);

-- 3. Meso Level: Cluster Scores

CREATE TABLE IF NOT EXISTS cluster_scores (
    region_id UUID REFERENCES regions(id),
    cluster_id TEXT NOT NULL,
    score FLOAT,
    score_percent FLOAT,
    trend FLOAT,
    weakest_area TEXT,
    PRIMARY KEY (region_id, cluster_id)
);

-- 4. Micro Level: Question Scores

CREATE TABLE IF NOT EXISTS question_scores (
    region_id UUID REFERENCES regions(id),
    question_id TEXT NOT NULL,
    score FLOAT,
    score_percent FLOAT,
    evidence_count INTEGER DEFAULT 0,
    PRIMARY KEY (region_id, question_id)
);

-- 5. Evidence / Answers (The 51K Dataset)

CREATE TABLE IF NOT EXISTS answers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    region_id UUID REFERENCES regions(id),
    question_id TEXT NOT NULL,
    text TEXT, -- Extracted text or summary
    source_document TEXT,
    page_number INTEGER,
    relevance_score FLOAT,
    timestamp TIMESTAMP WITH TIME ZONE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_regions_subregion ON regions(subregion_id);
CREATE INDEX IF NOT EXISTS idx_question_scores_region ON question_scores(region_id);
CREATE INDEX IF NOT EXISTS idx_answers_region ON answers(region_id);
CREATE INDEX IF NOT EXISTS idx_answers_question ON answers(question_id);
