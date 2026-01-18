import src
import src.data_platform.document_processing.loaders.directory_loader as directory_loader
from src.data_platform.retrieval.vector_search import search_documents
from src.data_platform.storage.start_PostGres import ensure_postgres_started
from src.data_platform.retrieval.search_similarity import search_pgvector
#from src.data_platform.test_documents  import test_search_queries
from src.data_platform.storage.document_repo import getdocument_by_id

# Run
if __name__ == "__main__":
    print("🚀 Starting PostgreSQL database...")
    if ensure_postgres_started():
        print("✅ PostgreSQL is running.")
    print("🚀 Starting document ingestion and vectorization...")
    directory_loader.Load_and_vectorize("src/data_platform/test_documents/")
    # directory_loader.Load_and_vectorize("C:\Mohandar\Capstone-Project\GenAI-Capstone-Project\smart-doc-qa\src\data_platform\test_documents")
    print("✅ Document ingestion and vectorization completed.")
    # Test search
    print("🔍 Searching documents...")
    # print(search_documents("Summarize the document"))
    # print("++++++++++++++++++++✅ Search 1 completed.++++++++++++++++++++")
    ########################################### Mohandar ##################################
    ###Following search query is used to provide similarity based search results from the PGVector database it will return top 3 results with minimum similarity of 0.5

    #search_query = "What is Synthetic Data sumarize synthetic data techniques?"
    search_query = "What is Retrieval Augmented Generation?"
    print("++++++++++++++++++++✅ Search 2 started.++++++++++++++++++++")
    print(f"Searching for: {search_query}")
    hits = search_pgvector(search_query, top_k=5, min_similarity=0.2)
    for row in hits:
        document = getdocument_by_id(row['document_id'])
        print(f"[{row['similarity']:.4f}] \n Document: {document['filename']}\nchunk: {row['chunk_text']}\n")
        print("---------------**********************************************************************---------------")
    print("++++++++++++++++++++✅ Search 2 completed.++++++++++++++++++++")
