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
