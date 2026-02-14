# src/data_platform/api/client.py

from src.data_platform.retrieval.vector_search import search_documents
from src.data_platform.storage import document_repo, chunk_repo
from psycopg2.extras import RealDictCursor
from config.db_connection import get_connection
from typing import List, Dict, Any, Optional

class DataPlatformClient:
    """
    Client for Workstream 2 agents to interact with Workstream 1 data platform.
    Replace the mock DataPlatformClient in requirements_agent.py with this.
    """
    
    def __init__(self, base_url: str = None):
        # base_url kept for compatibility but not used (direct DB access)
        pass
    
    def retrieve_requirements_by_query(
        self,
        query: str,
        project_id: int = 1,
        top_k: int = 5,
        min_similarity: float = 0.2,
        priority_filter: Optional[List[str]] = None,
        status_filter: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve requirements chunks using vector search.
        
        Returns: List of chunk dictionaries with metadata
        """
        # Get basic vector search results
        raw_results = search_documents(query, top_k=top_k * 2)  # Get more initially

        # Enhance results with full chunk metadata
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        results = []
        for filename, chunk_text, similarity in raw_results:
            print(f"Filename: {filename}")
            print(f"Similarity: {similarity}")
            if similarity < min_similarity:
                print(f"Similarity: {similarity} is less than min similarity: {min_similarity}")
                continue
                
            # Get chunk with all metadata
            cur.execute("""
                SELECT c.id, c.chunk_text, c.metadata, c.page_number,
                       c.section_title, c.heading_hierarchy,
                       d.filename, d.id as document_id,
                       cat.name as category_name
                FROM chunks c
                JOIN documents d ON c.document_id = d.id
                JOIN categories cat ON c.category_id = cat.id
                WHERE c.chunk_text = %s 
                  AND c.project_id = %s
                  AND cat.name = 'Requirements'
            """, (chunk_text, project_id))
            
            row = cur.fetchone()
            if row:
                # Apply filters
                metadata = row['metadata'] or {}
                
                if priority_filter and metadata.get('priority') not in priority_filter:
                    continue
                if status_filter and metadata.get('status') not in status_filter:
                    continue
                
                results.append({
                    'id': row['id'],
                    'chunk_text': row['chunk_text'],
                    'metadata': metadata,
                    'filename': row['filename'],
                    'page_number': row['page_number'],
                    'category_name': row['category_name'],
                    'similarity_score': similarity
                })
                
                if len(results) >= top_k:
                    break
        
        cur.close()
        conn.close()
        
        return results
    
    def get_requirement_by_id(
        self,
        requirement_id: str,
        project_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get specific requirement by ID from metadata.
        
        Args:
            requirement_id: e.g. "REQ-001"
            project_id: Project ID
            
        Returns: Chunk dict or None
        """
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT c.id, c.chunk_text, c.metadata, c.page_number,
                   d.filename, cat.name as category_name
            FROM chunks c
            JOIN documents d ON c.document_id = d.id
            JOIN categories cat ON c.category_id = cat.id
            WHERE c.metadata->>'requirement_id' = %s
              AND c.project_id = %s
              AND cat.name = 'Requirements'
        """, (requirement_id, project_id))
        
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        return dict(result) if result else None
    
    def find_requirements_without_design(
        self,
        project_id: int,
        priority_filter: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Find requirements that lack design documentation (gap analysis).
        
        Uses chunk_references table to detect missing links.
        """
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        priority_clause = ""
        params = [project_id]
        
        if priority_filter:
            priority_clause = "AND c.metadata->>'priority' = ANY(%s)"
            params.append(priority_filter)
        
        cur.execute(f"""
            SELECT c.id, c.chunk_text, c.metadata, d.filename
            FROM chunks c
            JOIN documents d ON c.document_id = d.id
            JOIN categories cat ON c.category_id = cat.id
            WHERE cat.name = 'Requirements'
              AND c.project_id = %s
              {priority_clause}
              AND NOT EXISTS (
                  SELECT 1 FROM chunk_references cr
                  JOIN chunks target ON cr.target_chunk_id = target.id
                  JOIN categories target_cat ON target.category_id = target_cat.id
                  WHERE cr.source_chunk_id = c.id
                    AND target_cat.name = 'Design Specifications'
                    AND cr.reference_type = 'implements'
              )
        """, params)
        
        results = cur.fetchall()
        cur.close()
        conn.close()
        
        return [dict(r) for r in results]
    
    def get_requirement_traceability(
        self,
        requirement_id: str,
        project_id: int
    ) -> Dict[str, Any]:
        """
        Get full traceability chain for a requirement.
        
        Returns:
            {
                'requirement': {...},
                'design_links': [...],
                'tech_spec_links': [...]
            }
        """
        # Get the requirement
        requirement = self.get_requirement_by_id(requirement_id, project_id)
        
        if not requirement:
            return {}
        
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get design links
        cur.execute("""
            SELECT target.id, target.chunk_text, target.metadata,
                   d.filename, cr.confidence_score,
                   target.metadata->>'component_name' as component_name
            FROM chunk_references cr
            JOIN chunks target ON cr.target_chunk_id = target.id
            JOIN documents d ON target.document_id = d.id
            JOIN categories cat ON target.category_id = cat.id
            WHERE cr.source_chunk_id = %s
              AND cat.name = 'Design Specifications'
              AND cr.reference_type = 'implements'
        """, (requirement['id'],))
        
        design_links = [dict(r) for r in cur.fetchall()]
        
        # Get tech spec links
        cur.execute("""
            SELECT target.id, target.chunk_text, target.metadata,
                   d.filename, cr.confidence_score
            FROM chunk_references cr
            JOIN chunks target ON cr.target_chunk_id = target.id
            JOIN documents d ON target.document_id = d.id
            JOIN categories cat ON target.category_id = cat.id
            WHERE cr.source_chunk_id = %s
              AND cat.name IN ('Technical Specifications', 'User Manuals')
        """, (requirement['id'],))
        
        tech_spec_links = [dict(r) for r in cur.fetchall()]
        
        cur.close()
        conn.close()
        
        return {
            'requirement': requirement,
            'design_links': design_links,
            'tech_spec_links': tech_spec_links
        }
    
    def get_all_requirement_ids(
        self,
        project_id: int,
        status_filter: Optional[List[str]] = None
    ) -> List[str]:
        """Get all requirement IDs in project."""
        conn = get_connection()
        cur = conn.cursor()
        
        status_clause = ""
        params = [project_id]
        
        if status_filter:
            status_clause = "AND c.metadata->>'status' = ANY(%s)"
            params.append(status_filter)
        
        cur.execute(f"""
            SELECT DISTINCT c.metadata->>'requirement_id'
            FROM chunks c
            JOIN categories cat ON c.category_id = cat.id
            WHERE cat.name = 'Requirements'
              AND c.project_id = %s
              AND c.metadata->>'requirement_id' IS NOT NULL
              {status_clause}
        """, params)
        
        ids = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        
        return ids
        
    def retrieve_by_category(
        self,
        category_name: str,
        query: str,
        project_id: int,
        top_k: int = 5,
        **filters
    ) -> List[Dict[str, Any]]:
        """
        Generic retrieval for any category.
        
        Args:
            category_name: 'Requirements', 'Business Rules', 'Design Specifications', etc.
            query: Search query
            project_id: Project ID
            top_k: Number of results
            **filters: Category-specific filters (e.g., priority, status)
        """
        raw_results = search_documents(query, top_k=top_k * 2)
        
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        results = []
        for filename, chunk_text, similarity in raw_results:
            cur.execute("""
                SELECT c.id, c.chunk_text, c.metadata, c.page_number,
                       d.filename, cat.name as category_name
                FROM chunks c
                JOIN documents d ON c.document_id = d.id
                JOIN categories cat ON c.category_id = cat.id
                WHERE c.chunk_text = %s 
                  AND c.project_id = %s
                  AND cat.name = %s
            """, (chunk_text, project_id, category_name))
            
            row = cur.fetchone()
            if row:
                # Apply dynamic filters
                metadata = row['metadata'] or {}
                
                # Filter based on **filters kwargs
                if filters:
                    should_include = True
                    for key, expected_values in filters.items():
                        if expected_values and metadata.get(key) not in expected_values:
                            should_include = False
                            break
                    
                    if not should_include:
                        continue
                
                results.append({
                    'id': row['id'],
                    'chunk_text': row['chunk_text'],
                    'metadata': metadata,
                    'filename': row['filename'],
                    'page_number': row['page_number'],
                    'category_name': row['category_name'],
                    'similarity_score': similarity
                })
                
                if len(results) >= top_k:
                    break
        
        cur.close()
        conn.close()
        
        return results
