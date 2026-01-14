from config.db_connection import get_connection

import datetime
from psycopg2.extras import RealDictCursor

def get_next_document_id():
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT nextval('public.document_id_seq');")
            row = cur.fetchone()
            return row[0]
        except Exception as e:
            print(f"Database error: {e}")
        finally:
            if conn:
                cur.close()
                conn.close()

def get_file_hash(file_path: str = None):
    import hashlib
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def get_file_size(file_path: str = None):
    import os
    return os.path.getsize(file_path)

def get_document_id_from_document(filename: str,file_path=None, project_id=None, category_id=None):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT id FROM public.documents WHERE filename = %s AND project_id = %s AND category_id = %s;", (filename, project_id, category_id))
            rows = cur.fetchall()
            for row in rows:
                print(row)
        except Exception as e:
            print(f"Database error: {e}")
        finally:
            if conn:
                cur.close()
                conn.close()
                
        if not rows:
            print(f"No document found with filename: {filename}")
            print("inserting document into documents table")
            document_already_exists = False
            return Insert_document_into_documents_table(filename,file_path,project_id, category_id),document_already_exists
        else:
            print(f"Document found with filename: {filename} already present in documents table")
            print("fetching document id")
            document_already_exists = True
            return row[0],document_already_exists  # Assuming filename is unique and returns a single id

def Insert_document_into_documents_table(filename: str, file_path: str = None, project_id=None, category_id=None):
    try:
        nextval = get_next_document_id()    
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO public.documents (
                id,
                project_id,
                category_id,
                filename,
                file_hash,
                file_size,
                upload_date,
                content,
                metadata,
                tags,
                version,
                author,
                status,
                processing_error,
                search_vector
            ) VALUES (
                %s, -- id
                %s, -- project_id
                %s, -- category_id
                %s, -- filename
                %s, -- file_hash
                %s, -- file_size
                %s, -- upload_date
                NULL,   -- content
                NULL,   -- metadata
                NULL,   -- tags
                NULL,   -- version
                NULL,   -- author
                'processing',  -- status
                NULL,   -- processing_error
                to_tsvector('english', %s) -- search_vector
            )
            """,
            (
                nextval,
                project_id,
                category_id,
                filename,
                get_file_hash(file_path),
                get_file_size(file_path),
                datetime.datetime.now(),
                filename  # for search_vector
            )
        )
        conn.commit()
        print(f"Inserted document with filename: {filename}")
    except Exception as e:
        print(f"Database error during insertion: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()
    return nextval  

def getdocument_by_id(document_id: int):
        try:
            conn = get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("SELECT * FROM public.documents WHERE id = %s;", (document_id,))
            row = cur.fetchone()
            return row
        except Exception as e:
            print(f"Database error: {e}")
            return None
        finally:
            if conn:
                cur.close()
                conn.close()
                