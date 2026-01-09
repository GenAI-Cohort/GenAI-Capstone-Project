
from config.db_connection import get_connection
from sentence_transformers import SentenceTransformer
import psycopg2
from typing import List
import tiktoken
from psycopg2.extras import RealDictCursor

# Load model (downloads ~90MB first time)
model = SentenceTransformer('all-MiniLM-L6-v2')
enc = tiktoken.get_encoding("cl100k_base")
#################################Search Function###############################
# How it WorksEmbedding Model: You cannot search a string directly against a vector column. 
# The SentenceTransformer encodes your text into a numerical array that matches the dimensions stored in your database.
# The Operator <=>: This is the pgvector operator for cosine distance.
# Similarity Logic: Since distance is the opposite of similarity, we calculate it as:$$\text{Similarity} = 1 - \text{Cosine Distance}
# Type Casting: The ::vector cast ensures PostgreSQL treats your Python list as the correct vector type.
###############################################################################################################
def search_pgvector(query_string, top_k=5, min_similarity=0.7):
    # 1. Load a local embedding model
    # This converts your string into a 384-dimensional vector
   # model = SentenceTransformer('all-MiniLM-L6-v2')
    query_vector = model.encode(query_string).tolist()

   
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # 3. Execute Search
        # We use 1 - (embedding <=> %s) to convert cosine distance to similarity
        sql = """
        SELECT id, filename, chunk, content, 1 - (embedding <=> %s::vector) AS similarity
        FROM documents_1
        WHERE 1 - (embedding <=> %s::vector) >= %s
        ORDER BY similarity DESC
        LIMIT %s;
        """
        
        cur.execute(sql, (query_vector, query_vector, min_similarity, top_k))
        results = cur.fetchall()
        return results

    except Exception as e:
        print(f"Database error: {e}")
        return []
    finally:
        if conn:
            cur.close()
            conn.close()