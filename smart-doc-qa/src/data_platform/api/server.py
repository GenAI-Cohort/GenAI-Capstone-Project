from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys
sys.path.append('../')

from data_ingestion.vector_store_manager import VectorStoreManager
from data_ingestion.embedding_generator import EmbeddingGenerator
from utils.logger import setup_logger

logger = setup_logger(__name__)
app = FastAPI(title="Data Platform API")

vector_store = VectorStoreManager()
embedding_gen = EmbeddingGenerator()

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    namespace: str = "default"

class SearchResponse(BaseModel):
    success: bool
    results: list
    count: int

@app.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """Search for relevant documents"""
    try:
        # Generate embedding for query
        query_embedding = embedding_gen.generate_single(request.query)
        
        # Search vector store
        results = vector_store.search(
            query_vector=query_embedding,
            top_k=request.top_k
        )
        
        logger.info(f"Search completed: {len(results)} results")
        
        return SearchResponse(
            success=True,
            results=results,
            count=len(results)
        )
    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    from config.config import Config
    
    uvicorn.run(
        app,
        host=Config.API_HOST,
        port=Config.API_PORT
    )
