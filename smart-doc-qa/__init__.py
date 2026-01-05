import src.data_platform.document_processing.loaders.directory_loader as directory_loader
from src.data_platform.retrieval.vector_search import search_documents
from src.data_platform.storage.start_PostGres import ensure_postgres_started

# Run
if __name__ == "__main__":
    print("🚀 Starting PostgreSQL database...")
    if ensure_postgres_started():
        print("✅ PostgreSQL is running.")
    print("🚀 Starting document ingestion and vectorization...")
    directory_loader.Load_and_vectorize("/Users/karthikkumarthirugnanam/AI Fellowship/5 PDF")
    print("✅ Document ingestion and vectorization completed.")
    # Test search
    print("🔍 Searching documents...")
    print(search_documents("Summarize the document"))
