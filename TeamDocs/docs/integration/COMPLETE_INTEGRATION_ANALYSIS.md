# Integration Analysis - GenAI Capstone Project

**Date:** January 14, 2026 | **Branch:** Balaji | **Status:** 45% Complete

## Problem

Two codebases can't communicate:

- **Workstream 1** (data_platform): Processes docs, stores in Pinecone - 65% done
- **Workstream 2** (workstream2_agents): Multi-agent chat - 40% done
- **Gap:** NO API connecting them

## Impact

- System doesn't work end-to-end
- Agents return mock data
- 55% of project value unrealized

## Solution

Build REST API bridge (2 files, ~300 lines, 1 day)

## Implementation

### File 1: API Server

**Create:** `data_platform/api/server.py`

```python
from fastapi import FastAPI
from data_ingestion.vector_store_manager import VectorStoreManager

app = FastAPI()
vector_store = VectorStoreManager()

@app.post("/search")
async def search(query: str, top_k: int = 5):
    results = vector_store.search(query, top_k)
    return {"results": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)
```

### File 2: HTTP Client

**Create:** `workstream2_agents/agents/data_platform_client.py`

```python
import requests

class DataPlatformClient:
    def __init__(self, url="http://localhost:8000"):
        self.url = url
    
    def search(self, query: str, top_k: int = 5):
        response = requests.post(f"{self.url}/search", 
                               json={"query": query, "top_k": top_k})
        return response.json()["results"]
```

### File 3: Update Retriever

**Update:** `workstream2_agents/agents/retriever_agent.py`

```python
from .data_platform_client import DataPlatformClient

class RetrieverAgent:
    def __init__(self):
        self.client = DataPlatformClient()
    
    def retrieve(self, query: str):
        return self.client.search(query, top_k=5)
```

## Quick Start

### Terminal 1: Start API

```bash
cd data_platform/api
python server.py
```

### Terminal 2: Run Agents

```bash
cd workstream2_agents  
streamlit run main.py
```

## Success Criteria

- [ ] API responds to /search requests
- [ ] Agents return real documents (not mocks)
- [ ] End-to-end query works

## Timeline

- Hours 0-2: Create server.py and client.py
- Hours 2-3: Update agents
- Hours 3-4: Testing
- Hour 4: ✅ MVP Complete!

## Bottom Line

**Gap:** 2 files + small updates = 300 lines  
**Time:** 1 day MVP  
**Risk:** LOW  
**Value:** HIGH (unlocks 55% of project)

---
For more details, see 00_START_HERE.md
