import psycopg2 
from  ..document_processing.chunkers.base_chunker import chunk_text
from ..document_processing.chunkers import base_chunker
from config.db_connection import get_connection
from ..storage.chunk_repo import insert_chunk
from ..storage.document_repo import get_document_id_from_document

def text_to_embeddings(project_id: int, category_id: int, text: str, filename: str,file_path: str = None):

    print(f"Storing document metadata for {filename}...")
    document_id,document_already_exists = get_document_id_from_document(filename,file_path,project_id, category_id)
    if document_already_exists:
        print(f"Document {filename} already exists in the database. Skipping embedding generation.")
        return
    
    print(f"Processing text of length {len(text)}")
    
    # Chunk
    chunks = chunk_text(text)
    
    print(f"Chunked into {len(chunks)} chunks")
    if(len(chunks) == 0):
        print(f"No chunks generated for {filename}, skipping embedding generation.")
        return 
   

    print(f"Generating embeddings...")
    # Local embeddings (384D)
    embeddings = base_chunker.model.encode(chunks, normalize_embeddings=True).tolist()

    print(f"Generated embeddings for {len(chunks)} chunks")

    print(f"Storing embeddings in database...")
    for chunk, emb in zip(chunks, embeddings):
        insert_chunk(document_id, category_id, project_id, chunk, emb)
    print(f"✅ Stored {len(chunks)} chunks  from {filename}")


    
    

    