# Requirements Agent - Complete Integration Guide

## Overview

This guide helps Workstream 1 and Workstream 2 teams integrate the Requirements Agent into the Multi-Agent RAG system.

---

## 📦 Package Structure

``` txt

requirements_agent/
├── requirements_agent.py       # Main agent implementation
├── data_platform_client.py     # Interface to Workstream 1 (to be implemented)
├── ollama_client.py            # LLM client
├── test_agent.py               # Unit tests
├── requirements.txt            # Python dependencies
└── README.md                   # Usage documentation
```

---

## 🔧 Installation & Setup

### Step 1: Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install requests typing-extensions dataclasses
```

### Step 2: Install and Configure Ollama

```bash
# Install Ollama (macOS/Linux)
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service
ollama serve

# Pull Llama 3.1 8B model (in another terminal)
ollama pull llama3.1:8b

# Verify model is available
ollama list
```

### Step 3: Test Ollama Connection

```python
from requirements_agent import OllamaLLM

llm = OllamaLLM()
if llm.health_check():
    print("✅ Ollama is ready!")
    
    # Test generation
    response = llm.generate("What is a requirement?", temperature=0.1)
    print(response)
else:
    print("❌ Ollama not available")
```

---

## 🔗 Workstream 1 Integration

### Option 1: Replace Mock Client (Recommended)

Create `data_platform_client.py` with actual API calls:

```python
import requests
from typing import List, Dict, Any, Optional

class DataPlatformClient:
    """Client for Workstream 1 Data Platform API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
    
    def retrieve_requirements_by_query(
        self,
        query: str,
        project_id: int,
        top_k: int = 5,
        min_similarity: float = 0.3,
        priority_filter: Optional[List[str]] = None,
        status_filter: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Call Workstream 1 retrieval API
        
        API Endpoint: POST /api/v1/retrieve/requirements
        """
        payload = {
            "query": query,
            "project_id": project_id,
            "top_k": top_k,
            "min_similarity": min_similarity,
            "category": "requirements",
            "filters": {
                "priority": priority_filter,
                "status": status_filter
            }
        }
        
        response = requests.post(
            f"{self.api_url}/retrieve/requirements",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        return response.json()["results"]
    
    def get_requirement_by_id(
        self,
        requirement_id: str,
        project_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get specific requirement by ID
        
        API Endpoint: GET /api/v1/requirements/{requirement_id}
        """
        response = requests.get(
            f"{self.api_url}/requirements/{requirement_id}",
            params={"project_id": project_id},
            timeout=10
        )
        
        if response.status_code == 404:
            return None
        
        response.raise_for_status()
        return response.json()
    
    def find_requirements_without_design(
        self,
        project_id: int,
        priority_filter: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Find requirements lacking design documentation
        
        API Endpoint: GET /api/v1/analytics/gaps
        """
        params = {
            "project_id": project_id,
            "gap_type": "requirements_without_design"
        }
        
        if priority_filter:
            params["priority_filter"] = ",".join(priority_filter)
        
        response = requests.get(
            f"{self.api_url}/analytics/gaps",
            params=params,
            timeout=30
        )
        response.raise_for_status()
        
        return response.json()["gaps"]
    
    def get_requirement_traceability(
        self,
        requirement_id: str,
        project_id: int
    ) -> Dict[str, Any]:
        """
        Get traceability chain
        
        API Endpoint: GET /api/v1/traceability/{requirement_id}
        """
        response = requests.get(
            f"{self.api_url}/traceability/{requirement_id}",
            params={"project_id": project_id},
            timeout=30
        )
        response.raise_for_status()
        
        return response.json()
    
    def get_all_requirement_ids(
        self,
        project_id: int,
        status_filter: Optional[List[str]] = None
    ) -> List[str]:
        """
        Get all requirement IDs
        
        API Endpoint: GET /api/v1/requirements/ids
        """
        params = {"project_id": project_id}
        
        if status_filter:
            params["status_filter"] = ",".join(status_filter)
        
        response = requests.get(
            f"{self.api_url}/requirements/ids",
            params=params,
            timeout=10
        )
        response.raise_for_status()
        
        return response.json()["requirement_ids"]
```

Then replace the import in `requirements_agent.py`:

```python
# Before (using mock)
from requirements_agent import DataPlatformClient

# After (using real API)
from data_platform_client import DataPlatformClient
```

### Option 2: Direct Database Access

If Workstream 1 provides a database connection, modify the agent to query directly:

```python
import psycopg2
from psycopg2.extras import RealDictCursor

class DatabaseClient:
    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
    
    def retrieve_requirements_by_query(self, query, project_id, top_k=5, **kwargs):
        # Generate embedding (assuming you have the embedding model)
        query_embedding = self.generate_embedding(query)
        
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    c.id,
                    c.chunk_text,
                    c.metadata,
                    d.filename,
                    1 - (c.embedding <=> %s::vector) as similarity_score
                FROM chunks c
                JOIN documents d ON c.document_id = d.id
                WHERE c.category_id = (
                    SELECT id FROM categories WHERE name = 'Requirements'
                )
                AND c.project_id = %s
                ORDER BY c.embedding <=> %s::vector
                LIMIT %s
            """, (query_embedding, project_id, query_embedding, top_k))
            
            return cur.fetchall()
```

---

## 🧪 Testing

### Unit Tests

Create `test_requirements_agent.py`:

```python
import unittest
from requirements_agent import RequirementsAgent, AgentContext, DataPlatformClient

class TestRequirementsAgent(unittest.TestCase):
    
    def setUp(self):
        self.data_platform = DataPlatformClient()
        self.agent = RequirementsAgent(
            category_id=1,
            data_platform_client=self.data_platform
        )
        self.context = AgentContext(project_id=1)
    
    def test_can_handle_requirements_query(self):
        """Test agent recognizes requirements queries"""
        query = "What are the authentication requirements?"
        score = self.agent.can_handle_query(query, self.context)
        self.assertGreater(score, 0.5)
    
    def test_can_handle_specific_req_id(self):
        """Test agent recognizes specific requirement IDs"""
        query = "Show me REQ-045"
        score = self.agent.can_handle_query(query, self.context)
        self.assertGreater(score, 0.9)
    
    def test_rejects_unrelated_query(self):
        """Test agent rejects unrelated queries"""
        query = "What's the weather today?"
        score = self.agent.can_handle_query(query, self.context)
        self.assertLess(score, 0.5)
    
    def test_process_general_query(self):
        """Test processing general requirements query"""
        query = "What are the authentication requirements?"
        response = self.agent.process_query(query, self.context)
        
        self.assertIsNotNone(response.content)
        self.assertGreater(response.confidence, 0.5)
        self.assertGreater(len(response.sources), 0)
    
    def test_gap_analysis(self):
        """Test gap analysis functionality"""
        query = "What requirements don't have design documentation?"
        response = self.agent.process_query(query, self.context)
        
        self.assertIn("gap_count", response.metadata)
    
    def test_traceability_query(self):
        """Test traceability queries"""
        query = "What components implement REQ-045?"
        response = self.agent.process_query(query, self.context)
        
        self.assertIsNotNone(response.content)
        self.assertIn("requirement_id", response.metadata)

if __name__ == "__main__":
    unittest.main()
```

Run tests:

```bash
python -m pytest test_requirements_agent.py -v
```

### Integration Tests with Workstream 1

```python
def test_end_to_end_integration():
    """Test complete flow with real data platform"""
    
    # Setup
    data_platform = DataPlatformClient(base_url="http://localhost:8000")
    agent = RequirementsAgent(category_id=1, data_platform_client=data_platform)
    context = AgentContext(project_id=1)
    
    # Test 1: Upload a sample requirement document (via Workstream 1 API)
    # (Assuming Workstream 1 provides upload endpoint)
    
    # Test 2: Query the requirement
    query = "What are the authentication requirements?"
    response = agent.process_query(query, context)
    
    assert response.confidence > 0.5
    assert len(response.sources) > 0
    
    print("✅ End-to-end integration test passed!")
```

---

## 🎯 Usage Examples

### Example 1: Simple Query

```python
from requirements_agent import RequirementsAgent, AgentContext, DataPlatformClient

# Initialize
data_platform = DataPlatformClient()
agent = RequirementsAgent(category_id=1, data_platform_client=data_platform)

# Create context
context = AgentContext(
    project_id=1,
    conversation_history=[],
    current_query="What are the authentication requirements?"
)

# Process query
response = agent.process_query(
    query="What are the authentication requirements?",
    context=context
)

# Display results
print(f"Answer: {response.content}")
print(f"Confidence: {response.confidence}")
print(f"Sources: {len(response.sources)}")

for source in response.sources:
    req_id = source['metadata'].get('requirement_id', 'Unknown')
    print(f"  - {req_id}: {source['chunk_text'][:100]}...")
```

### Example 2: Gap Analysis

```python
# Query for gaps
response = agent.process_query(
    query="What high-priority requirements don't have design documentation?",
    context=context
)

# Access gap metadata
gap_count = response.metadata.get('gap_count', 0)
high_priority_gaps = response.metadata.get('high_priority_gaps', 0)

print(f"Found {gap_count} requirements without design")
print(f"{high_priority_gaps} are high priority")
```

### Example 3: Traceability Analysis

```python
# Query specific requirement traceability
response = agent.process_query(
    query="What components implement REQ-045?",
    context=context
)

# Check if other agents are suggested
if response.suggested_agents:
    print("Suggested consulting:", ", ".join(response.suggested_agents))
```

### Example 4: Multi-Turn Conversation

```python
context = AgentContext(project_id=1, conversation_history=[])

# First query
query1 = "What are the authentication requirements?"
response1 = agent.process_query(query1, context)
context.conversation_history.append({"role": "user", "content": query1})
context.conversation_history.append({"role": "assistant", "content": response1.content})

# Follow-up query (uses conversation history)
query2 = "Which of these are high priority?"
response2 = agent.process_query(query2, context)

print(response2.content)  # Will reference previous authentication requirements
```

---

## 🔍 Troubleshooting

### Issue 1: Ollama Not Running

**Error:** `Cannot connect to Ollama. Ensure Ollama is running on localhost:11434`

**Solution:**

```bash
# Start Ollama
ollama serve

# In another terminal, verify it's running
curl http://localhost:11434/api/tags
```

### Issue 2: Model Not Available

**Error:** `Model llama3.1:8b not found`

**Solution:**

```bash
# Pull the model
ollama pull llama3.1:8b

# Verify
ollama list
```

### Issue 3: Slow Response Times

**Problem:** Agent takes 30+ seconds to respond

**Solutions:**

1. Use smaller model: `ollama pull mistral:7b`
2. Reduce max_tokens in generation
3. Use GPU acceleration (if available)
4. Cache frequent queries

### Issue 4: Low Quality Responses

**Problem:** LLM gives irrelevant or incomplete answers

**Solutions:**

1. Improve prompt engineering (add more examples)
2. Increase temperature slightly (0.1 → 0.2)
3. Provide more context in retrieval (top_k=10 instead of 5)
4. Try different model (Mistral vs Llama)

### Issue 5: JSON Parsing Errors

**Problem:** `JSONDecodeError` when parsing LLM response

**Solution:** The agent has built-in fallback for non-JSON responses. If issues persist:

```python
# The agent uses regex to extract JSON
# If LLM isn't returning JSON, try simplifying the prompt
# or add explicit JSON formatting instructions
```

---

## 📊 Performance Benchmarks

### Expected Performance (local hardware)

#### **Hardware: MacBook Pro M1, 16GB RAM**

| Operation | Avg Time | Notes |
| ----------- | ---------- | ------- |
| Query relevance check | 1-2ms | Fast, no LLM |
| Context retrieval | 100-300ms | Depends on Workstream 1 |
| LLM generation | 5-15s | Local Llama 3.1 8B |
| Total query time | 6-20s | End-to-end |

#### **Hardware: Intel i7, 32GB RAM, RTX 3080**

| Operation | Avg Time | Notes |
| ----------- | ---------- | ------- |
| LLM generation | 2-5s | GPU acceleration |
| Total query time | 3-8s | Much faster with GPU |

### Optimization Tips

1. **Use GPU**: Ollama automatically uses GPU if available

   ```bash
   # Verify GPU usage
   nvidia-smi
   ```

2. **Reduce context length**: Use fewer retrieved chunks (top_k=3 instead of 5)

3. **Cache results**: Cache frequent queries in memory or Redis

4. **Batch processing**: If processing multiple queries, use batch APIs

---

## 🚀 Deployment

### Development

```bash
# Run agent in development mode
python requirements_agent.py
```

### Production (with FastAPI)

Create `api_server.py`:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from requirements_agent import RequirementsAgent, AgentContext, DataPlatformClient

app = FastAPI()

# Initialize agent (singleton)
data_platform = DataPlatformClient(base_url="http://data-platform:8000")
agent = RequirementsAgent(category_id=1, data_platform_client=data_platform)

class QueryRequest(BaseModel):
    query: str
    project_id: int
    conversation_history: list = []

@app.post("/api/requirements/query")
async def query_requirements(request: QueryRequest):
    try:
        context = AgentContext(
            project_id=request.project_id,
            conversation_history=request.conversation_history
        )
        
        response = agent.process_query(request.query, context)
        
        return {
            "answer": response.content,
            "confidence": response.confidence,
            "sources": response.sources,
            "metadata": response.metadata,
            "suggested_agents": response.suggested_agents
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/requirements/health")
async def health_check():
    return {
        "status": "healthy",
        "ollama_available": agent.llm.health_check()
    }
```

Run server:

```bash
uvicorn api_server:app --host 0.0.0.0 --port 8001
```

---

## 📚 Next Steps

1. **Workstream 1**: Implement the 5 API endpoints defined in the API documentation
2. **Workstream 2**: Replace mock DataPlatformClient with real implementation
3. **Integration Testing**: Test end-to-end with real documents
4. **Performance Tuning**: Optimize prompts and retrieval parameters
5. **Deploy**: Set up production environment with FastAPI server

---

## 🤝 Support

**Questions?**

- Slack: #requirements-agent
- GitHub Issues: Tag with `requirements-agent`
- Integration Lead: [Your Name]

**Documentation:**

- API Docs: See `requirements_agent_api_docs.md`
- Code: See `requirements_agent.py`
- Tests: See `test_requirements_agent.py`
