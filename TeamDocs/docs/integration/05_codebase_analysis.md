# Codebase Analysis - Deep Dive

**Project:** GenAI Capstone - Smart Document QA System  
**Date:** January 14, 2026  
**Branch:** Balaji  
**Audience:** Developers

---

## Table of Contents

1. [Workstream 1: data_platform](#workstream-1-data_platform)
2. [Workstream 2: workstream2_agents](#workstream-2-workstream2_agents)
3. [Integration Points](#integration-points)
4. [Code Examples](#code-examples)

---

## Workstream 1: data_platform

### Data Platform Directory Structure

```text
data_platform/
├── data_ingestion/
│   ├── __init__.py
│   ├── document_processor.py      ✅ Complete
│   ├── embedding_generator.py     ✅ Complete
│   └── vector_store_manager.py    ✅ Complete
├── config/
│   ├── __init__.py
│   └── config.py                  ✅ Complete
├── utils/
│   ├── __init__.py
│   └── logger.py                  ✅ Complete
├── api/                           ❌ TO CREATE
│   ├── __init__.py                ❌ TO CREATE
│   └── server.py                  ❌ TO CREATE
└── requirements.txt               ✅ Complete
```

---

### File: `data_ingestion/document_processor.py`

**Purpose:** Parse PDF documents and chunk text

**Key Functions:**

```python
class DocumentProcessor:
    def __init__(self):
        self.chunk_size = 1000
        self.chunk_overlap = 200
    
    def process_pdf(self, file_path: str) -> List[str]:
        """Extract and chunk text from PDF"""
        # Uses PyPDF2 for extraction
        # Returns list of text chunks
        
    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        # Uses RecursiveCharacterTextSplitter
        # Maintains context with overlap
```

**Status:** ✅ Working well  
**Dependencies:** PyPDF2, LangChain  
**Integration:** None needed - works independently

---

### File: `data_ingestion/embedding_generator.py`

**Purpose:** Generate OpenAI embeddings for text chunks

**Key Functions:**

```python
class EmbeddingGenerator:
    def __init__(self):
        self.model = "text-embedding-ada-002"
        self.client = OpenAI()
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for text chunks"""
        # Batch processing with rate limit handling
        # Returns list of embedding vectors
        
    def generate_single(self, text: str) -> List[float]:
        """Generate embedding for single text"""
        # Wrapper for single text embedding
```

**Status:** ✅ Working well  
**Dependencies:** OpenAI SDK  
**Integration:** None needed - works independently

---

### File: `data_ingestion/vector_store_manager.py`

**Purpose:** Manage Pinecone vector database operations

**Key Functions:**

```python
class VectorStoreManager:
    def __init__(self):
        self.index_name = "documents"
        self.pinecone_client = self._initialize_pinecone()
    
    def upsert_documents(self, vectors: List, metadata: List[Dict]):
        """Store vectors in Pinecone"""
        # Batch upsert with error handling
        
    def search(self, query_vector: List[float], top_k: int = 5) -> List[Dict]:
        """Search for similar vectors"""
        # THIS IS THE KEY METHOD WE NEED TO EXPOSE VIA API
        # Currently only used internally
        # Returns: [{"text": str, "score": float, "metadata": dict}]
```

**Status:** ✅ Working well, but not accessible externally  
**Dependencies:** Pinecone SDK  
**Integration:** ⚠️ **CRITICAL - Need to expose `search()` via API**

---

### File: `config/config.py`

**Purpose:** Configuration and environment variables

**Key Variables:**

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
    
    # API (TO ADD)
    API_PORT = int(os.getenv("API_PORT", 8000))
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
```

**Status:** ✅ Complete, may need API config additions  
**Dependencies:** python-dotenv  
**Integration:** Add API configuration variables

---

### File: `utils/logger.py`

**Purpose:** Logging infrastructure

**Key Functions:**

```python
import logging
import sys

def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Setup logger with consistent format"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger
```

**Status:** ✅ Complete and ready to use  
**Dependencies:** Standard library  
**Integration:** Use for API logging

---

### ❌ File TO CREATE: `api/server.py`

**Purpose:** REST API to expose vector search

**Implementation Needed:**

```python
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
```

**Estimated Lines:** ~150  
**Estimated Time:** 2 hours  
**Dependencies:** fastapi, uvicorn

---

## Workstream 2: workstream2_agents

### Agent Directory Structure

```text
workstream2_agents/
├── agents/
│   ├── __init__.py
│   ├── supervisor_agent.py        ✅ Complete
│   ├── router_agent.py            ✅ Complete
│   ├── retriever_agent.py         ⚠️ Returns mocks
│   ├── generator_agent.py         ⚠️ Uses mocks
│   ├── query_classifier.py        ✅ Complete
│   └── data_platform_client.py    ❌ TO CREATE
├── tools/
│   ├── __init__.py
│   └── custom_tools.py            ✅ Complete
├── main.py                        ✅ Complete
└── requirements.txt               ✅ Complete
```

---

### File: `agents/supervisor_agent.py`

**Purpose:** Orchestrate multi-agent workflow

**Key Functions:**

```python
class SupervisorAgent:
    def __init__(self):
        self.router = RouterAgent()
        self.retriever = RetrieverAgent()
        self.generator = GeneratorAgent()
    
    def process_query(self, query: str) -> str:
        """Main orchestration logic"""
        # 1. Route query to appropriate agent
        intent = self.router.classify(query)
        
        # 2. Retrieve relevant documents
        documents = self.retriever.retrieve(query)
        
        # 3. Generate response
        response = self.generator.generate(query, documents)
        
        return response
```

**Status:** ✅ Framework complete  
**Dependencies:** Internal agents  
**Integration:** None needed - just orchestrates

---

### File: `agents/router_agent.py`

**Purpose:** Route queries to appropriate handlers

**Key Functions:**

```python
class RouterAgent:
    def __init__(self):
        self.classifier = QueryClassifier()
    
    def classify(self, query: str) -> str:
        """Classify query intent"""
        # Uses NLP to determine query type
        # Returns: "search", "summarize", "compare", etc.
```

**Status:** ✅ Complete  
**Dependencies:** query_classifier  
**Integration:** None needed

---

### File: `agents/retriever_agent.py`

**Purpose:** Retrieve relevant documents

**Current Implementation (MOCK):**

```python
class RetrieverAgent:
    def retrieve(self, query: str) -> List[Dict]:
        """Retrieve relevant documents"""
        # TODO: Replace with real API call
        return [
            {
                "text": "This is mock document 1",
                "score": 0.95,
                "metadata": {"source": "mock"}
            },
            {
                "text": "This is mock document 2",
                "score": 0.87,
                "metadata": {"source": "mock"}
            }
        ]
```

**Needed Implementation:**

```python
from .data_platform_client import DataPlatformClient

class RetrieverAgent:
    def __init__(self):
        self.api_client = DataPlatformClient(
            base_url="http://localhost:8000"
        )
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """Retrieve relevant documents from data platform"""
        try:
            results = self.api_client.search_documents(
                query=query,
                top_k=top_k
            )
            return results
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            return []  # Graceful degradation
```

**Status:** ⚠️ **NEEDS UPDATE** - Replace mocks with API client  
**Estimated Lines:** ~50 lines to modify  
**Estimated Time:** 30 minutes

---

### File: `agents/generator_agent.py`

**Purpose:** Generate responses using LLM

**Current Implementation (Uses mocks):**

```python
class GeneratorAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4")
    
    def generate(self, query: str, documents: List[Dict]) -> str:
        """Generate response based on documents"""
        # Currently documents are mocks
        context = "\n".join([doc["text"] for doc in documents])
        
        prompt = f"""Based on the following documents:
        
        {context}
        
        Question: {query}
        
        Answer:"""
        
        response = self.llm.invoke(prompt)
        return response.content
```

**Status:** ✅ Logic is fine, just needs real documents  
**Integration:** Will automatically work once retriever is fixed

---

### File: `agents/query_classifier.py`

**Purpose:** Classify query intent

**Status:** ✅ Complete  
**Integration:** None needed

---

### ❌ File TO CREATE: `agents/data_platform_client.py`

**Purpose:** HTTP client to call data platform API

**Implementation Needed:**

```python
import requests
from typing import List, Dict, Optional
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class DataPlatformClient:
    """HTTP client for data platform API"""
    
    def __init__(
        self, 
        base_url: str = "http://localhost:8000",
        timeout: int = 30
    ):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def search_documents(
        self, 
        query: str, 
        top_k: int = 5,
        namespace: str = "default"
    ) -> List[Dict]:
        """
        Search for relevant documents
        
        Args:
            query: Search query text
            top_k: Number of results to return
            namespace: Pinecone namespace
            
        Returns:
            List of documents with text, score, metadata
        """
        try:
            response = self.session.post(
                f"{self.base_url}/search",
                json={
                    "query": query,
                    "top_k": top_k,
                    "namespace": namespace
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("success"):
                logger.info(f"Retrieved {data.get('count')} documents")
                return data.get("results", [])
            else:
                logger.warning("Search returned no results")
                return []
                
        except requests.exceptions.Timeout:
            logger.error("API request timed out")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return []
    
    def health_check(self) -> bool:
        """Check if API is healthy"""
        try:
            response = self.session.get(
                f"{self.base_url}/health",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
```

**Estimated Lines:** ~100  
**Estimated Time:** 1 hour  
**Dependencies:** requests, tenacity

---

### File: `main.py`

**Purpose:** Streamlit UI entry point

**Key Code:**

```python
import streamlit as st
from agents.supervisor_agent import SupervisorAgent

st.title("Smart Document QA System")

supervisor = SupervisorAgent()
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a question about your documents"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        response = supervisor.process_query(prompt)
        st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
```

**Status:** ✅ Complete - works with current mock setup  
**Integration:** Will automatically work once agents use real data

---

## Integration Points

### Critical Integration Point #1: API Server

**Location:** `data_platform/api/server.py` (TO CREATE)

**What it does:**

- Exposes vector search functionality via REST API
- Accepts search queries as JSON
- Returns relevant documents

**Interface:**

```json
POST /search
Request:  {"query": "user question", "top_k": 5}
Response: {"success": true, "results": [...], "count": 5}
```

**Dependencies:**

- `data_ingestion/vector_store_manager.py` (exists)
- `data_ingestion/embedding_generator.py` (exists)

**Estimated Effort:** 2 hours

---

### Critical Integration Point #2: HTTP Client

**Location:** `workstream2_agents/agents/data_platform_client.py` (TO CREATE)

**What it does:**

- Makes HTTP requests to data platform API
- Handles errors and retries
- Returns results to agents

**Interface:**

```python
client = DataPlatformClient("http://localhost:8000")
results = client.search_documents(query="test", top_k=5)
# Returns: [{"text": str, "score": float, "metadata": dict}]
```

**Dependencies:**

- `data_platform/api/server.py` (must be running)
- `requests` library

**Estimated Effort:** 1 hour

---

### Critical Integration Point #3: Retriever Agent Update

**Location:** `workstream2_agents/agents/retriever_agent.py` (UPDATE)

**What needs to change:**

**Before:**

```python
def retrieve(self, query: str) -> List[Dict]:
    # Returns hardcoded mocks
    return [{"text": "mock", "score": 0.9}]
```

**After:**

```python
from .data_platform_client import DataPlatformClient

def __init__(self):
    self.api_client = DataPlatformClient()

def retrieve(self, query: str) -> List[Dict]:
    # Returns real documents from API
    return self.api_client.search_documents(query)
```

**Estimated Effort:** 30 minutes

---

### Integration Point #4: Generator Agent (Auto-fixed)

**Location:** `workstream2_agents/agents/generator_agent.py`

**Status:** No changes needed! Once retriever returns real documents, generator will automatically use them.

---

## Code Examples

### Example 1: Complete API Server

```python
# data_platform/api/server.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from data_ingestion.vector_store_manager import VectorStoreManager
from data_ingestion.embedding_generator import EmbeddingGenerator
from utils.logger import setup_logger
from config.config import Config

# Setup
logger = setup_logger(__name__)
app = FastAPI(
    title="Data Platform API",
    description="API for document retrieval and search",
    version="1.0.0"
)

# Initialize components
vector_store = VectorStoreManager()
embedding_gen = EmbeddingGenerator()

# Models
class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    namespace: str = "default"

class DocumentResult(BaseModel):
    text: str
    score: float
    metadata: dict

class SearchResponse(BaseModel):
    success: bool
    results: List[DocumentResult]
    count: int

# Endpoints
@app.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """
    Search for relevant documents
    
    Args:
        request: SearchRequest with query, top_k, namespace
        
    Returns:
        SearchResponse with results
    """
    try:
        logger.info(f"Search request: query='{request.query}', top_k={request.top_k}")
        
        # Generate query embedding
        query_embedding = embedding_gen.generate_single(request.query)
        
        # Search vector store
        results = vector_store.search(
            query_vector=query_embedding,
            top_k=request.top_k,
            namespace=request.namespace
        )
        
        logger.info(f"Search completed: {len(results)} results found")
        
        return SearchResponse(
            success=True,
            results=results,
            count=len(results)
        )
        
    except Exception as e:
        logger.error(f"Search failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "data-platform-api",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Data Platform API",
        "docs": "/docs",
        "health": "/health"
    }

# Run server
if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting API server on {Config.API_HOST}:{Config.API_PORT}")
    
    uvicorn.run(
        app,
        host=Config.API_HOST,
        port=Config.API_PORT,
        log_level="info"
    )
```

---

### Example 2: Complete HTTP Client

```python
# workstream2_agents/agents/data_platform_client.py

import requests
from typing import List, Dict, Optional
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class DataPlatformClient:
    """
    HTTP client for data platform API
    
    Provides methods to search documents and check health
    with automatic retry logic and error handling.
    """
    
    def __init__(
        self, 
        base_url: str = "http://localhost:8000",
        timeout: int = 30
    ):
        """
        Initialize client
        
        Args:
            base_url: Base URL of the data platform API
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
        logger.info(f"Initialized DataPlatformClient with base_url={base_url}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def search_documents(
        self, 
        query: str, 
        top_k: int = 5,
        namespace: str = "default"
    ) -> List[Dict]:
        """
        Search for relevant documents
        
        Args:
            query: Search query text
            top_k: Number of results to return
            namespace: Pinecone namespace
            
        Returns:
            List of documents with text, score, metadata
            Empty list if search fails
        """
        try:
            logger.info(f"Searching documents: query='{query[:50]}...', top_k={top_k}")
            
            response = self.session.post(
                f"{self.base_url}/search",
                json={
                    "query": query,
                    "top_k": top_k,
                    "namespace": namespace
                },
                timeout=self.timeout
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data.get("success"):
                results = data.get("results", [])
                logger.info(f"Retrieved {len(results)} documents")
                return results
            else:
                logger.warning("Search returned success=false")
                return []
                
        except requests.exceptions.Timeout:
            logger.error(f"API request timed out after {self.timeout}s")
            return []
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            return []
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            return []
            
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return []
    
    def health_check(self) -> bool:
        """
        Check if API is healthy
        
        Returns:
            True if API is responding, False otherwise
        """
        try:
            response = self.session.get(
                f"{self.base_url}/health",
                timeout=5
            )
            is_healthy = response.status_code == 200
            logger.info(f"Health check: {'healthy' if is_healthy else 'unhealthy'}")
            return is_healthy
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False
    
    def close(self):
        """Close the session"""
        self.session.close()
```

---

### Example 3: Updated Retriever Agent

```python
# workstream2_agents/agents/retriever_agent.py

from typing import List, Dict
import logging
from .data_platform_client import DataPlatformClient

logger = logging.getLogger(__name__)

class RetrieverAgent:
    """
    Agent responsible for retrieving relevant documents
    from the data platform.
    """
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        """
        Initialize retriever agent
        
        Args:
            api_base_url: Base URL of data platform API
        """
        self.api_client = DataPlatformClient(base_url=api_base_url)
        logger.info("RetrieverAgent initialized")
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Retrieve relevant documents for a query
        
        Args:
            query: User's question or search query
            top_k: Number of documents to retrieve
            
        Returns:
            List of relevant documents with text, score, metadata
        """
        logger.info(f"Retrieving documents for query: '{query[:50]}...'")
        
        # Check API health first
        if not self.api_client.health_check():
            logger.error("Data platform API is not healthy")
            return []
        
        # Retrieve documents
        results = self.api_client.search_documents(
            query=query,
            top_k=top_k
        )
        
        if not results:
            logger.warning(f"No documents found for query: '{query[:50]}...'")
        else:
            logger.info(f"Retrieved {len(results)} documents")
        
        return results
```

---

## Testing Commands

### Start API Server

```bash
cd data_platform/api
python server.py

# Should see:
# INFO:     Started server process
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Test API with curl

```bash
# Health check
curl http://localhost:8000/health

# Search
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the main features?", "top_k": 3}'
```

### Test API with Python

```python
import requests

# Health check
response = requests.get("http://localhost:8000/health")
print(response.json())

# Search
response = requests.post(
    "http://localhost:8000/search",
    json={"query": "test query", "top_k": 5}
)
print(response.json())
```

### Run Agent System

```bash
cd workstream2_agents
streamlit run main.py

# Should see:
# You can now view your Streamlit app in your browser.
# Local URL: http://localhost:8501
```

---

## Dependencies to Install

### Workstream 1 (data_platform)

```bash
pip install fastapi uvicorn[standard]
```

### Workstream 2 (workstream2_agents)

```bash
pip install requests tenacity
```

---

## Summary

**Files to Create:** 2

1. `data_platform/api/server.py` (~150 lines)
2. `workstream2_agents/agents/data_platform_client.py` (~100 lines)

**Files to Update:** 1

1. `workstream2_agents/agents/retriever_agent.py` (~50 lines modified)

**Total New/Modified Code:** ~300 lines

**Estimated Time:** 4 hours

---

*For next steps, see IMPLEMENTATION_CHECKLIST.md*  
*For quick commands, see QUICK_REFERENCE_GUIDE.md*

---
