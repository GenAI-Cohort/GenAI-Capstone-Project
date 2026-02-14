from ast import Import
from sentence_transformers import SentenceTransformer
import pypdf
import psycopg2
import tiktoken
from typing import List
from psycopg2.extras import RealDictCursor

# Load model (downloads ~90MB first time)
model = SentenceTransformer('all-MiniLM-L6-v2')
enc = tiktoken.get_encoding("cl100k_base")

# 2. Database connection parameters
conn_params = {
        "host": "localhost",
        "database": "GenAI-Capstone",
        "user": "postgres",
        "password": "Lenovo"
}

def chunk_text(text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
    tokens = enc.encode(text)
    chunks = []
    for i in range(0, len(tokens), chunk_size - overlap):
        chunk_tokens = tokens[i:i + chunk_size]
        chunks.append(enc.decode(chunk_tokens))
    return chunks

def pdf_to_embeddings(filename: str):
    # Read PDF
    reader = pypdf.PdfReader(filename)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    
    # Chunk
    chunks = chunk_text(text)
    
    # Local embeddings (384D)
    embeddings = model.encode(chunks, normalize_embeddings=True).tolist()
    
    # Store
    #conn = psycopg2.connect(dbname="postgres", user="karthikkumarthirugnanam", host="localhost")
#    conn = psycopg2.connect(dbname="GenAI-Capstone", user="postgres", password="Lenovo", host="localhost")
    conn = psycopg2.connect(dbname="postgres", user="balaji",  host="localhost")
    
    cur = conn.cursor()
    
    for chunk, emb in zip(chunks, embeddings):
        cur.execute(
            "INSERT INTO documents (filename, content, chunk, embedding) VALUES (%s, %s, %s, %s)",
            (filename, text, chunk, emb)
        )
    
    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ Stored {len(chunks)} chunks from {filename}")

def search_documents(query: str, top_k: int = 5):
    query_emb = model.encode([query], normalize_embeddings=True)[0].tolist()
    
    # conn = psycopg2.connect(dbname="postgres", user="karthikkumarthirugnanam", host="localhost")
    # conn = psycopg2.connect(dbname="GenAI-Capstone", user="postgres", password="Lenovo", host="localhost")
    conn = psycopg2.connect(dbname="postgres", user="balaji",  host="localhost")

    cur = conn.cursor()
    
    cur.execute("""
        SELECT filename, chunk, 1 - (embedding <=> %s::vector) AS similarity
        FROM documents ORDER BY embedding <=> %s::vector LIMIT %s
    """, (query_emb, query_emb, top_k))
    
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results
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
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # 3. Execute Search
        # We use 1 - (embedding <=> %s) to convert cosine distance to similarity
        sql = """
        SELECT id, filename, chunk, content, 1 - (embedding <=> %s::vector) AS similarity
        FROM documents
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
###############################################
# Example Usage
########################## Run###############################
if __name__ == "__main__":
    #pdf_to_embeddings("5-beginner-ai-projects.pdf")
    ####################################### ##################################
    # following line is used to convert pdf document into embeddings and store it into PGVector database
    pdf_to_embeddings("Synthetic Data Generation.pdf")
    
################################# Test search function ###############################
    ################################################################################
    ###Following search query is used to provide top k search results from the PGVector database 

#print(search_documents("Summarize the document"))
    search_list = search_documents("Summarize the document NLP and LLM", top_k=5)
    for item in search_list:
        print(f"Filename: {item[0]}\nChunk: {item[1]}\nSimilarity: {item[2]}\n")
        print("---------------**********************************************************************---------------")

########################################### Mohandar ##################################
###Following search query is used to provide similarity based search results from the PGVector database it will return top 3 results with minimum similarity of 0.5

    #search_query = "What is Synthetic Data sumarize synthetic data techniques?"
    search_query = "Summarize the document NLP and LLM"
    hits = search_pgvector(search_query, top_k=3, min_similarity=0.5)

    for row in hits:
        print(f"[{row['similarity']:.4f}] \nFileName {row['filename']}\nchunk: {row['chunk']}")
        print("---------------**********************************************************************---------------")