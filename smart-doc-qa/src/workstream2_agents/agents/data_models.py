"""
Data models for agent communication and responses
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


# Add parent directory to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


class QueryType(Enum):
    """Types of queries the system can handle"""
    FACTUAL = "factual"
    PROCEDURAL = "procedural"
    COMPARATIVE = "comparative"
    TRACEABILITY = "traceability"
    GAP_ANALYSIS = "gap_analysis"
    IMPACT_ANALYSIS = "impact_analysis"


class Complexity(Enum):
    """Query complexity levels"""
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"
    MULTI_FACETED = "multi_faceted"


class ConfidenceLevel(Enum):
    """Confidence levels for agent responses"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class AgentContext:
    """Shared context across all agents"""
    project_id: int
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    current_query: str = ""
    query_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_message(self, role: str, content: str):
        """Add a message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content
        })


@dataclass
class Source:
    """Information about a source document/chunk"""
    chunk_id: int
    document_id: int
    filename: str
    category_name: str
    chunk_text: str
    page_number: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    similarity_score: float = 0.0


@dataclass
class AgentResponse:
    """Standardized response from agents"""
    agent_id: str
    agent_name: str
    content: str
    confidence: ConfidenceLevel
    sources: List[Source]
    metadata: Dict[str, Any] = field(default_factory=dict)
    requires_followup: bool = False
    suggested_agents: List[str] = field(default_factory=list)
    processing_time_ms: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "content": self.content,
            "confidence": self.confidence.value,
            "sources": [
                {
                    "chunk_id": s.chunk_id,
                    "filename": s.filename,
                    "category": s.category_name,
                    "text": s.chunk_text[:200],  # Truncate for display
                    "page": s.page_number,
                    "score": s.similarity_score
                }
                for s in self.sources
            ],
            "metadata": self.metadata,
            "suggested_agents": self.suggested_agents,
            "processing_time_ms": self.processing_time_ms
        }


@dataclass
class QueryAnalysis:
    """Analysis of a user query"""
    query_type: QueryType
    primary_intent: str
    required_categories: List[str]
    complexity: Complexity
    requires_multiple_agents: bool
    key_entities: Dict[str, Any] = field(default_factory=dict)
    temporal_scope: str = "current"
    suggested_workflow: str = "parallel"  # parallel, sequential, hybrid
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QueryAnalysis':
        """Create QueryAnalysis from dictionary"""
        return cls(
            query_type=QueryType(data.get("query_type", "factual")),
            primary_intent=data.get("primary_intent", ""),
            required_categories=data.get("required_categories", []),
            complexity=Complexity(data.get("complexity", "simple")),
            requires_multiple_agents=data.get("requires_multiple_agents", False),
            key_entities=data.get("key_entities", {}),
            temporal_scope=data.get("temporal_scope", "current"),
            suggested_workflow=data.get("suggested_workflow", "parallel")
        )


@dataclass
class OrchestratorResponse:
    """Final response from the orchestrator"""
    answer: str
    confidence: ConfidenceLevel
    sources: List[Source]
    agents_consulted: List[str]
    agent_agreement: str = "full"  # full, partial, conflicting
    key_insights: List[str] = field(default_factory=list)
    conflicts: Optional[str] = None
    processing_time_ms: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
        return {
            "answer": self.answer,
            "confidence": self.confidence.value,
            "sources": [
                {
                    "chunk_id": s.chunk_id,
                    "filename": s.filename,
                    "category": s.category_name,
                    "text": s.chunk_text[:200],
                    "page": s.page_number
                }
                for s in self.sources
            ],
            "agents_consulted": self.agents_consulted,
            "agent_agreement": self.agent_agreement,
            "key_insights": self.key_insights,
            "conflicts": self.conflicts,
            "processing_time_ms": self.processing_time_ms
        }
        