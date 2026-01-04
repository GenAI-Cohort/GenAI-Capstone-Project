# Multi-Agent RAG System - Project Structure

```
smart-doc-qa/
│
├── README.md                           # Main project documentation
├── requirements.txt                    # Python dependencies
├── requirements-dev.txt                # Development dependencies (pytest, etc.)
├── .env.example                        # Environment variables template
├── .gitignore                          # Git ignore rules
├── setup.py                            # Package installation config
├── docker-compose.yml                  # Optional: Docker setup
│
├── docs/                               # 📚 Documentation
│   ├── architecture/
│   │   ├── database_schema.md
│   │   ├── agent_architecture.md
│   │   ├── data_flow.md
│   │   └── diagrams/
│   ├── api/
│   │   ├── endpoints.md
│   │   └── authentication.md
│   ├── setup/
│   │   ├── installation.md
│   │   ├── ollama_setup.md
│   │   └── troubleshooting.md
│   └── user_guide/
│       ├── uploading_documents.md
│       ├── querying.md
│       └── analytics.md
│
├── config/                             # ⚙️ Configuration files
│   ├── database.py                     # Database configuration
│   ├── embeddings.py                   # Embedding model config
│   ├── llm.py                          # LLM model config (Ollama)
│   ├── categories.py                   # Category definitions
│   └── logging.py                      # Logging configuration
│
├── scripts/                            # 🛠️ Utility scripts
│   ├── setup_database.py               # Initialize DB schema
│   ├── seed_categories.py              # Seed initial categories
│   ├── migrate_to_openai.py            # Migration script (if needed)
│   ├── benchmark_embeddings.py         # Test embedding performance
│   └── test_ollama.py                  # Verify Ollama connection
│
├── migrations/                         # 🗄️ Database migrations (Alembic)
│   ├── alembic.ini
│   ├── env.py
│   └── versions/
│       ├── 001_initial_schema.py
│       ├── 002_add_categories.py
│       └── 003_add_relationships.py
│
├── src/                                # 📦 Main source code
│   │
│   ├── __init__.py
│   │
│   ├── core/                           # Core utilities used across project
│   │   ├── __init__.py
│   │   ├── database.py                 # DB connection & session management
│   │   ├── exceptions.py               # Custom exceptions
│   │   ├── logging.py                  # Logging utilities
│   │   └── utils.py                    # General utility functions
│   │
│   ├── models/                         # 🗃️ Database models (SQLAlchemy)
│   │   ├── __init__.py
│   │   ├── document.py                 # Documents table
│   │   ├── chunk.py                    # Chunks table
│   │   ├── category.py                 # Categories table
│   │   ├── project.py                  # Projects table
│   │   ├── conversation.py             # Conversations & messages
│   │   ├── relationship.py             # Document relationships
│   │   └── query_log.py                # Query logging
│   │
│   ├── schemas/                        # 📋 Pydantic schemas (API models)
│   │   ├── __init__.py
│   │   ├── document.py                 # Document request/response schemas
│   │   ├── query.py                    # Query request/response schemas
│   │   ├── category.py                 # Category schemas
│   │   ├── project.py                  # Project schemas
│   │   └── agent.py                    # Agent response schemas
│   │
│   ├── data_platform/                  # 🔵 WORKSTREAM 1: Data Platform
│   │   ├── __init__.py
│   │   │
│   │   ├── embeddings/                 # Embedding generation
│   │   │   ├── __init__.py
│   │   │   ├── local_embeddings.py     # sentence-transformers wrapper
│   │   │   └── embedding_cache.py      # Optional caching layer
│   │   │
│   │   ├── document_processing/        # Document ingestion & chunking
│   │   │   ├── __init__.py
│   │   │   ├── loaders/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── pdf_loader.py
│   │   │   │   ├── docx_loader.py
│   │   │   │   ├── txt_loader.py
│   │   │   │   └── markdown_loader.py
│   │   │   ├── chunkers/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base_chunker.py
│   │   │   │   ├── requirements_chunker.py
│   │   │   │   ├── business_rules_chunker.py
│   │   │   │   ├── design_chunker.py
│   │   │   │   ├── tech_specs_chunker.py
│   │   │   │   ├── contracts_chunker.py
│   │   │   │   └── proposals_chunker.py
│   │   │   ├── metadata_extractors/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base_extractor.py
│   │   │   │   └── category_extractors.py  # All 6 categories
│   │   │   └── pipeline.py             # Document processing orchestrator
│   │   │
│   │   ├── retrieval/                  # Retrieval engine
│   │   │   ├── __init__.py
│   │   │   ├── vector_search.py        # Vector similarity search
│   │   │   ├── keyword_search.py       # Full-text search
│   │   │   ├── hybrid_search.py        # Combined vector + keyword
│   │   │   ├── category_retriever.py   # Category-aware retrieval
│   │   │   ├── reranker.py             # Re-ranking logic
│   │   │   └── traceability.py         # Relationship tracking
│   │   │
│   │   ├── analytics/                  # Analytics & insights
│   │   │   ├── __init__.py
│   │   │   ├── gap_analysis.py         # Find documentation gaps
│   │   │   ├── impact_analysis.py      # Change impact tracking
│   │   │   ├── traceability_matrix.py  # Req -> Design tracing
│   │   │   └── statistics.py           # System statistics
│   │   │
│   │   └── storage/                    # Database operations
│   │       ├── __init__.py
│   │       ├── document_repo.py        # Document CRUD
│   │       ├── chunk_repo.py           # Chunk CRUD
│   │       ├── category_repo.py        # Category CRUD
│   │       └── query_repo.py           # Query logging CRUD
│   │
│   ├── agent_system/                   # 🟢 WORKSTREAM 2: Agent System
│   │   ├── __init__.py
│   │   │
│   │   ├── llm/                        # LLM integration
│   │   │   ├── __init__.py
│   │   │   ├── ollama_client.py        # Ollama API wrapper
│   │   │   └── prompt_builder.py       # Prompt construction utilities
│   │   │
│   │   ├── agents/                     # Specialized agents
│   │   │   ├── __init__.py
│   │   │   ├── base_agent.py           # Base agent class
│   │   │   ├── requirements_agent.py
│   │   │   ├── business_rules_agent.py
│   │   │   ├── design_agent.py
│   │   │   ├── tech_specs_agent.py
│   │   │   ├── contracts_agent.py
│   │   │   └── proposals_agent.py
│   │   │
│   │   ├── orchestration/              # Orchestrator logic
│   │   │   ├── __init__.py
│   │   │   ├── orchestrator.py         # Main orchestrator
│   │   │   ├── query_analyzer.py       # Query understanding
│   │   │   ├── agent_selector.py       # Agent selection logic
│   │   │   ├── executor.py             # Agent execution (parallel/sequential)
│   │   │   └── synthesizer.py          # Response synthesis
│   │   │
│   │   ├── prompts/                    # Prompt templates
│   │   │   ├── __init__.py
│   │   │   ├── system_prompts.py       # System prompts per agent
│   │   │   ├── query_analysis.py       # Query analysis prompts
│   │   │   └── synthesis.py            # Synthesis prompts
│   │   │
│   │   └── memory/                     # Conversation memory
│   │       ├── __init__.py
│   │       ├── conversation_manager.py
│   │       └── context_builder.py
│   │
│   └── api/                            # 🟡 WORKSTREAM 3: API & UI
│       ├── __init__.py
│       │
│       ├── main.py                     # FastAPI application entry point
│       │
│       ├── routers/                    # API route handlers
│       │   ├── __init__.py
│       │   ├── documents.py            # Document endpoints
│       │   ├── queries.py              # Query endpoints
│       │   ├── projects.py             # Project endpoints
│       │   ├── categories.py           # Category endpoints
│       │   ├── analytics.py            # Analytics endpoints
│       │   └── health.py               # Health check
│       │
│       ├── dependencies.py             # FastAPI dependencies
│       ├── middleware.py               # Custom middleware
│       └── background_tasks.py         # Background job handlers
│
├── ui/                                 # 🖥️ Streamlit UI
│   ├── app.py                          # Main Streamlit app
│   ├── pages/
│   │   ├── 1_📚_Documents.py           # Document management page
│   │   ├── 2_💬_Chat.py                # Chat interface page
│   │   └── 3_📊_Analytics.py           # Analytics dashboard page
│   ├── components/
│   │   ├── __init__.py
│   │   ├── chat_message.py             # Chat message component
│   │   ├── document_uploader.py        # File upload component
│   │   ├── citation_display.py         # Citation component
│   │   └── agent_activity.py           # Agent activity indicator
│   └── utils/
│       ├── __init__.py
│       ├── session_state.py            # Session management
│       ├── api_client.py               # API communication
│       └── formatting.py               # Display formatting
│
├── tests/                              # 🧪 Test suite
│   ├── __init__.py
│   ├── conftest.py                     # Pytest fixtures
│   │
│   ├── unit/                           # Unit tests
│   │   ├── test_embeddings.py
│   │   ├── test_chunkers.py
│   │   ├── test_agents.py
│   │   ├── test_retrieval.py
│   │   └── test_orchestrator.py
│   │
│   ├── integration/                    # Integration tests
│   │   ├── test_document_pipeline.py
│   │   ├── test_query_flow.py
│   │   ├── test_multi_agent.py
│   │   └── test_api_endpoints.py
│   │
│   └── fixtures/                       # Test data
│       ├── sample_documents/
│       │   ├── requirements_sample.pdf
│       │   ├── business_rules_sample.docx
│       │   └── design_sample.md
│       └── expected_outputs/
│
├── data/                               # 🗂️ Data storage (gitignored)
│   ├── uploads/                        # Uploaded documents
│   ├── processed/                      # Processed documents
│   └── cache/                          # Embedding cache (optional)
│
├── logs/                               # 📝 Application logs (gitignored)
│   ├── app.log
│   ├── api.log
│   └── errors.log
│
└── demo/                               # 🎬 Demo materials
    ├── demo_dataset/                   # Sample documents for demo
    │   ├── requirements/
    │   ├── business_rules/
    │   ├── design_docs/
    │   ├── tech_specs/
    │   ├── contracts/
    │   └── proposals/
    ├── demo_script.md                  # Demo walkthrough script
    ├── demo_queries.txt                # List of impressive queries
    └── presentation.pdf                # Presentation slides
```

---

## 📁 Key Folder Purposes

### `/config` - Configuration Management
- Centralized configuration for database, embeddings, LLM
- Environment-specific settings
- Category definitions and chunking strategies

### `/src/data_platform` - Workstream 1
- **Complete data ingestion pipeline**: document loaders, chunkers, metadata extractors
- **Local embeddings**: sentence-transformers integration
- **Retrieval engine**: vector search, hybrid search, reranking
- **Analytics**: gap analysis, impact analysis, traceability

### `/src/agent_system` - Workstream 2
- **LLM integration**: Ollama client wrapper
- **6 specialized agents**: One per document category
- **Orchestration**: Query analysis, agent selection, synthesis
- **Prompts**: All prompt templates organized
- **Memory**: Conversation state management

### `/src/api` - Workstream 3 Backend
- **FastAPI application**: RESTful API endpoints
- **Routers**: Organized by resource (documents, queries, analytics)
- **Background tasks**: Async document processing

### `/ui` - Workstream 3 Frontend
- **Streamlit application**: Multi-page app
- **Components**: Reusable UI components
- **API client**: Communication with backend

### `/tests` - Quality Assurance
- **Unit tests**: Test individual components
- **Integration tests**: Test end-to-end workflows
- **Fixtures**: Sample data for testing

### `/docs` - Documentation
- Architecture documentation
- API specifications
- User guides
- Setup instructions

---

## 🚀 Getting Started Commands

```bash
# Clone and setup
git clone <your-repo>
cd smart-doc-qa

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your settings

# Initialize database
python scripts/setup_database.py
python scripts/seed_categories.py

# Verify Ollama
python scripts/test_ollama.py

# Run database migrations
alembic upgrade head

# Start API server
uvicorn src.api.main:app --reload --port 8000

# Start UI (in another terminal)
streamlit run ui/app.py
```

---

## 📦 Example `requirements.txt`

```txt
# Core dependencies
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0

# Database
psycopg2-binary==2.9.9
sqlalchemy==2.0.23
alembic==1.13.0
pgvector==0.2.4

# Embeddings (Local)
sentence-transformers==2.2.2
torch==2.1.0

# LLM (Ollama)
requests==2.31.0

# Document Processing
pypdf2==3.0.1
python-docx==1.1.0
beautifulsoup4==4.12.2
markdown==3.5.1

# API
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# UI
streamlit==1.28.1

# Utilities
langchain==0.1.0  # Optional
rank-bm25==0.2.2

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.1
```

---

## 🔧 Example `.env.example`

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/smart_doc_qa
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
OLLAMA_TIMEOUT=120

# Embeddings
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_DEVICE=cpu  # or 'cuda' if GPU available
EMBEDDING_BATCH_SIZE=32

# API
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# UI
UI_PORT=8501

# Storage
UPLOAD_DIR=./data/uploads
PROCESSED_DIR=./data/processed
LOG_DIR=./logs

# Performance
MAX_CHUNK_SIZE=1200
RETRIEVAL_TOP_K=10
ENABLE_CACHE=true
```

---

## 📝 Key Files Content Examples

### `src/api/main.py`
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routers import documents, queries, projects, categories, analytics, health

app = FastAPI(
    title="Multi-Agent RAG System API",
    version="1.0.0",
    description="Intelligent document Q&A with specialized AI agents"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/health", tags=["Health"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(queries.router, prefix="/api/queries", tags=["Queries"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(categories.router, prefix="/api/categories", tags=["Categories"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
```

### `ui/app.py`
```python
import streamlit as st
from ui.utils.session_state import initialize_session
from ui.utils.api_client import APIClient

st.set_page_config(
    page_title="Multi-Agent Knowledge Base",
    page_icon="🤖",
    layout="wide"
)

# Initialize
initialize_session()
api = APIClient()

st.title("🤖 Multi-Agent Document Q&A System")
st.markdown("Ask questions across your software documentation with specialized AI agents")

# Main content in pages/
```

---

This structure provides:
- ✅ **Clear separation** of the 3 workstreams
- ✅ **Modular design** for easy collaboration
- ✅ **Industry best practices** (Python project structure)
- ✅ **Scalable architecture** (easy to add new agents/categories)
- ✅ **Testing infrastructure** built-in
- ✅ **Documentation-ready** structure

Each team can work independently in their respective folders with minimal conflicts!