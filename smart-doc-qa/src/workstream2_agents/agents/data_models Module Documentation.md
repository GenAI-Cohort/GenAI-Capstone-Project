# Data Models Module Documentation

The `agents/data_models.py` module defines the core data structures used throughout the workstream2 agent framework for communication, query processing, and response handling.

## Module Overview

This module provides a comprehensive type system built on Python's `dataclasses` and `Enum` types to ensure type safety and structured data flow across all agents, orchestrators, and API layers. It standardizes how queries are analyzed, how agents communicate their findings, and how responses are aggregated and serialized for client consumption.

### Design Philosophy

- **Immutability by Default**: Uses `@dataclass` for value-object semantics
- **Type Safety**: Leverages Python typing hints extensively for IDE support and validation
- **Serialization Ready**: All major classes include `to_dict()` methods for JSON conversion
- **Enum-based Classification**: Uses enums to constrain valid values for query types, complexity, and confidence

***

## Dependencies and Imports

### Standard Library

- `dataclasses`: Provides `@dataclass` decorator and `field` factory for default values
- `typing`: Imports `List`, `Dict`, `Any`, `Optional` for comprehensive type annotations
- `enum`: Provides `Enum` base class for enumerated types


### Path Setup

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

Adds the parent directory to `sys.path` to enable relative imports during development.

***

## Enumeration Types

### QueryType

```python
class QueryType(Enum):
    """Types of queries the system can handle"""
    FACTUAL = "factual"
    PROCEDURAL = "procedural"
    COMPARATIVE = "comparative"
    TRACEABILITY = "traceability"
    GAP_ANALYSIS = "gap_analysis"
    IMPACT_ANALYSIS = "impact_analysis"
```


#### Purpose

Classifies user queries into distinct categories to guide agent selection and workflow routing.

#### Values

- **FACTUAL**: Direct information retrieval queries
    - Example: "What is the maximum processing time for a payment?"
    - Requires single-agent lookup from knowledge base
- **PROCEDURAL**: Questions about processes, workflows, or how-to steps
    - Example: "How do I configure the authentication module?"
    - May require multiple document categories
- **COMPARATIVE**: Queries comparing options, approaches, or versions
    - Example: "What's the difference between REST and GraphQL implementations?"
    - Requires synthesis across multiple sources
- **TRACEABILITY**: Questions linking requirements to implementations or tests
    - Example: "Which components implement requirement REQ-001?"
    - Requires cross-referencing multiple artifact types
- **GAP_ANALYSIS**: Identifying missing information or coverage
    - Example: "Which requirements lack test coverage?"
    - Requires analysis agent and data correlation
- **IMPACT_ANALYSIS**: Assessing ripple effects of changes
    - Example: "What would be affected if we change the authentication protocol?"
    - Requires design and technical specs agents


#### Usage Pattern

```python
query_analysis = QueryAnalysis(
    query_type=QueryType.COMPARATIVE,
    primary_intent="compare authentication methods",
    # ...
)
```


***

### Complexity

```python
class Complexity(Enum):
    """Query complexity levels"""
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"
    MULTI_FACETED = "multi_faceted"
```


#### Purpose

Indicates computational and agent coordination requirements for a query.

#### Values

- **SIMPLE**: Single fact lookup, single agent, minimal processing
    - Example: "What is the API version?"
- **MEDIUM**: Multiple document chunks, single or two agents
    - Example: "List all authentication methods supported"
- **COMPLEX**: Multiple agents, sequential dependencies, synthesis required
    - Example: "Explain the end-to-end payment flow"
- **MULTI_FACETED**: Requires orchestration, multiple agent types, conflict resolution
    - Example: "Analyze security implications across all system components"


#### Workflow Implications

| Complexity | Agents | Workflow | Timeout |
| :-- | :-- | :-- | :-- |
| SIMPLE | 1 | Direct | ~5s |
| MEDIUM | 1-2 | Parallel | ~15s |
| COMPLEX | 2-4 | Sequential/Parallel | ~30s |
| MULTI_FACETED | 3+ | Hybrid | ~60s |


***

### ConfidenceLevel

```python
class ConfidenceLevel(Enum):
    """Confidence levels for agent responses"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
```


#### Purpose

Quantifies agent certainty in responses based on source quality, completeness, and consistency.

#### Interpretation Guidelines

- **HIGH**:
    - Multiple sources agree
    - High semantic similarity scores (>0.8)
    - Complete information retrieved
    - No contradictions found
- **MEDIUM**:
    - Limited sources or single source
    - Moderate similarity scores (0.5-0.8)
    - Partial information
    - Minor ambiguities
- **LOW**:
    - Weak source matches (<0.5)
    - Incomplete information
    - Conflicting evidence
    - Out-of-scope query


#### Usage in Decision Logic

```python
if response.confidence == ConfidenceLevel.LOW:
    # Trigger human escalation or suggest query refinement
    suggest_reformulation(response)
elif response.confidence == ConfidenceLevel.HIGH:
    # Directly present answer
    return response.content
```


***

## Data Classes

### AgentContext

```python
@dataclass
class AgentContext:
    """Shared context across all agents"""
    project_id: int
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    current_query: str = ""
    query_metadata: Dict[str, Any] = field(default_factory=dict)
```


#### Purpose

Encapsulates shared state and context that flows through the agent system during query processing.

#### Attributes

- **project_id: int** (required)
    - Unique identifier for the project being queried
    - Used to scope document retrieval and permissions
    - Example: `42`
- **conversation_history: List[Dict[str, str]]**
    - Ordered list of previous messages in the conversation
    - Each message has `"role"` and `"content"` keys
    - Enables context-aware follow-up questions
    - Default: Empty list
- **user_preferences: Dict[str, Any]**
    - User-specific settings (verbosity, format preferences, language)
    - Example: `{"detail_level": "concise", "include_examples": True}`
    - Default: Empty dict
- **current_query: str**
    - The active user query being processed
    - Updated by orchestrator for each new query
    - Default: Empty string
- **query_metadata: Dict[str, Any]**
    - Additional query-specific data (timestamp, session_id, filters)
    - Example: `{"timestamp": "2025-12-30T14:25:00Z", "category_filter": ["design"]}`
    - Default: Empty dict


#### Methods

##### add_message()

```python
def add_message(self, role: str, content: str):
    """Add a message to conversation history"""
    self.conversation_history.append({
        "role": role,
        "content": content
    })
```

**Parameters**:

- `role`: Either `"user"`, `"assistant"`, or `"system"`
- `content`: The message text

**Purpose**: Maintains conversation continuity for context-aware responses

**Example**:

```python
context = AgentContext(project_id=123)
context.add_message("user", "What are the API endpoints?")
context.add_message("assistant", "The system exposes 5 REST endpoints...")
context.add_message("user", "Tell me more about the authentication endpoint")
# Agent can now reference "authentication endpoint" with full context
```


***

### Source

```python
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
```


#### Purpose

Represents a single evidence source retrieved from the document knowledge base, used for citation and traceability.

#### Attributes

- **chunk_id: int** (required)
    - Unique identifier for the text chunk
    - Used for deduplication and retrieval
- **document_id: int** (required)
    - Parent document identifier
    - Links chunk to original file
- **filename: str** (required)
    - Original document filename
    - Example: `"API_Design_v2.3.pdf"`
- **category_name: str** (required)
    - Document category/type
    - Example: `"design"`, `"requirements"`, `"technical_specs"`
- **chunk_text: str** (required)
    - The actual text content of the chunk
    - Full text used by agents for analysis
- **page_number: Optional[int]**
    - Page number in original document (if applicable)
    - `None` for non-paginated sources (markdown, code files)
- **metadata: Dict[str, Any]**
    - Additional source information
    - Example: `{"section": "Authentication", "author": "John Doe", "last_modified": "2025-12-01"}`
- **similarity_score: float**
    - Semantic similarity score from vector search (0.0-1.0)
    - Higher scores indicate better relevance
    - Default: `0.0`


#### Usage Pattern

```python
source = Source(
    chunk_id=12345,
    document_id=789,
    filename="requirements.pdf",
    category_name="requirements",
    chunk_text="The system shall support OAuth 2.0 authentication...",
    page_number=15,
    similarity_score=0.92
)
```


***

### AgentResponse

```python
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
```


#### Purpose

Standardizes the output structure from all specialized agents, enabling orchestrator aggregation and conflict resolution.

#### Attributes

- **agent_id: str** (required)
    - Unique agent identifier
    - Example: `"requirements_agent"`
- **agent_name: str** (required)
    - Human-readable agent name
    - Example: `"Requirements Analysis Agent"`
- **content: str** (required)
    - The agent's generated response/answer
    - Natural language text, may include markdown formatting
- **confidence: ConfidenceLevel** (required)
    - Agent's confidence in the response
    - Enum value: `HIGH`, `MEDIUM`, or `LOW`
- **sources: List[Source]** (required)
    - Evidence supporting the response
    - Ordered by relevance (highest similarity first)
- **metadata: Dict[str, Any]**
    - Agent-specific diagnostic information
    - Example: `{"model_used": "llama3.1:8b", "temperature": 0.1, "tokens": 450}`
- **requires_followup: bool**
    - Indicates if query is incomplete or ambiguous
    - Triggers clarification prompts
    - Default: `False`
- **suggested_agents: List[str]**
    - Other agents that should be consulted
    - Example: `["design_agent", "tech_specs_agent"]`
    - Empty list if none suggested
- **processing_time_ms: int**
    - Time taken by agent to generate response (milliseconds)
    - Used for performance monitoring
    - Default: `0`


#### Methods

##### to_dict()

```python
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
```

**Purpose**: Serializes response for JSON API output or logging

**Key Behaviors**:

- Converts `ConfidenceLevel` enum to string via `.value`
- Truncates source text to 200 characters for display efficiency
- Flattens nested `Source` objects into simple dictionaries
- Preserves all essential metadata

**Example Output**:

```json
{
  "agent_id": "requirements_agent",
  "agent_name": "Requirements Agent",
  "content": "The system supports OAuth 2.0 and SAML 2.0 authentication.",
  "confidence": "high",
  "sources": [
    {
      "chunk_id": 42,
      "filename": "requirements.pdf",
      "category": "requirements",
      "text": "REQ-AUTH-001: The system shall support OAuth 2.0 authentication with refresh tokens...",
      "page": 12,
      "score": 0.94
    }
  ],
  "metadata": {"tokens": 380},
  "suggested_agents": [],
  "processing_time_ms": 1250
}
```


***

### QueryAnalysis

```python
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
    suggested_workflow: str = "parallel"
```


#### Purpose

Captures the orchestrator's understanding of a query, guiding agent selection and execution strategy.

#### Attributes

- **query_type: QueryType** (required)
    - Classification from `QueryType` enum
    - Determines base agent routing logic
- **primary_intent: str** (required)
    - Natural language description of what user wants
    - Example: `"Find all API endpoints related to payment processing"`
- **required_categories: List[str]** (required)
    - Document categories needed to answer query
    - Example: `["requirements", "design", "technical_specs"]`
- **complexity: Complexity** (required)
    - Query complexity level from `Complexity` enum
    - Affects timeout and orchestration strategy
- **requires_multiple_agents: bool** (required)
    - Whether query needs coordination across multiple agents
    - `True` triggers orchestrator's multi-agent workflow
- **key_entities: Dict[str, Any]**
    - Extracted entities from the query
    - Example: `{"component": "payment_service", "operation": "refund", "version": "2.0"}`
    - Used for filtering and context enrichment
- **temporal_scope: str**
    - Time-related aspect of query
    - Values: `"current"`, `"historical"`, `"future"`, `"all"`
    - Default: `"current"`
- **suggested_workflow: str**
    - Orchestration strategy recommendation
    - Values: `"parallel"`, `"sequential"`, `"hybrid"`
    - Default: `"parallel"`


#### Methods

##### from_dict()

```python
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
```

**Purpose**: Factory method for deserializing query analysis from JSON/dict (e.g., from cache or API)

**Parameters**:

- `data`: Dictionary with query analysis fields
- Missing fields receive defaults

**Returns**: Fully constructed `QueryAnalysis` instance

**Example**:

```python
data = {
    "query_type": "comparative",
    "primary_intent": "compare REST vs GraphQL",
    "required_categories": ["design"],
    "complexity": "medium",
    "requires_multiple_agents": False
}
analysis = QueryAnalysis.from_dict(data)
```


***

### OrchestratorResponse

```python
@dataclass
class OrchestratorResponse:
    """Final response from the orchestrator"""
    answer: str
    confidence: ConfidenceLevel
    sources: List[Source]
    agents_consulted: List[str]
    agent_agreement: str = "full"
    key_insights: List[str] = field(default_factory=list)
    conflicts: Optional[str] = None
    processing_time_ms: int = 0
```


#### Purpose

Represents the final synthesized answer after orchestrator aggregates and resolves responses from multiple agents.

#### Attributes

- **answer: str** (required)
    - The final, synthesized natural language answer
    - Combines information from all consulted agents
    - May include citations or inline references
- **confidence: ConfidenceLevel** (required)
    - Overall confidence in the final answer
    - Derived from individual agent confidences and agreement level
- **sources: List[Source]** (required)
    - All unique sources cited across all agent responses
    - Deduplicated by `chunk_id`
    - Sorted by relevance
- **agents_consulted: List[str]** (required)
    - IDs of agents that contributed to the response
    - Example: `["requirements_agent", "design_agent"]`
- **agent_agreement: str**
    - Level of consensus among agents
    - Values: `"full"`, `"partial"`, `"conflicting"`
    - Default: `"full"`
- **key_insights: List[str]**
    - Bullet-point highlights or takeaways
    - Example: `["OAuth 2.0 is the primary auth method", "SAML 2.0 supported for enterprise SSO"]`
    - Empty list if none extracted
- **conflicts: Optional[str]**
    - Description of any contradictions found between agents
    - `None` if agents agree
    - Example: `"Requirements agent found OAuth 2.0 only, but design doc mentions SAML"`
- **processing_time_ms: int**
    - Total time for orchestration and all agents (milliseconds)
    - Includes network, computation, and aggregation time
    - Default: `0`


#### Methods

##### to_dict()

```python
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
```

**Purpose**: Serializes orchestrator response for API response body

**Key Behaviors**:

- Converts enums to strings
- Truncates source text to 200 characters
- Omits similarity scores (not needed in final response)
- Preserves conflict information for transparency

**Example Output**:

```json
{
  "answer": "The system supports both OAuth 2.0 and SAML 2.0 for authentication...",
  "confidence": "high",
  "sources": [
    {
      "chunk_id": 42,
      "filename": "requirements.pdf",
      "category": "requirements",
      "text": "REQ-AUTH-001: The system shall support OAuth 2.0...",
      "page": 12
    }
  ],
  "agents_consulted": ["requirements_agent", "design_agent"],
  "agent_agreement": "full",
  "key_insights": [
    "OAuth 2.0 is the primary method",
    "SAML 2.0 available for enterprise integration"
  ],
  "conflicts": null,
  "processing_time_ms": 3450
}
```


***

## Design Patterns and Best Practices

### Type Safety

All classes use comprehensive type hints enabling:

- IDE auto-completion and inline documentation
- Static analysis with `mypy`
- Runtime validation with libraries like `pydantic` (future enhancement)


### Immutability

Dataclasses are not frozen but should be treated as immutable after creation:

- Create new instances rather than mutating existing ones
- Simplifies debugging and testing
- Prevents unintended side effects in multi-agent workflows


### Factory Methods

The `from_dict()` classmethod pattern enables:

- Easy deserialization from JSON/database
- Default value handling for missing fields
- Type conversion (string enum values to enum instances)


### Serialization

Both `AgentResponse` and `OrchestratorResponse` include `to_dict()` methods:

- Consistent JSON structure across API
- Explicit truncation of verbose fields (chunk text)
- Enum-to-string conversion for JSON compatibility

***

## Integration Examples

### Creating Context for a New Query

```python
context = AgentContext(
    project_id=123,
    current_query="What authentication methods are supported?",
    query_metadata={
        "session_id": "abc-123",
        "timestamp": "2025-12-30T14:30:00Z"
    }
)
```


### Agent Generating a Response

```python
response = AgentResponse(
    agent_id="requirements_agent",
    agent_name="Requirements Agent",
    content="The system supports OAuth 2.0 and SAML 2.0.",
    confidence=ConfidenceLevel.HIGH,
    sources=[source1, source2],
    metadata={"model": "llama3.1:8b", "temperature": 0.3},
    processing_time_ms=1250
)
```


### Orchestrator Building Final Response

```python
orchestrator_response = OrchestratorResponse(
    answer="Based on requirements and design documents, the system supports OAuth 2.0 as the primary authentication method and SAML 2.0 for enterprise SSO integration.",
    confidence=ConfidenceLevel.HIGH,
    sources=deduplicated_sources,
    agents_consulted=["requirements_agent", "design_agent"],
    agent_agreement="full",
    key_insights=[
        "OAuth 2.0 with refresh tokens",
        "SAML 2.0 for enterprise customers"
    ],
    processing_time_ms=3450
)

# Serialize for API
response_json = orchestrator_response.to_dict()
```


### Query Analysis Workflow

```python
analysis = QueryAnalysis(
    query_type=QueryType.FACTUAL,
    primary_intent="retrieve authentication methods",
    required_categories=["requirements", "design"],
    complexity=Complexity.SIMPLE,
    requires_multiple_agents=False,
    key_entities={"domain": "authentication"}
)

if analysis.complexity == Complexity.SIMPLE:
    # Single agent, fast path
    response = requirements_agent.process(context)
else:
    # Multi-agent orchestration
    response = orchestrator.coordinate(context, analysis)
```


***

## Testing Recommendations

### Unit Testing Data Classes

```python
def test_agent_response_to_dict():
    source = Source(
        chunk_id=1,
        document_id=10,
        filename="test.pdf",
        category_name="requirements",
        chunk_text="A" * 300,  # Long text
        similarity_score=0.95
    )
    
    response = AgentResponse(
        agent_id="test_agent",
        agent_name="Test Agent",
        content="Test content",
        confidence=ConfidenceLevel.HIGH,
        sources=[source],
        processing_time_ms=100
    )
    
    result = response.to_dict()
    
    assert result["confidence"] == "high"
    assert len(result["sources"][0]["text"]) == 200  # Truncated
    assert result["sources"][0]["score"] == 0.95
```


### Testing Enums

```python
def test_query_type_values():
    assert QueryType.FACTUAL.value == "factual"
    assert QueryType.IMPACT_ANALYSIS.value == "impact_analysis"
    
    # Test enum from string
    qt = QueryType("comparative")
    assert qt == QueryType.COMPARATIVE
```


### Testing Factory Methods

```python
def test_query_analysis_from_dict():
    data = {
        "query_type": "traceability",
        "primary_intent": "find linked components",
        "required_categories": ["requirements", "design"],
        "complexity": "complex",
        "requires_multiple_agents": True
    }
    
    analysis = QueryAnalysis.from_dict(data)
    
    assert analysis.query_type == QueryType.TRACEABILITY
    assert analysis.complexity == Complexity.COMPLEX
    assert analysis.temporal_scope == "current"  # Default value
```


***

## Future Enhancement Opportunities

### Pydantic Integration

Replace `@dataclass` with `pydantic.BaseModel` for:

- Automatic validation of field types and constraints
- Built-in JSON serialization/deserialization
- OpenAPI schema generation for API documentation


### Confidence Score Quantification

Replace `ConfidenceLevel` enum with a float (0.0-1.0) for:

- More granular confidence tracking
- Weighted aggregation in orchestrator
- Statistical confidence intervals


### Source Provenance Chain

Extend `Source` to track:

- Original document version/hash
- Extraction timestamp
- Transformation history (chunking, embedding, indexing)


### Query Analysis Caching

Add fields to `QueryAnalysis` for:

- Cache key generation
- Time-to-live (TTL) for cached analyses
- Version tracking for invalidation


### Agent Response Versioning

Add version field to `AgentResponse` for:

- A/B testing different agent implementations
- Backward compatibility during upgrades
- Response replay for debugging

