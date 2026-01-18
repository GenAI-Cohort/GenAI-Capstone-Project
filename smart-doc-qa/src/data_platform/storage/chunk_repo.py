from config.db_connection import get_connection
    

def get_next_chunk_index():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COALESCE(MAX(chunk_index), 0) + 1 FROM public.chunks;")
        row = cur.fetchone()
        return row[0]
    except Exception as e:
        print(f"Database error: {e}")
        return 0
    finally:
        if conn:
            cur.close()
            conn.close()
            
def get_next_chunk_id():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT nextval('public.chunk_id_seq');")
        row = cur.fetchone()
        return row[0]
    except Exception as e:
        print(f"Database error: {e}")
        return 0
    finally:
        if conn:
            cur.close()
            conn.close()

def insert_chunk(document_id: int, category_id: int, project_id: int, chunk: str, emb: list):
    chunk_index = get_next_chunk_index()
    chunk_id = get_next_chunk_id()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO public.chunks (
            id,
            document_id,
            category_id,
            project_id,
            chunk_text,
            chunk_index,
            chunk_type,
            page_number,
            section_title,
            heading_hierarchy,
            embedding,
            metadata,
            search_vector,
            created_at
        ) VALUES (
            %s,  -- id
            %s,  -- document_id
            %s,  -- category_id
            %s,  -- project_id
            %s,  -- chunk_text
            %s,  -- chunk_index
            %s,  -- chunk_type
            %s,  -- page_number
            %s,  -- section_title
            %s,  -- heading_hierarchy
            %s,  -- embedding (pgvector)
            %s,  -- metadata (jsonb)
            to_tsvector('english', %s), -- search_vector
            now()  -- created_at
        )
        """,
        (
            chunk_id,                    # id
            document_id,                # document_id (example)
            category_id,                 # category_id (example)
            project_id,                  # project_id (example)
            chunk,                       # chunk_text
            chunk_index,                 # chunk_index (example, you may want to enumerate)
            'body',                      # chunk_type (example)
            1,                           # page_number (example)
            'Introduction',              # section_title (example)
            ['Introduction', 'Overview'], # heading_hierarchy (example)
            emb,                         # embedding
           # '{"source": "pdf", "lang": "en"}',  # metadata (example)
            '{"requirement_id": "REQ-chunk_id", "priority": "high", "status": "approved", "section": "Introduction", "dependencies": []}',
            chunk                        # search_vector source text
        )
    )
    conn.commit()
    cur.close()
    conn.close()
