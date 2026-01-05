from sentence_transformers import SentenceTransformer
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