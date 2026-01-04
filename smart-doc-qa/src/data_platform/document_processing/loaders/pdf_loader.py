# loaders/pdf_loader.py
from pypdf import PdfReader  # pip install pypdf

def load_pdf(path: str) -> str:
    reader = PdfReader(path)
    parts = []
    for page in reader.pages:
        text = page.extract_text() or ""
        parts.append(text)
    return "\n".join(parts)
