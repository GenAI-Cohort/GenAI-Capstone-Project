# src/data_platform/api/server.py

from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from src.data_platform.api.client import DataPlatformClient

app = FastAPI(title="Data Platform API for Agents")
client = DataPlatformClient()

class QueryRequest(BaseModel):
    query: str
    project_id: int
    top_k: int = 5
    min_similarity: float = 0.3
    priority_filter: Optional[List[str]] = None
    status_filter: Optional[List[str]] = None

class RetrievalResponse(BaseModel):
    chunks: List[dict]
    total_found: int

@app.post("/api/v1/retrieve/requirements", response_model=RetrievalResponse)
def retrieve_requirements(request: QueryRequest):
    """
    Vector search for requirements chunks.
    Used by RequirementsAgent.retrieve_requirements_by_query()
    """
    try:
        chunks = client.retrieve_requirements_by_query(
            query=request.query,
            project_id=request.project_id,
            top_k=request.top_k,
            min_similarity=request.min_similarity,
            priority_filter=request.priority_filter,
            status_filter=request.status_filter
        )
        return RetrievalResponse(chunks=chunks, total_found=len(chunks))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/requirements/{requirement_id}")
def get_requirement(requirement_id: str, project_id: int = Query(...)):
    """Get specific requirement by ID."""
    result = client.get_requirement_by_id(requirement_id, project_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Requirement {requirement_id} not found")
    return result

@app.get("/api/v1/requirements/gaps/without-design")
def find_gaps(
    project_id: int = Query(...),
    priority_filter: Optional[List[str]] = Query(None)
):
    """
    Find requirements without design documentation (gap analysis).
    Used by RequirementsAgent._handle_gap_analysis()
    """
    gaps = client.find_requirements_without_design(
        project_id=project_id,
        priority_filter=priority_filter
    )
    return {"gaps": gaps, "gap_count": len(gaps)}

@app.get("/api/v1/requirements/{requirement_id}/traceability")
def get_traceability(requirement_id: str, project_id: int = Query(...)):
    """
    Get full traceability chain for a requirement.
    Used by RequirementsAgent._handle_traceability_query()
    """
    trace_data = client.get_requirement_traceability(requirement_id, project_id)
    if not trace_data:
        raise HTTPException(status_code=404, detail=f"Requirement {requirement_id} not found")
    return trace_data

@app.get("/api/v1/requirements/ids")
def list_requirement_ids(
    project_id: int = Query(...),
    status_filter: Optional[List[str]] = Query(None)
):
    """Get all requirement IDs in project."""
    ids = client.get_all_requirement_ids(project_id, status_filter)
    return {"requirement_ids": ids, "total": len(ids)}

# Similar endpoints for other categories
@app.post("/api/v1/retrieve/business-rules")
def retrieve_business_rules(request: QueryRequest):
    """Vector search for business rules."""
    # Similar to requirements, but filter by category_id = 2
    pass

@app.post("/api/v1/retrieve/design-specs")
def retrieve_design_specs(request: QueryRequest):
    """Vector search for design specifications."""
    # Filter by category_id = 3
    pass

@app.post("/api/v1/retrieve/contracts")
def retrieve_contracts(request: QueryRequest):
    """Vector search for contracts."""
    # Filter by category_id = 5
    pass

# Generic retrieval endpoint for any category
@app.post("/api/v1/retrieve/by-category/{category_name}")
def retrieve_by_category(category_name: str, request: QueryRequest):
    """Generic vector search by category name."""
    pass
