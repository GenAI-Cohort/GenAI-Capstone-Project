from sentence_transformers import SentenceTransformer
import psycopg2
from config.db_connection import get_connection
# Load model (downloads ~90MB first time)
model = SentenceTransformer('all-MiniLM-L6-v2')

def search_documents(query: str, top_k: int = 5):
    query_embedding = model.encode([query], normalize_embeddings=True)[0].tolist()

    conn=get_connection()
    cur = conn.cursor()
    params = {
        'query': query,
        'query_embedding': query_embedding,
        'category_id': 1,
        'project_id': 1,
        'priority': None,
        'status': None,
        'top_k': top_k,
        'min_similarity': 0.2
    }

    cur.execute(
"""
WITH vector_search AS (
    SELECT c.id
         , c.chunk_text
         , c.chunk_index
         , c.page_number
         , c.section_title
         , c.document_id
         , d.filename
         , cat.id as category_id
         , cat.name as category_name
         , c.metadata
         , 1 - (c.embedding <=> %(query_embedding)s::vector) AS similarity_score
    FROM chunks c
    JOIN documents d ON c.document_id = d.id
    JOIN categories cat ON c.category_id = cat.id
    WHERE c.category_id = %(category_id)s
      AND c.project_id = %(project_id)s
      AND (%(priority)s IS NULL OR c.metadata->>'priority' = ANY(%(priority)s))
      AND (%(status)s IS NULL OR c.metadata->>'status' = ANY(%(status)s))
    ORDER BY c.embedding <=> %(query_embedding)s::vector
    LIMIT %(top_k)s * 2
),
keyword_search AS (
    SELECT c.id
         , ts_rank(c.search_vector, plainto_tsquery('english', %(query)s)) AS keyword_score
    FROM chunks c
    WHERE c.category_id = %(category_id)s
        AND c.project_id = %(project_id)s
        AND c.search_vector @@ plainto_tsquery('english', %(query)s)
    LIMIT %(top_k)s * 2
)
SELECT DISTINCT
    vs.filename,
    vs.chunk_text,
    COALESCE(vs.similarity_score, 0) * 0.7 + COALESCE(ks.keyword_score, 0) * 0.3 AS combined_score
FROM vector_search vs
LEFT JOIN keyword_search ks ON vs.id = ks.id
WHERE vs.similarity_score >= %(min_similarity)s OR ks.keyword_score > 0
ORDER BY combined_score DESC
LIMIT %(top_k)s
""",
params,)
    
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results

def search_documents_deprecated(query: str, top_k: int = 5):
    query_emb = model.encode([query], normalize_embeddings=True)[0].tolist()
    
    ##conn = psycopg2.connect(dbname="postgres", user="karthikkumarthirugnanam", host="localhost")
    conn=get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT filename, chunk, 1 - (embedding <=> %s::vector) AS similarity
        FROM documents_1 ORDER BY embedding <=> %s::vector LIMIT %s
    """, (query_emb, query_emb, top_k))
    
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results
