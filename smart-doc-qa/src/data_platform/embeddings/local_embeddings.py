import psycopg2 
from  ..document_processing.chunkers.base_chunker import chunk_text
from ..document_processing.chunkers import base_chunker
from config.db_connection import get_connection
def text_to_embeddings(text: str, filename: str):
    
    print(f"Processing text of length {len(text)}")
    
    # Chunk
    chunks = chunk_text(text)
    
    print(f"Chunked into {len(chunks)} chunks")
    
    print(f"Generating embeddings...")
    # Local embeddings (384D)
    embeddings = base_chunker.model.encode(chunks, normalize_embeddings=True).tolist()

    print(f"Generated embeddings for {len(chunks)} chunks")
    print(f"Storing embeddings in database...")
    # Store
    ##conn = psycopg2.connect(dbname="postgres", user="karthikkumarthirugnanam", host="localhost")
    conn = get_connection() #psycopg2.connect(**conn_params)
    cur = conn.cursor()
    
    for chunk, emb in zip(chunks, embeddings):
        cur.execute(
            # "INSERT INTO documents_1 (filename, content, chunk, embedding) VALUES (%s, %s, %s, %s)",
            # (filename, text, chunk, emb)
            "INSERT INTO documents_1 (filename, content, chunk, embedding) VALUES (%s, %s, %s, %s)",
            (filename, text, chunk, emb)
        )
    
    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ Stored {len(chunks)} chunks  from {filename}")