# loaders/__init__.py
from .pdf_loader import load_pdf
from .docx_loader import load_docx
from .markdown_loader import load_markdown
from .txt_loader import load_txt

EXTENSION_LOADERS = {
    ".pdf": load_pdf,
    ".docx": load_docx,
    ".md": load_markdown,
    ".txt": load_txt,
}
