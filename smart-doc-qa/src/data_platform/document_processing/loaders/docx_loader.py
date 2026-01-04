# loaders/docx_loader.py
from docx import Document  # pip install python-docx

def load_docx(path: str) -> str:
    doc = Document(path)
    paragraphs = [p.text for p in doc.paragraphs if p.text]
    return "\n".join(paragraphs)
