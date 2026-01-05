# loaders/txt_loader.py
from pathlib import Path

def load_txt(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")
