"""
Data Platform Module

This module provides document processing, embedding, storage, and retrieval capabilities
for the Smart Document QA system.

To use this module, ensure you're running from the project root (smart-doc-qa/) or
have the project root in your PYTHONPATH.
"""

import sys
from pathlib import Path

# Add project root to Python path if not already present
# This allows imports to work regardless of where the script is run from
_project_root = Path(__file__).parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Now we can use absolute imports with 'src.' prefix
# Import directory_loader module directly (not exported from loaders/__init__.py)
import src.data_platform.document_processing.loaders.directory_loader as directory_loader
from src.data_platform.retrieval.vector_search import search_documents
from src.data_platform.storage.start_PostGres import ensure_postgres_started

# Run
if __name__ == "__main__":
    print("🚀 Starting PostgreSQL database...")
    if ensure_postgres_started():
        print("✅ PostgreSQL is running.")
    print("🚀 Starting document ingestion and vectorization...")
    directory_loader.Load_and_vectorize("src/data_platform/test_documents/")
    print("✅ Document ingestion and vectorization completed.")
    # Test search
    print("🔍 Searching documents...")
    print(search_documents("Retreival Augmented Generation"))
