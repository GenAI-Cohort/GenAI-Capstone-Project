# directory_loader.py
import os
from . import EXTENSION_LOADERS
from src.data_platform.embeddings.local_embeddings import text_to_embeddings as Vectorize_text_to_pgvector
from src.data_platform.storage.project_repo import get_project_id_from_project
from src.data_platform.storage.category_repo import get_category_id_from_document_category

#get project_id, category_id
project_id = get_project_id_from_project("CapStone")
category_id = get_category_id_from_document_category("Requirements")
    
def Load_and_vectorize(root_dir: str):
    """
    root_dir: folder to scan
    vectorize_fn: function(path: str, content: str) -> None
    """
    for dirpath, _, filenames in os.walk(root_dir):
        for fname in filenames:
            print(f"Processing {fname}...") 
            path = os.path.join(dirpath, fname)
            ext = os.path.splitext(fname)[1].lower()
            loader = EXTENSION_LOADERS.get(ext)
            if not loader:
                continue  # skip unsupported files

            # loader returns raw text for this file
            print(f"Loading text from {path}...")  
            text = loader(path)
            Vectorize_text_to_pgvector(project_id, category_id, text, os.path.basename(path), path)
            print(f"Finished processing {fname}.")
            print("-" * 40)
            print()
    print("Done processing all files.")
    return
# Example usage:
# Load_and_vectorize("/path/to/your/documents") 
