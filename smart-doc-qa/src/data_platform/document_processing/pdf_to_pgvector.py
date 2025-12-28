from sentence_transformers import SentenceTransformer
import pypdf
import psycopg2
import tiktoken
from typing import List

# Load model (downloads ~90MB first time)
model = SentenceTransformer('all-MiniLM-L6-v2')
enc = tiktoken.get_encoding("cl100k_base")

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
    conn = psycopg2.connect(dbname="postgres", user="karthikkumarthirugnanam", host="localhost")
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


# Run
if __name__ == "__main__":
    pdf_to_embeddings("5-beginner-ai-projects.pdf")
    
# Test search
print(search_documents("Summarize the document"))
