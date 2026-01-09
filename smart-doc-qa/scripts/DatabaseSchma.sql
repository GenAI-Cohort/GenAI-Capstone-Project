-- Categories/Document Types
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,  -- 'Requirements', 'Business Rules', etc.
    description TEXT,
    color VARCHAR(7),  -- for UI visualization
    icon VARCHAR(50),
    chunking_strategy JSONB,  -- store category-specific chunking config
    metadata_schema JSONB,  -- define required/optional metadata fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Projects/Workspaces (for team organization)
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    settings JSONB  -- project-specific configs
);

-- Enhanced Documents table with categorization
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    category_id INTEGER REFERENCES categories(id),
    filename VARCHAR(255) NOT NULL,
    file_hash VARCHAR(64) UNIQUE NOT NULL,
    file_size INTEGER,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    content text,
    -- Rich metadata
    metadata JSONB,  -- flexible metadata per document
    tags TEXT[],  -- array of tags for filtering
    version VARCHAR(50),  -- document version tracking
    author VARCHAR(100),
    
    -- Status tracking
    status VARCHAR(50) DEFAULT 'processing',  -- processing, indexed, failed
    processing_error TEXT,
    
    -- Full-text search
    search_vector tsvector,
    
    UNIQUE(project_id, filename, version)
);

-- Create full-text search index
CREATE INDEX documents_search_idx ON documents USING GIN(search_vector);
CREATE INDEX documents_tags_idx ON documents USING GIN(tags);
CREATE INDEX documents_category_idx ON documents(category_id);
CREATE INDEX documents_project_idx ON documents(project_id);

-- Enhanced Chunks table with category awareness
CREATE TABLE chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    category_id INTEGER REFERENCES categories(id),
    project_id INTEGER REFERENCES projects(id),
    
    -- Content
    chunk_text TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    chunk_type VARCHAR(50),  -- 'paragraph', 'table', 'code', 'list', 'heading'
    
    -- Location metadata
    page_number INTEGER,
    section_title TEXT,
    heading_hierarchy TEXT[],  -- ['Chapter 1', 'Section 1.1', 'Subsection 1.1.1']
    
    -- Vector embedding
    embedding vector(384),
    
    -- Category-specific metadata
    metadata JSONB,  -- e.g., requirement_id, priority, status for Requirements
    
    -- Search optimization
    search_vector tsvector,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Optimized indexes
CREATE INDEX chunks_embedding_idx ON chunks 
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

CREATE INDEX chunks_category_idx ON chunks(category_id);
CREATE INDEX chunks_project_idx ON chunks(project_id);
CREATE INDEX chunks_document_idx ON chunks(document_id);
CREATE INDEX chunks_search_idx ON chunks USING GIN(search_vector);
CREATE INDEX chunks_metadata_idx ON chunks USING GIN(metadata);

-- Category-specific metadata examples stored as JSONB
-- Requirements: {"requirement_id": "REQ-001", "priority": "high", "status": "approved"}
-- Business Rules: {"rule_id": "BR-023", "applies_to": "payment_processing"}
-- Contracts: {"contract_id": "CNT-2024-05", "party": "Acme Corp", "effective_date": "2024-01-01"}

-- Document relationships (for traceability)
CREATE TABLE document_relationships (
    id SERIAL PRIMARY KEY,
    source_document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    target_document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    relationship_type VARCHAR(50),  -- 'implements', 'references', 'supersedes', 'derived_from'
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_document_id, target_document_id, relationship_type)
);

-- Cross-references between chunks (requirement -> design -> code)
CREATE TABLE chunk_references (
    id SERIAL PRIMARY KEY,
    source_chunk_id INTEGER REFERENCES chunks(id) ON DELETE CASCADE,
    target_chunk_id INTEGER REFERENCES chunks(id) ON DELETE CASCADE,
    reference_type VARCHAR(50),  -- 'implements', 'satisfies', 'related_to'
    confidence_score FLOAT,  -- AI-detected reference confidence
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
