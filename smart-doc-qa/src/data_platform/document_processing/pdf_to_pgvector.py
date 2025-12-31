from ast import Import
from sentence_transformers import SentenceTransformer
import pypdf
import psycopg2
import tiktoken
from typing import List
import sys
# Load model (downloads ~90MB first time)
model = SentenceTransformer('all-MiniLM-L6-v2')
enc = tiktoken.get_encoding("cl100k_base")
## creating connection to Postgres database
def connect_to_postgres():
    """ Connect to the PostgreSQL database server """
    connection = None
    try:
        # Define connection parameters
        params = {
            "host": "localhost",
            "database": "GenAI-Capstone",
            "user": "postgres",
            "password": "Lenovo"
        }
        
        # Connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        connection = psycopg2.connect(**params)
        
        # Create a cursor object
        cursor = connection.cursor()
        
        # Execute a simple query
        print('PostgreSQL database version:')
        cursor.execute('SELECT version()')
        
        # Fetch the result and print
        db_version = cursor.fetchone()
        print(db_version)
        
        # Close the cursor and connection (handled automatically by the finally block below in this structure)
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        sys.exit(1)
    finally:
        if connection is not None:
            connection.close()
            print('Database connection closed.')


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
    conn = psycopg2.connect(dbname="GenAI-Capstone", user="postgres", password="Lenovo", host="localhost")
   
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
    conn = psycopg2.connect(dbname="GenAI-Capstone", user="postgres", password="Lenovo", host="localhost")
   
    cur = conn.cursor()
    
    cur.execute("""
        SELECT filename, chunk, 1 - (embedding <=> %s::vector) AS similarity
        FROM documents ORDER BY embedding <=> %s::vector LIMIT %s
    """, (query_emb, query_emb, top_k))
    
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results


# Run
if __name__ == "__main__":
    pdf_to_embeddings("5-beginner-ai-projects.pdf")
    
# Test search
print(search_documents("Summarize the document",2))
