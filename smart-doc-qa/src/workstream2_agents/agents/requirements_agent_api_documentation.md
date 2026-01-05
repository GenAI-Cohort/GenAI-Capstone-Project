# Requirements Agent - API Integration Documentation

## Overview

This document defines the interface between the Requirements Agent (Workstream 2) and the Data Platform (Workstream 1). Follow these specifications to ensure seamless integration.

---

## Data Models

### 1. Chunk Retrieval Response

The Requirements Agent expects chunks in this format from Workstream 1:

```python
{
    "id": int,                          # Unique chunk ID
    "chunk_text": str,                  # The actual text content
    "chunk_index": int,                 # Position in original document
    "page_number": int | None,          # Page number (if applicable)
    "section_title": str | None,        # Section heading
    "document_id": int,                 # Parent document ID
    "filename": str,                    # Original document filename
    "category_id": int,                 # Category ID (should be Requirements category)
    "category_name": str,               # "Requirements"
    "metadata": {                       # Requirements-specific metadata
        "requirement_id": str | None,   # e.g., "REQ-001", "REQ-045"
        "priority": str | None,         # "high", "medium", "low"
        "status": str | None,           # "draft", "approved", "implemented", "deprecated"
        "section": str | None,          # Section name in document
        "dependencies": list[str]       # List of related REQ-IDs
    },
    "similarity_score": float,          # Cosine similarity score (0.0-1.0)
    "combined_score": float            # Hybrid search score if applicable
}
```

### 2. Related Chunks (Traceability)

For traceability queries, include related chunks:

```python
{
    "chunk_id": int,
    "related_chunks": [
        {
            "id": int,
            "chunk_text": str,
            "category_name": str,       # e.g., "Design Documents", "Tech Specs"
            "filename": str,
            "reference_type": str,      # "implements", "satisfies", "related_to"
            "confidence_score": float   # AI-detected relationship confidence
        }
    ]
}
```

---

## Required Database Functions

### Function 1: `retrieve_requirements_by_query()`

**Purpose:** Retrieve relevant requirement chunks based on semantic search

**Signature:**

```python
def retrieve_requirements_by_query(
    query: str,
    project_id: int,
    top_k: int = 5,
    min_similarity: float = 0.3,
    priority_filter: list[str] | None = None,
    status_filter: list[str] | None = None
) -> list[dict]:
    """
    Retrieve requirement chunks using hybrid search (vector + keyword).
    
    Args:
        query: User's search query
        project_id: Project ID to filter
        top_k: Number of results to return
        min_similarity: Minimum similarity threshold
        priority_filter: Optional list of priorities ["high", "medium", "low"]
        status_filter: Optional list of statuses ["draft", "approved", etc.]
    
    Returns:
        List of chunk dictionaries (see Data Model above)
    """
```

**SQL Implementation Reference:**

```sql
WITH vector_search AS (
    SELECT 
        c.id,
        c.chunk_text,
        c.metadata,
        c.document_id,
        c.page_number,
        c.section_title,
        d.filename,
        cat.name as category_name,
        1 - (c.embedding <=> :query_embedding::vector) AS similarity_score
    FROM chunks c
    JOIN documents d ON c.document_id = d.id
    JOIN categories cat ON c.category_id = cat.id
    WHERE c.category_id = :requirements_category_id
        AND c.project_id = :project_id
        AND (:priority_filter IS NULL OR c.metadata->>'priority' = ANY(:priority_filter))
        AND (:status_filter IS NULL OR c.metadata->>'status' = ANY(:status_filter))
    ORDER BY c.embedding <=> :query_embedding::vector
    LIMIT :top_k * 2
),
keyword_search AS (
    SELECT 
        c.id,
        ts_rank(c.search_vector, plainto_tsquery('english', :query)) AS keyword_score
    FROM chunks c
    WHERE c.category_id = :requirements_category_id
        AND c.project_id = :project_id
        AND c.search_vector @@ plainto_tsquery('english', :query)
    LIMIT :top_k * 2
)
SELECT DISTINCT
    vs.*,
    COALESCE(vs.similarity_score, 0) * 0.7 + 
    COALESCE(ks.keyword_score, 0) * 0.3 AS combined_score
FROM vector_search vs
LEFT JOIN keyword_search ks ON vs.id = ks.id
WHERE vs.similarity_score >= :min_similarity OR ks.keyword_score > 0
ORDER BY combined_score DESC
LIMIT :top_k;
```

---

### Function 2: `get_requirement_by_id()`

**Purpose:** Retrieve a specific requirement by its REQ-ID

**Signature:**

```python
def get_requirement_by_id(
    requirement_id: str,
    project_id: int
) -> dict | None:
    """
    Get a specific requirement by its ID (e.g., "REQ-045").
    
    Args:
        requirement_id: Requirement identifier (e.g., "REQ-001")
        project_id: Project ID
    
    Returns:
        Chunk dictionary or None if not found
    """
```

**SQL Implementation:**

```sql
SELECT 
    c.id,
    c.chunk_text,
    c.metadata,
    c.document_id,
    c.page_number,
    c.section_title,
    d.filename,
    cat.name as category_name
FROM chunks c
JOIN documents d ON c.document_id = d.id
JOIN categories cat ON c.category_id = cat.id
WHERE c.metadata->>'requirement_id' = :requirement_id
    AND c.project_id = :project_id
    AND cat.name = 'Requirements'
LIMIT 1;
```

---

### Function 3: `find_requirements_without_design()`

**Purpose:** Gap analysis - find requirements lacking design documentation

**Signature:**

```python
def find_requirements_without_design(
    project_id: int,
    priority_filter: list[str] | None = None
) -> list[dict]:
    """
    Find requirements that don't have associated design documentation.
    
    Args:
        project_id: Project ID
        priority_filter: Optional priority filter
    
    Returns:
        List of requirements with gap information:
        [{
            "requirement_id": "REQ-001",
            "chunk_text": "Requirement text...",
            "priority": "high",
            "status": "approved",
            "has_design": False,
            "filename": "requirements.pdf"
        }]
    """
```

**SQL Implementation:**

```sql
WITH requirements AS (
    SELECT 
        c.id,
        c.metadata->>'requirement_id' as req_id,
        c.chunk_text,
        c.metadata->>'priority' as priority,
        c.metadata->>'status' as status,
        d.filename
    FROM chunks c
    JOIN documents d ON c.document_id = d.id
    JOIN categories cat ON c.category_id = cat.id
    WHERE cat.name = 'Requirements'
        AND c.project_id = :project_id
        AND c.metadata->>'requirement_id' IS NOT NULL
        AND c.metadata->>'status' != 'deprecated'
        AND (:priority_filter IS NULL OR c.metadata->>'priority' = ANY(:priority_filter))
),
has_design AS (
    SELECT DISTINCT r.req_id
    FROM requirements r
    JOIN chunk_references cr ON r.id = cr.source_chunk_id
    JOIN chunks dc ON cr.target_chunk_id = dc.id
    JOIN categories cat ON dc.category_id = cat.id
    WHERE cat.name IN ('Design Documents', 'Tech Specs')
        AND cr.confidence_score > 0.7
)
SELECT 
    r.req_id as requirement_id,
    r.chunk_text,
    r.priority,
    r.status,
    FALSE as has_design,
    r.filename
FROM requirements r
WHERE r.req_id NOT IN (SELECT req_id FROM has_design)
ORDER BY 
    CASE r.priority
        WHEN 'high' THEN 1
        WHEN 'medium' THEN 2
        WHEN 'low' THEN 3
        ELSE 4
    END;
```

---

### Function 4: `get_requirement_traceability()`

**Purpose:** Get complete traceability for a requirement (REQ → Design → Tech Specs)

**Signature:**

```python
def get_requirement_traceability(
    requirement_id: str,
    project_id: int
) -> dict:
    """
    Get traceability chain for a requirement.
    
    Args:
        requirement_id: Requirement ID (e.g., "REQ-045")
        project_id: Project ID
    
    Returns:
        {
            "requirement": {
                "id": "REQ-045",
                "text": "...",
                "priority": "high",
                "status": "approved"
            },
            "design_links": [
                {
                    "chunk_id": 123,
                    "chunk_text": "Design specification...",
                    "filename": "design.pdf",
                    "component_name": "AuthService",
                    "confidence": 0.85
                }
            ],
            "tech_spec_links": [
                {
                    "chunk_id": 456,
                    "chunk_text": "API specification...",
                    "filename": "api_spec.pdf",
                    "api_endpoint": "/api/auth/login",
                    "confidence": 0.9
                }
            ]
        }
    """
```

**SQL Implementation:**

```sql
WITH requirement_chunk AS (
    SELECT c.id, c.chunk_text, c.metadata
    FROM chunks c
    JOIN categories cat ON c.category_id = cat.id
    WHERE cat.name = 'Requirements'
        AND c.metadata->>'requirement_id' = :requirement_id
        AND c.project_id = :project_id
    LIMIT 1
),
design_links AS (
    SELECT 
        dc.id as chunk_id,
        dc.chunk_text,
        d.filename,
        dc.metadata->>'component_name' as component_name,
        cr.confidence_score
    FROM requirement_chunk rc
    JOIN chunk_references cr ON rc.id = cr.source_chunk_id
    JOIN chunks dc ON cr.target_chunk_id = dc.id
    JOIN documents d ON dc.document_id = d.id
    JOIN categories cat ON dc.category_id = cat.id
    WHERE cat.name = 'Design Documents'
        AND cr.confidence_score > 0.7
    ORDER BY cr.confidence_score DESC
),
tech_spec_links AS (
    SELECT 
        tc.id as chunk_id,
        tc.chunk_text,
        d.filename,
        tc.metadata->>'api_endpoint' as api_endpoint,
        cr.confidence_score
    FROM requirement_chunk rc
    JOIN chunk_references cr ON rc.id = cr.source_chunk_id
    JOIN chunks tc ON cr.target_chunk_id = tc.id
    JOIN documents d ON tc.document_id = d.id
    JOIN categories cat ON tc.category_id = cat.id
    WHERE cat.name = 'Tech Specs'
        AND cr.confidence_score > 0.7
    ORDER BY cr.confidence_score DESC
)
SELECT 
    (SELECT json_build_object(
        'id', rc.metadata->>'requirement_id',
        'text', rc.chunk_text,
        'priority', rc.metadata->>'priority',
        'status', rc.metadata->>'status'
    ) FROM requirement_chunk rc) as requirement,
    
    (SELECT json_agg(
        json_build_object(
            'chunk_id', chunk_id,
            'chunk_text', chunk_text,
            'filename', filename,
            'component_name', component_name,
            'confidence', confidence_score
        )
    ) FROM design_links) as design_links,
    
    (SELECT json_agg(
        json_build_object(
            'chunk_id', chunk_id,
            'chunk_text', chunk_text,
            'filename', filename,
            'api_endpoint', api_endpoint,
            'confidence', confidence_score
        )
    ) FROM tech_spec_links) as tech_spec_links;
```

---

### Function 5: `get_all_requirement_ids()`

**Purpose:** Get list of all requirement IDs in a project

**Signature:**

```python
def get_all_requirement_ids(
    project_id: int,
    status_filter: list[str] | None = None
) -> list[str]:
    """
    Get all requirement IDs in a project.
    
    Args:
        project_id: Project ID
        status_filter: Optional status filter
    
    Returns:
        List of requirement IDs: ["REQ-001", "REQ-002", ...]
    """
```

**SQL Implementation:**

```sql
SELECT DISTINCT c.metadata->>'requirement_id' as req_id
FROM chunks c
JOIN categories cat ON c.category_id = cat.id
WHERE cat.name = 'Requirements'
    AND c.project_id = :project_id
    AND c.metadata->>'requirement_id' IS NOT NULL
    AND (:status_filter IS NULL OR c.metadata->>'status' = ANY(:status_filter))
ORDER BY req_id;
```

---

## Integration Testing Checklist

### ✅ Workstream 1 Implementation Checklist

Before integrating with Requirements Agent, verify:

- [ ] Requirements category exists in `categories` table with ID
- [ ] Document processor extracts REQ-IDs correctly (regex: `REQ-\d+`)
- [ ] Metadata schema includes: `requirement_id`, `priority`, `status`, `dependencies`
- [ ] Vector embeddings are 384 dimensions (for all-MiniLM-L6-v2)
- [ ] IVFFlat index created on embeddings column
- [ ] Full-text search index created on `search_vector` column
- [ ] Chunk references table populated for traceability
- [ ] All 5 functions above implemented and tested
- [ ] Sample requirements documents processed and indexed

### ✅ Integration Test Cases

#### **Test 1: Basic Retrieval**

```python
# Query: "What are the authentication requirements?"
# Expected: Return 5 chunks with REQ-IDs related to authentication
# Verify: similarity_score > 0.3, metadata contains requirement_id

results = retrieve_requirements_by_query(
    query="authentication requirements",
    project_id=1,
    top_k=5
)
assert len(results) > 0
assert results[0]['metadata']['requirement_id'].startswith('REQ-')
```

#### **Test 2: Specific Requirement Lookup**

```python
# Query: Get requirement REQ-045
# Expected: Return exact requirement chunk

result = get_requirement_by_id("REQ-045", project_id=1)
assert result is not None
assert result['metadata']['requirement_id'] == "REQ-045"
```

#### **Test 3: Gap Analysis**

```python
# Query: Find high-priority requirements without design
# Expected: Return list with has_design=False

gaps = find_requirements_without_design(
    project_id=1,
    priority_filter=["high"]
)
assert all(gap['has_design'] == False for gap in gaps)
assert all(gap['priority'] == 'high' for gap in gaps)
```

#### **Test 4: Traceability**

```python
# Query: Get traceability for REQ-045
# Expected: Return requirement + design links + tech spec links

trace = get_requirement_traceability("REQ-045", project_id=1)
assert trace['requirement']['id'] == "REQ-045"
assert 'design_links' in trace
assert 'tech_spec_links' in trace
```

#### **Test 5: Priority Filtering**

```python
# Query: Get only high-priority requirements
# Expected: All results have priority="high"

results = retrieve_requirements_by_query(
    query="system requirements",
    project_id=1,
    priority_filter=["high"]
)
assert all(r['metadata']['priority'] == 'high' for r in results)
```

---

## Error Handling

### Expected Errors to Handle

Workstream 1 should raise clear exceptions:

```python
class RequirementNotFoundError(Exception):
    """Raised when requirement ID doesn't exist"""
    pass

class InvalidProjectError(Exception):
    """Raised when project_id doesn't exist"""
    pass

class EmbeddingGenerationError(Exception):
    """Raised when embedding generation fails"""
    pass

class DatabaseConnectionError(Exception):
    """Raised when database is unavailable"""
    pass
```

Requirements Agent will catch these and respond appropriately.

---

## Performance Requirements

### Response Time Targets

- `retrieve_requirements_by_query()`: < 500ms
- `get_requirement_by_id()`: < 50ms
- `find_requirements_without_design()`: < 1000ms
- `get_requirement_traceability()`: < 800ms
- `get_all_requirement_ids()`: < 100ms

### Optimization Tips

1. Use indexes on `metadata->>'requirement_id'`
2. Cache frequent queries (e.g., all requirement IDs)
3. Use EXPLAIN ANALYZE to optimize queries
4. Batch embed multiple queries if possible

---

## Sample Data for Testing

### Sample Requirement Document Content

```text
1. AUTHENTICATION REQUIREMENTS

REQ-001 (Priority: High, Status: Approved)
The system SHALL support multi-factor authentication for all users.

REQ-002 (Priority: Medium, Status: Draft)
The system SHALL allow password reset via email verification.

2. AUTHORIZATION REQUIREMENTS

REQ-045 (Priority: High, Status: Approved)
The system SHALL implement role-based access control (RBAC) with at least 
three roles: Admin, Manager, and User.

REQ-046 (Priority: Low, Status: Deprecated)
The system SHALL support legacy authentication protocols.
```

### Expected Metadata Extraction

```json
[
    {
        "requirement_id": "REQ-001",
        "priority": "high",
        "status": "approved",
        "section": "Authentication Requirements",
        "dependencies": []
    },
    {
        "requirement_id": "REQ-002",
        "priority": "medium",
        "status": "draft",
        "section": "Authentication Requirements",
        "dependencies": []
    },
    {
        "requirement_id": "REQ-045",
        "priority": "high",
        "status": "approved",
        "section": "Authorization Requirements",
        "dependencies": []
    }
]
```

---

## Contact & Support

**Questions?** Reach out to Workstream 2 team:

- Slack: #workstream-2-agents
- GitHub Issues: Tag with `integration` label
- Integration Lead: [Your Name]

**API Version:** 1.0  
**Last Updated:** [Current Date]
