from sentence_transformers import SentenceTransformer
import psycopg2

# Load model (downloads ~90MB first time)
model = SentenceTransformer('all-MiniLM-L6-v2')

def search_documents(query: str, top_k: int = 5):
    query_emb = model.encode([query], normalize_embeddings=True)[0].tolist()
    
    conn = psycopg2.connect(dbname="postgres", user="karthikkumarthirugnanam", host="localhost")
    cur = conn.cursor()
    
    cur.execute("""
        SELECT filename, chunk, 1 - (embedding <=> %s::vector) AS similarity
        FROM documents ORDER BY embedding <=> %s::vector LIMIT %s
    """, (query_emb, query_emb, top_k))
    
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results