# Quick Reference Guide

**Project:** GenAI Capstone - Smart Document QA System  
**Date:** January 14, 2026  
**Purpose:** Fast reference for common commands, code snippets, and solutions

---

## Table of Contents

1. [Quick Start Commands](#quick-start-commands)
2. [API Examples](#api-examples)
3. [Code Snippets](#code-snippets)
4. [Testing Commands](#testing-commands)
5. [Troubleshooting](#troubleshooting)
6. [Configuration](#configuration)

---

## Quick Start Commands

### Start API Server

```bash
cd data_platform/api
python server.py

# Or with custom port
python server.py --port 8001

# With debug mode
uvicorn server:app --reload --port 8000
```

### Start Agent System

```bash
cd workstream2_agents
streamlit run main.py

# With custom port
streamlit run main.py --server.port 8502
```

### Install Dependencies

```bash
# API Server
pip install fastapi uvicorn[standard] pydantic

# HTTP Client
pip install requests tenacity

# Testing
pip install pytest pytest-asyncio

# Optional
pip install slowapi cachetools redis
```

### Quick Test

```bash
# Terminal 1: Start API
cd data_platform/api && python server.py

# Terminal 2: Test API
curl http://localhost:8000/health

# Terminal 3: Start UI
cd workstream2_agents && streamlit run main.py
```

---

## API Examples

### Health Check

```bash
curl http://localhost:8000/health
```

**Response:**

```json
{
  "status": "healthy",
  "service": "data-platform-api",
  "version": "1.0.0"
}
```

---

### Search Documents

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the main features?",
    "top_k": 5,
    "namespace": "default"
  }'
```

**Response:**

```json
{
  "success": true,
  "results": [
    {
      "text": "Document content here...",
      "score": 0.89,
      "metadata": {
        "source": "doc1.pdf",
        "page": 1
      }
    }
  ],
  "count": 5
}
```

---

### Test with Python

```python
import requests

# Health check
response = requests.get("http://localhost:8000/health")
print(response.json())

# Search
response = requests.post(
    "http://localhost:8000/search",
    json={
        "query": "machine learning",
        "top_k": 3
    }
)
data = response.json()
for result in data["results"]:
    print(f"Score: {result['score']:.2f}")
    print(f"Text: {result['text'][:100]}...")
```

---

### With Authentication (Phase 3)

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{
    "query": "test",
    "top_k": 3
  }'
```

---

## Code Snippets

### API Server - Minimal Example

**File:** `data_platform/api/server.py`

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys
sys.path.append('../')

from data_ingestion.vector_store_manager import VectorStoreManager
from data_ingestion.embedding_generator import EmbeddingGenerator

app = FastAPI()
vector_store = VectorStoreManager()
embedding_gen = EmbeddingGenerator()

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

@app.post("/search")
async def search(request: SearchRequest):
    try:
        # Generate embedding
        embedding = embedding_gen.generate_single(request.query)
        
        # Search
        results = vector_store.search(embedding, request.top_k)
        
        return {
            "success": True,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

### HTTP Client - Minimal Example

**File:** `workstream2_agents/agents/data_platform_client.py`

```python
import requests
from typing import List, Dict

class DataPlatformClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def search_documents(self, query: str, top_k: int = 5) -> List[Dict]:
        try:
            response = self.session.post(
                f"{self.base_url}/search",
                json={"query": query, "top_k": top_k},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
        except Exception as e:
            print(f"Error: {e}")
            return []
    
    def health_check(self) -> bool:
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
```

---

### Retriever Agent - Updated

**File:** `workstream2_agents/agents/retriever_agent.py`

```python
from .data_platform_client import DataPlatformClient
from typing import List, Dict

class RetrieverAgent:
    def __init__(self):
        self.api_client = DataPlatformClient()
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        # Check API health
        if not self.api_client.health_check():
            print("API is not available")
            return []
        
        # Retrieve documents
        results = self.api_client.search_documents(query, top_k)
        return results
```

---

### Generator Agent - Uses Real Documents

**File:** `workstream2_agents/agents/generator_agent.py`

```python
from langchain.chat_models import ChatOpenAI
from typing import List, Dict

class GeneratorAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4")
    
    def generate(self, query: str, documents: List[Dict]) -> str:
        # Create context from documents
        context = "\n\n".join([doc["text"] for doc in documents])
        
        # Create prompt
        prompt = f"""Based on the following documents, answer the question.

Documents:
{context}

Question: {query}

Answer:"""
        
        # Generate response
        response = self.llm.invoke(prompt)
        return response.content
```

---

### Add Retry Logic

```python
from tenacity import retry, stop_after_attempt, wait_exponential

class DataPlatformClient:
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def search_documents(self, query: str, top_k: int = 5):
        # ... your code here
        pass
```

---

### Add Logging

```python
import logging

logger = logging.getLogger(__name__)

# In your function
logger.info(f"Searching for: {query}")
logger.error(f"Search failed: {error}")
```

---

### Add Request Validation

```python
from pydantic import BaseModel, Field, validator

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(5, ge=1, le=20)
    namespace: str = "default"
    
    @validator('query')
    def query_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Query cannot be empty')
        return v
```

---

### Add Error Handling

```python
@app.post("/search")
async def search(request: SearchRequest):
    try:
        # Your code here
        pass
    except ConnectionError as e:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid input: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
```

---

## Testing Commands

### Test API Manually

```bash
# Health check
curl http://localhost:8000/health

# Search with minimal parameters
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'

# Search with all parameters
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning", "top_k": 10, "namespace": "default"}'

# Pretty print JSON response
curl http://localhost:8000/health | jq '.'
```

---

### Test with Python Script

**File:** `test_api.py`

```python
import requests
import time

BASE_URL = "http://localhost:8000"

def test_health():
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    print("✓ Health check passed")

def test_search():
    print("Testing search endpoint...")
    response = requests.post(
        f"{BASE_URL}/search",
        json={"query": "test query", "top_k": 3}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    print(f"✓ Search returned {data['count']} results")

def test_invalid_request():
    print("Testing invalid request...")
    response = requests.post(
        f"{BASE_URL}/search",
        json={"query": "", "top_k": -1}
    )
    assert response.status_code == 422
    print("✓ Invalid request properly rejected")

def test_performance():
    print("Testing performance...")
    start = time.time()
    response = requests.post(
        f"{BASE_URL}/search",
        json={"query": "test", "top_k": 5}
    )
    elapsed = time.time() - start
    print(f"✓ Search completed in {elapsed:.2f}s")
    assert elapsed < 2.0, "Response too slow"

if __name__ == "__main__":
    test_health()
    test_search()
    test_invalid_request()
    test_performance()
    print("\n✅ All tests passed!")
```

**Run:** `python test_api.py`

---

### Integration Test

**File:** `tests/test_integration.py`

```python
import pytest
import requests
from workstream2_agents.agents.data_platform_client import DataPlatformClient

BASE_URL = "http://localhost:8000"

def test_api_available():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200

def test_client_can_search():
    client = DataPlatformClient(BASE_URL)
    results = client.search_documents("test", top_k=3)
    assert isinstance(results, list)

def test_end_to_end():
    from workstream2_agents.agents.retriever_agent import RetrieverAgent
    
    retriever = RetrieverAgent()
    results = retriever.retrieve("test query")
    assert len(results) > 0
    assert "text" in results
    assert "score" in results
```

**Run:** `pytest tests/test_integration.py -v`

---

## Troubleshooting

### API Won't Start

**Problem:** `Address already in use`

**Solution:**

```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
python server.py --port 8001
```

---

### Connection Refused

**Problem:** Client can't reach API

**Check:**

```bash
# 1. Is API running?
curl http://localhost:8000/health

# 2. Check API logs
# Look in terminal where API is running

# 3. Try different address
curl http://127.0.0.1:8000/health
curl http://0.0.0.0:8000/health

# 4. Check firewall
# On Mac: System Preferences → Security → Firewall
```

---

### Timeout Errors

**Problem:** Requests timing out

**Solutions:**

```python
# Increase timeout
client = DataPlatformClient(timeout=60)

# Check Pinecone connection
# Verify API keys in .env

# Add logging to see where it's slow
import time
start = time.time()
# ... your code ...
print(f"Took {time.time() - start:.2f}s")
```

---

### No Results Returned

**Problem:** Search returns empty list

**Check:**

```python
# 1. Verify Pinecone has data
from data_ingestion.vector_store_manager import VectorStoreManager
store = VectorStoreManager()
# Check if index exists and has vectors

# 2. Test with known query
# Use a query you know should return results

# 3. Check logs
# Look for errors in API logs

# 4. Test embedding generation
from data_ingestion.embedding_generator import EmbeddingGenerator
gen = EmbeddingGenerator()
embedding = gen.generate_single("test")
print(f"Embedding size: {len(embedding)}")
```

---

### Import Errors

**Problem:** `ModuleNotFoundError`

**Solutions:**

```bash
# Install missing package
pip install <package-name>

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Add to path in code
import sys
sys.path.append('/path/to/your/code')

# Or use relative imports
from .data_platform_client import DataPlatformClient
```

---

### Agent Returns Mocks

**Problem:** Still getting mock data after update

**Check:**

```python
# 1. Verify retriever_agent.py was updated
# Open file and check for DataPlatformClient import

# 2. Restart Streamlit
# Ctrl+C and restart: streamlit run main.py

# 3. Check API is running
# curl http://localhost:8000/health

# 4. Add debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Configuration

### Environment Variables

**File:** `.env`

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Pinecone
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX=documents

# API Server
API_HOST=0.0.0.0
API_PORT=8000
API_KEY=your-secret-api-key-here  # Phase 3

# Logging
LOG_LEVEL=INFO
```

**Load in Python:**

```python
from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
```

---

### API Configuration

**File:** `data_platform/config/config.py`

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Pinecone
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
    PINECONE_INDEX = os.getenv("PINECONE_INDEX", "documents")
    
    # API
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", 8000))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
```

---

### Client Configuration

**File:** `workstream2_agents/agents/data_platform_client.py`

```python
import os

class DataPlatformClient:
    def __init__(
        self, 
        base_url: str = None,
        timeout: int = 30,
        api_key: str = None
    ):
        self.base_url = base_url or os.getenv(
            "DATA_PLATFORM_URL", 
            "http://localhost:8000"
        )
        self.timeout = timeout
        self.api_key = api_key or os.getenv("DATA_PLATFORM_API_KEY")
```

---

## Useful Code Patterns

### Pattern 1: Graceful Degradation

```python
def retrieve(self, query: str) -> List[Dict]:
    try:
        # Try to get real data
        results = self.api_client.search_documents(query)
        if results:
            return results
    except Exception as e:
        logger.warning(f"API failed, using fallback: {e}")
    
    # Fallback to empty or cached results
    return []
```

---

### Pattern 2: Circuit Breaker

```python
class CircuitBreaker:
    def __init__(self, max_failures=3, timeout=60):
        self.failures = 0
        self.max_failures = max_failures
        self.timeout = timeout
        self.last_failure = None
    
    def call(self, func, *args, **kwargs):
        if self.failures >= self.max_failures:
            if time.time() - self.last_failure < self.timeout:
                raise Exception("Circuit breaker open")
            else:
                self.failures = 0  # Reset after timeout
        
        try:
            result = func(*args, **kwargs)
            self.failures = 0  # Reset on success
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure = time.time()
            raise
```

---

### Pattern 3: Response Caching

```python
from functools import lru_cache
import hashlib

def cache_key(query: str, top_k: int) -> str:
    """Generate cache key from query parameters"""
    key = f"{query}:{top_k}"
    return hashlib.md5(key.encode()).hexdigest()

@lru_cache(maxsize=100)
def cached_search(query_hash: str, query: str, top_k: int):
    """Cached search function"""
    return vector_store.search(query, top_k)
```

---

### Pattern 4: Async Operations

```python
import asyncio
from typing import List

async def batch_search(queries: List[str]) -> List[List[Dict]]:
    """Search multiple queries in parallel"""
    tasks = [
        asyncio.create_task(search_async(query))
        for query in queries
    ]
    results = await asyncio.gather(*tasks)
    return results

# Usage
results = asyncio.run(batch_search(["query1", "query2", "query3"]))
```

---

### Pattern 5: Structured Logging

```python
import logging
import json

class StructuredLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
    
    def log(self, level, message, **kwargs):
        log_data = {
            "message": message,
            "timestamp": time.time(),
            **kwargs
        }
        self.logger.log(level, json.dumps(log_data))

# Usage
logger = StructuredLogger(__name__)
logger.log(
    logging.INFO,
    "Search completed",
    query="test",
    results_count=5,
    response_time=0.5
)
```

---

## Performance Tips

### 1. Use Connection Pooling

```python
import requests

# Create session for connection reuse
session = requests.Session()
session.mount('http://', requests.adapters.HTTPAdapter(pool_connections=10))

# Use session for all requests
response = session.post(url, json=data)
```

---

### 2. Implement Caching

```python
from cachetools import TTLCache
import time

# Cache with 5-minute TTL
cache = TTLCache(maxsize=100, ttl=300)

def search_with_cache(query: str, top_k: int):
    key = f"{query}:{top_k}"
    
    if key in cache:
        return cache[key]
    
    result = search(query, top_k)
    cache[key] = result
    return result
```

---

### 3. Batch Operations

```python
# Instead of:
for query in queries:
    result = search(query)
    
# Do:
results = batch_search(queries)  # All at once
```

---

### 4. Async for I/O-bound Operations

```python
async def search_async(query: str):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            return await response.json()
```

---

### 5. Optimize Vector Search

```python
# Use appropriate top_k (don't retrieve more than needed)
results = search(query, top_k=5)  # Not 100

# Use filters to reduce search space
results = search(
    query, 
    top_k=5,
    filters={"source": "important_docs"}
)
```

---

## Common Error Messages and Solutions

### Error: `ModuleNotFoundError: No module named 'fastapi'`

**Solution:** `pip install fastapi uvicorn`

---

### Error: `Connection refused`

**Solution:** Check API is running: `curl http://localhost:8000/health`

---

### Error: `TypeError: 'coroutine' object is not iterable`

**Solution:** Add `await` before async function call

---

### Error: `KeyError: 'OPENAI_API_KEY'`

**Solution:** Create `.env` file with required keys or export environment variables

---

### Error: `422 Unprocessable Entity`

**Solution:** Check request body matches SearchRequest model schema

---

### Error: `TimeoutError`

**Solution:** Increase timeout or check Pinecone connection

---

### Error: `429 Too Many Requests`

**Solution:** Implement rate limiting or add delays between requests

---

## Deployment Checklist

### Before Deployment

- [ ] All environment variables configured
- [ ] All dependencies in requirements.txt
- [ ] API keys secured (not in code)
- [ ] Error handling implemented
- [ ] Logging configured
- [ ] Integration tests pass
- [ ] Load testing completed
- [ ] Documentation updated

### Deployment Commands

```bash
# 1. Update dependencies
pip freeze > requirements.txt

# 2. Set environment variables
export OPENAI_API_KEY=...
export PINECONE_API_KEY=...

# 3. Start API server
python data_platform/api/server.py

# 4. Start agent system
streamlit run workstream2_agents/main.py

# 5. Verify health
curl http://localhost:8000/health
```

---

## Monitoring Commands

### Check API Status

```bash
# Health check
curl http://localhost:8000/health

# Get metrics (if implemented)
curl http://localhost:8000/metrics
```

---

### Monitor Logs

```bash
# Follow API logs
tail -f api.log

# Search logs for errors
grep ERROR api.log

# Count error types
grep ERROR api.log | cut -d: -f2 | sort | uniq -c
```

---

### Check Performance

```bash
# Time a request
time curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'

# Monitor API with watch
watch -n 5 'curl -s http://localhost:8000/health'
```

---

## Quick Fixes

### Fix: API Won't Start

```bash
# Kill existing process
pkill -f "python server.py"

# Start fresh
python server.py
```

---

### Fix: Stale Cache

```python
# Clear cache
cache.clear()

# Or restart API to clear in-memory cache
```

---

### Fix: Slow Queries

```python
# Reduce top_k
results = search(query, top_k=3)  # Instead of 10

# Add filters
results = search(query, top_k=5, filters={"date": "recent"})

# Implement caching
```

---

### Fix: Import Issues

```bash
# Add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/your/project"

# Or in code
import sys
sys.path.insert(0, '/path/to/your/project')
```

---

## Keyboard Shortcuts

### Streamlit

- `Ctrl+C` - Stop server
- `R` - Rerun app
- `C` - Clear cache

### Terminal

- `Ctrl+C` - Stop process
- `Ctrl+Z` - Suspend process
- `fg` - Resume suspended process

---

## Helpful Resources

### Documentation

- [FastAPI](https://fastapi.tiangolo.com/)
- [Streamlit](https://docs.streamlit.io/)
- [Pinecone](https://docs.pinecone.io/)
- [LangChain](https://python.langchain.com/)

### Testing

- [curl](https://curl.se/docs/)
- [pytest](https://docs.pytest.org/)
- [Postman](https://www.postman.com/)

---

## Summary - Most Used Commands

```bash
# Start everything
cd data_platform/api && python server.py &
cd workstream2_agents && streamlit run main.py &

# Test API
curl http://localhost:8000/health
curl -X POST http://localhost:8000/search -H "Content-Type: application/json" -d '{"query":"test"}'

# Run tests
pytest tests/ -v

# Stop everything
pkill -f "python server.py"
pkill -f "streamlit"
```

---

**🔖 Bookmark this page for quick reference during development!**

*For full implementation details, see IMPLEMENTATION_CHECKLIST.md*  
*For troubleshooting, see integration_blockers_and_strategy.md*

---
