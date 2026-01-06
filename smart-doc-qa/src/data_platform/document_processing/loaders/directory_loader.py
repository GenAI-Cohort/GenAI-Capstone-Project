# directory_loader.py
import os
from . import EXTENSION_LOADERS
from src.data_platform.embeddings.local_embeddings import text_to_embeddings as Vectorize_text_to_pgvector

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
            Vectorize_text_to_pgvector(text,os.path.basename(path))
