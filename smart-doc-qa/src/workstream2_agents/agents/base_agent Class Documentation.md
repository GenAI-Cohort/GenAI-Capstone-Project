# BaseAgent Class Documentation

The `agents/base_agent.py` module defines the abstract base class that serves as the foundation for all specialized document analysis agents in the workstream2 agent framework.

## Module Overview

The `BaseAgent` class provides a comprehensive template and shared functionality for creating specialized agents that analyze specific document categories (requirements, design, technical specs, etc.). It implements the core agent lifecycle including context retrieval, prompt construction, LLM interaction, response parsing, and error handling.

### Design Philosophy

- **Abstract Base Class Pattern**: Uses Python's ABC (Abstract Base Class) to enforce implementation of key methods in subclasses
- **Template Method Pattern**: Defines the overall query processing workflow while allowing customization of specific steps
- **Separation of Concerns**: Isolates prompt engineering, LLM communication, and response parsing into distinct methods
- **Error Resilience**: Comprehensive exception handling with graceful degradation
- **Logging First**: Extensive logging at INFO, WARNING, and ERROR levels for observability

***

## Dependencies and Imports

### Standard Library

- **json**: Parses LLM responses expected in JSON format
- **logging**: Provides debug and operational logging throughout agent lifecycle
- **time**: Measures processing time for performance monitoring
- **abc**: Imports `ABC` and `abstractmethod` for abstract base class definition
- **typing**: Provides type hints (`List`, `Dict`, `Any`, `Optional`) for type safety


### Path Setup

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

Adds parent directory to `sys.path` to enable relative imports during development.

### Internal Dependencies

- **agents.data_models**: Imports core data structures
    - `AgentContext`: Shared context across agents
    - `AgentResponse`: Standardized response format
    - `ConfidenceLevel`: Confidence enum
    - `Source`: Document source representation
- **utils.ollama_client**: Imports LLM client
    - `ollama_client`: Pre-configured global client instance
    - `OllamaException`: Custom exception for LLM errors
- **config.settings**: Imports configuration object
    - `settings`: Global settings instance for model configuration


### Logging Configuration

```python
logger = logging.getLogger(__name__)
```

Creates a module-level logger following Python best practices. Logger name will be `agents.base_agent` in the log hierarchy.

***

## BaseAgent Class

```python
class BaseAgent(ABC):
    """Base class for all specialized agents"""
```


### Purpose

Provides a reusable foundation for all document category agents, ensuring consistent behavior, interface, and integration patterns.

***

## Constructor

```python
def __init__(
    self,
    agent_id: str,
    name: str,
    category_id: int,
    llm_model: str = None,
    temperature: float = 0.1
)
```


### Parameters

- **agent_id: str** (required)
    - Unique identifier for the agent
    - Example: `"requirements_agent"`, `"design_agent"`
    - Used in logging and response tracking
- **name: str** (required)
    - Human-readable agent name
    - Example: `"Requirements Analysis Agent"`, `"Design Documentation Agent"`
    - Displayed in responses and logs
- **category_id: int** (required)
    - Database identifier for the document category this agent specializes in
    - Links agent to its specific knowledge domain
    - Example: `1` for requirements, `2` for design
- **llm_model: str** (optional)
    - Name of the LLM model to use (e.g., `"llama3.1:8b"`, `"mistral:7b"`)
    - Falls back to `settings.OLLAMA_MODEL` if not provided
    - Allows per-agent model customization
- **temperature: float** (optional)
    - Controls LLM output randomness (0.0-1.0)
    - Default: `0.1` (highly deterministic, appropriate for factual retrieval)
    - Lower values produce more consistent, focused outputs


### Instance Attributes

After initialization, the agent has these attributes:

- `self.agent_id`: Stored agent identifier
- `self.name`: Stored agent name
- `self.category_id`: Stored category identifier
- `self.llm_model`: Model name (from parameter or settings)
- `self.temperature`: Temperature setting
- `self.llm_client`: Reference to global `ollama_client` instance


### Logging

Logs initialization message at INFO level:

```
INFO: Initialized Requirements Analysis Agent (ID: requirements_agent)
```


### Example Usage

```python
class RequirementsAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="requirements_agent",
            name="Requirements Analysis Agent",
            category_id=1,
            temperature=0.1
        )
```


***

## Abstract Methods

Subclasses **must** implement these methods.

### get_system_prompt()

```python
@abstractmethod
def get_system_prompt(self) -> str:
    """
    Define agent's personality and expertise
    Must be implemented by each specialized agent
    """
    pass
```


#### Purpose

Returns the system prompt that defines the agent's role, expertise, and behavior guidelines.

#### Returns

- **str**: Multi-line system prompt text


#### Implementation Guidelines

The system prompt should:

- Define the agent's domain expertise and role
- Specify expected output format and structure
- Include guidelines for citing sources
- Set the tone and verbosity level
- Provide constraints and boundaries


#### Example Implementation

```python
def get_system_prompt(self) -> str:
    return """You are a Requirements Analysis Expert specializing in software requirements documents.

Your expertise includes:
- Functional and non-functional requirements analysis
- Requirements traceability and validation
- Identifying ambiguities and conflicts in requirements

When answering queries:
1. Cite specific requirement IDs when available
2. Distinguish between mandatory (SHALL) and optional (SHOULD) requirements
3. Flag any ambiguous or incomplete requirements
4. Provide confidence levels based on source clarity

Format: Professional, precise, and structured."""
```


***

### can_handle_query()

```python
@abstractmethod
def can_handle_query(self, query: str, context: AgentContext) -> float:
    """
    Determine if this agent should handle the query
    
    Args:
        query: User query
        context: Agent context
    
    Returns:
        Confidence score 0.0-1.0
    """
    pass
```


#### Purpose

Calculates a relevance score indicating how well this agent can answer the query based on its domain expertise.

#### Parameters

- **query: str**: The user's query text
- **context: AgentContext**: Shared context including conversation history


#### Returns

- **float**: Confidence score between 0.0 and 1.0
    - `0.0-0.3`: Low relevance, probably not the right agent
    - `0.3-0.7`: Medium relevance, could contribute partial information
    - `0.7-1.0`: High relevance, primary agent for this query


#### Implementation Strategies

**Keyword Matching** (simple):

```python
def can_handle_query(self, query: str, context: AgentContext) -> float:
    keywords = ["requirement", "functional", "non-functional", "shall", "must"]
    return self._calculate_keyword_score(query, keywords)
```

**ML-based Classification** (advanced):

```python
def can_handle_query(self, query: str, context: AgentContext) -> float:
    # Use trained classifier or semantic similarity
    embedding = self.embedder.encode(query)
    similarity = cosine_similarity(embedding, self.domain_embedding)
    return float(similarity)
```

**Rule-based Heuristics** (hybrid):

```python
def can_handle_query(self, query: str, context: AgentContext) -> float:
    query_lower = query.lower()
    
    # High confidence triggers
    if any(phrase in query_lower for phrase in ["requirements", "req-", "functional spec"]):
        return 0.9
    
    # Medium confidence triggers
    if any(word in query_lower for word in ["feature", "capability", "constraint"]):
        return 0.6
    
    # Low confidence default
    return 0.2
```


***

## Core Methods

### retrieve_context()

```python
def retrieve_context(
    self,
    query: str,
    context: AgentContext,
    top_k: int = 5
) -> List[Source]:
    """
    Retrieve relevant documents from this agent's category
    
    NOTE: This is a placeholder. Will be integrated with Workstream 1
    retrieval system later.
    
    Args:
        query: User query
        context: Agent context
        top_k: Number of results to retrieve
    
    Returns:
        List of Source objects
    """
```


#### Purpose

Retrieves the most relevant document chunks from the agent's specialized category to provide context for answering the query.

#### Parameters

- **query: str**: User's query text
- **context: AgentContext**: Shared agent context
- **top_k: int**: Maximum number of sources to retrieve (default: 5)


#### Returns

- **List[Source]**: Ordered list of relevant document chunks, sorted by relevance (highest first)


#### Current Implementation

**Status**: Mock implementation pending Workstream 1 integration

Currently returns a single mock source:

```python
return [
    Source(
        chunk_id=1,
        document_id=1,
        filename=f"mock_doc_{self.category_id}.pdf",
        category_name=self.name,
        chunk_text=f"Mock content related to: {query}",
        page_number=1,
        metadata={},
        similarity_score=0.85
    )
]
```

Logs warning: `"Using mock retrieval (integration pending)"`

#### Future Integration

Will connect to Workstream 1's vector database and retrieval pipeline:

```python
def retrieve_context(self, query: str, context: AgentContext, top_k: int = 5) -> List[Source]:
    # Generate query embedding
    query_embedding = self.embedding_service.embed_query(query)
    
    # Search vector database for this category
    results = self.vector_db.search(
        embedding=query_embedding,
        category_id=self.category_id,
        project_id=context.project_id,
        top_k=top_k,
        filters=context.query_metadata.get("filters", {})
    )
    
    # Convert to Source objects
    return [self._result_to_source(r) for r in results]
```


#### Customization Points

Subclasses can override this method to implement specialized retrieval logic:

- Filter by document metadata (author, date range, version)
- Apply category-specific re-ranking
- Combine vector search with keyword filters
- Implement hybrid retrieval strategies

***

### process_query()

```python
def process_query(
    self,
    query: str,
    context: AgentContext,
    retrieved_context: Optional[List[Source]] = None
) -> AgentResponse:
    """
    Main processing logic for the agent
    
    Args:
        query: User query
        context: Agent context
        retrieved_context: Pre-retrieved context (optional)
    
    Returns:
        AgentResponse with answer and metadata
    """
```


#### Purpose

Orchestrates the complete query processing workflow from context retrieval through response generation. This is the main entry point for agent execution.

#### Parameters

- **query: str** (required): The user's query text
- **context: AgentContext** (required): Shared context with conversation history and metadata
- **retrieved_context: Optional[List[Source]]**: Pre-retrieved sources (if already available from orchestrator)


#### Returns

- **AgentResponse**: Structured response including answer, confidence, sources, and metadata


#### Workflow Steps

**Step 1: Context Retrieval**

If `retrieved_context` is not provided, calls `retrieve_context()` to fetch relevant documents.

```python
if retrieved_context is None:
    logger.info(f"{self.name}: Retrieving context for query")
    retrieved_context = self.retrieve_context(query, context)
```

**Step 2: Prompt Construction**

Builds the complete prompt by calling `_build_prompt()`, which combines:

- System prompt (agent personality)
- Conversation history
- Retrieved context
- Current query
- Output format instructions

**Step 3: LLM Generation**

Calls the LLM via `_call_llm()` to generate a response.

**Step 4: Response Parsing**

Parses the LLM's JSON output into an `AgentResponse` object via `_parse_response()`.

**Step 5: Timing and Logging**

Calculates processing time and adds it to the response:

```python
response.processing_time_ms = int((time.time() - start_time) * 1000)
logger.info(f"{self.name}: Response generated ({response.processing_time_ms}ms)")
```


#### Error Handling

Comprehensive exception handling returns a LOW-confidence error response if any step fails:

```python
except Exception as e:
    logger.error(f"{self.name}: Error processing query: {e}")
    return AgentResponse(
        agent_id=self.agent_id,
        agent_name=self.name,
        content=f"Error: {str(e)}",
        confidence=ConfidenceLevel.LOW,
        sources=[],
        metadata={"error": str(e)},
        processing_time_ms=int((time.time() - start_time) * 1000)
    )
```

This ensures the orchestrator always receives a valid response and can handle failures gracefully.

#### Example Usage

```python
# Simple usage
response = agent.process_query("What are the authentication requirements?", context)

# With pre-fetched context (orchestrator pattern)
sources = orchestrator.batch_retrieve(query, [agent1, agent2, agent3])
response = agent.process_query(query, context, retrieved_context=sources[agent.category_id])
```


***

## Private Helper Methods

These methods support the main workflow and can be overridden by subclasses for customization.

### _build_prompt()

```python
def _build_prompt(
    self,
    query: str,
    retrieved_context: List[Source],
    context: AgentContext
) -> str:
    """Build the prompt for LLM"""
```


#### Purpose

Constructs the complete prompt sent to the LLM by assembling all necessary components.

#### Parameters

- **query: str**: The user's query
- **retrieved_context: List[Source]**: Retrieved document chunks
- **context: AgentContext**: Shared context


#### Returns

- **str**: Complete multi-part prompt


#### Prompt Structure

The prompt includes these sections:

1. **System Prompt**: Agent personality and expertise (from `get_system_prompt()`)
2. **Conversation History**: Last 5 messages for context continuity
3. **Retrieved Context**: Formatted source documents with citations
4. **Current Query**: The user's question
5. **Output Instructions**: JSON format specification with required fields

#### JSON Output Schema

The prompt instructs the LLM to return:

```json
{
  "answer": "detailed answer with [Source N] citations",
  "confidence": "high|medium|low",
  "key_sources": ["brief description of key sources"],
  "suggests_consulting": ["agent_name1", "agent_name2"],
  "reasoning": "why you're suggesting other agents if any"
}
```


#### Key Features

- **Source Citation**: Instructs LLM to cite sources as `[Source N]` where N is 1-indexed
- **Confidence Self-Assessment**: Asks LLM to estimate its own confidence level
- **Cross-Agent Suggestions**: Enables agents to recommend consulting other agents
- **JSON-Only Output**: Explicitly requires "ONLY valid JSON, no other text"


#### Example Output

```
You are a Requirements Analysis Expert...

CONVERSATION HISTORY:
USER: What authentication methods are supported?
ASSISTANT: The system supports OAuth 2.0 and SAML 2.0.
USER: What are the specific requirements for OAuth?

RELEVANT CONTEXT FROM REQUIREMENTS ANALYSIS AGENT:
[Source 1] - requirements_v2.3.pdf (Page 12)
REQ-AUTH-001: The system shall support OAuth 2.0...
---
[Source 2] - requirements_v2.3.pdf (Page 13)
REQ-AUTH-002: OAuth tokens shall expire after 1 hour...

CURRENT QUERY:
What are the specific requirements for OAuth?

Please provide a response that:
1. Answers the query using the context provided
2. Cites specific sources with [Source N] notation
...

IMPORTANT: Return ONLY valid JSON, no other text.

RESPONSE:
```


***

### _format_context()

```python
def _format_context(self, sources: List[Source]) -> str:
    """Format retrieved sources for prompt"""
```


#### Purpose

Converts a list of `Source` objects into a readable, numbered format for inclusion in the prompt.

#### Parameters

- **sources: List[Source]**: Retrieved document chunks


#### Returns

- **str**: Formatted context text with source numbering


#### Format Pattern

Each source is formatted as:

```
[Source 1] - filename.pdf (Page 15)
<chunk text content>
Metadata: {"author": "John Doe", "version": "2.3"}
---

[Source 2] - design_doc.md (Page N/A)
<chunk text content>
Metadata: None
---
```


#### Special Cases

- Returns `"No relevant context found."` if sources list is empty
- Shows `"Page N/A"` if `page_number` is None (for non-paginated sources)
- Shows `"Metadata: None"` if metadata dict is empty


#### Source Numbering

Sources are numbered starting from 1, matching the citation format `[Source N]` in the LLM's response.

***

### _format_conversation_history()

```python
def _format_conversation_history(self, history: List[Dict]) -> str:
    """Format conversation history"""
```


#### Purpose

Converts conversation history into a readable format for prompt inclusion.

#### Parameters

- **history: List[Dict]**: List of message dictionaries with `"role"` and `"content"` keys


#### Returns

- **str**: Formatted conversation history


#### Behavior

- Returns `"No previous conversation."` if history is empty
- **Limits to last 5 messages** to keep prompt size manageable
- Formats each message as: `ROLE: content\n`


#### Example Output

```
USER: What are the authentication requirements?
ASSISTANT: The system supports OAuth 2.0 and SAML 2.0.
USER: What about token expiration?
ASSISTANT: OAuth tokens expire after 1 hour per REQ-AUTH-002.
USER: Are there any refresh token requirements?
```


#### Rationale

Limiting to 5 messages balances:

- Sufficient context for follow-up questions
- Avoiding token limits and prompt bloat
- Focusing on recent, relevant conversation

***

### _call_llm()

```python
def _call_llm(self, prompt: str, context: AgentContext) -> str:
    """
    Call LLM with prompt
    
    Args:
        prompt: Full prompt
        context: Agent context
    
    Returns:
        Generated text
    """
```


#### Purpose

Handles the actual LLM API call with error handling.

#### Parameters

- **prompt: str**: Complete prompt to send
- **context: AgentContext**: Shared context (currently unused but available for future enhancements)


#### Returns

- **str**: Raw LLM response text


#### Implementation

```python
try:
    response = self.llm_client.generate(
        prompt=prompt,
        temperature=self.temperature
    )
    return response
except OllamaException as e:
    logger.error(f"{self.name}: LLM call failed: {e}")
    raise
```


#### Error Handling

- Catches `OllamaException` (timeouts, connection errors, HTTP errors)
- Logs error with agent name for debugging
- Re-raises exception to be caught by `process_query()`


#### Future Enhancements

Could leverage `context` for:

- Dynamic temperature adjustment based on query complexity
- Retry logic with exponential backoff
- Fallback to backup model on failure
- Token usage tracking and limits

***

### _parse_response()

```python
def _parse_response(
    self,
    llm_response: str,
    retrieved_context: List[Source]
) -> AgentResponse:
    """Parse LLM response into structured format"""
```


#### Purpose

Converts the LLM's JSON response into a structured `AgentResponse` object.

#### Parameters

- **llm_response: str**: Raw text from LLM (expected to be JSON)
- **retrieved_context: List[Source]**: Original sources (attached to response for traceability)


#### Returns

- **AgentResponse**: Structured response object


#### Parsing Logic

**Step 1: Clean Response**

Removes markdown code block markers if present:

```python
cleaned = llm_response.strip()
if cleaned.startswith("```
    cleaned = cleaned[7:]
if cleaned.startswith("```"):
    cleaned = cleaned[3:]
if cleaned.endswith("```
    cleaned = cleaned[:-3]
cleaned = cleaned.strip()
```

This handles cases where the LLM wraps JSON in markdown despite instructions.[page:0]

**Step 2: Parse JSON**[page:0]

```
parsed = json.loads(cleaned)
```

**Step 3: Map Confidence**[page:0]

Converts string confidence to enum:[page:0]

```
confidence_str = parsed.get("confidence", "medium").lower()
confidence_map = {
    "high": ConfidenceLevel.HIGH,
    "medium": ConfidenceLevel.MEDIUM,
    "low": ConfidenceLevel.LOW
}
confidence = confidence_map.get(confidence_str, ConfidenceLevel.MEDIUM)
```

Defaults to `MEDIUM` if confidence string is unrecognized.[page:0]

**Step 4: Build AgentResponse**[page:0]

```
return AgentResponse(
    agent_id=self.agent_id,
    agent_name=self.name,
    content=parsed.get("answer", ""),
    confidence=confidence,
    sources=retrieved_context,
    metadata={
        "key_sources": parsed.get("key_sources", []),
        "reasoning": parsed.get("reasoning", "")
    },
    suggested_agents=parsed.get("suggests_consulting", [])
)
```


#### Error Handling

**JSON Parse Failures**:[page:0]

If JSON parsing fails, returns a fallback response with raw LLM output:[page:0]

```
except json.JSONDecodeError as e:
    logger.error(f"{self.name}: Failed to parse JSON response: {e}")
    logger.debug(f"Response was: {llm_response[:200]}")
    
    return AgentResponse(
        agent_id=self.agent_id,
        agent_name=self.name,
        content=llm_response,  # Raw text
        confidence=ConfidenceLevel.LOW,
        sources=retrieved_context,
        metadata={"parse_error": str(e)}
    )
```

This ensures:[page:0]

- User still sees the LLM's response (even if not properly formatted)
- Confidence is marked LOW to signal issues
- Error is tracked in metadata for debugging


#### Logging

- Logs parse errors at ERROR level
- Logs first 200 characters of problematic response at DEBUG level for troubleshooting[page:0]

---

### _calculate_keyword_score()

```
def _calculate_keyword_score(self, query: str, keywords: List[str]) -> float:
    """
    Helper method to calculate relevance score based on keywords
    
    Args:
        query: User query
        keywords: List of keywords to check
    
    Returns:
        Score between 0.0 and 1.0
    """
```


#### Purpose

Provides a simple keyword-based relevance scoring mechanism for implementing `can_handle_query()`.[page:0]

#### Parameters

- **query: str**: User's query text
- **keywords: List[str]**: Keywords relevant to this agent's domain


#### Returns

- **float**: Relevance score between 0.0 and 1.0


#### Algorithm

1. Convert query to lowercase for case-insensitive matching[page:0]
2. Count how many keywords appear in the query[page:0]
3. Calculate score using formula: `min(0.3 + (matches * 0.15), 1.0)`[page:0]

#### Scoring Table

| Matches | Score |
| :-- | :-- |
| 0 | 0.0 |
| 1 | 0.45 |
| 2 | 0.60 |
| 3 | 0.75 |
| 4 | 0.90 |
| 5+ | 1.0 (capped) |

#### Example Usage

```
class RequirementsAgent(BaseAgent):
    def can_handle_query(self, query: str, context: AgentContext) -> float:
        keywords = [
            "requirement", "functional", "non-functional",
            "shall", "must", "req-", "specification"
        ]
        return self._calculate_keyword_score(query, keywords)
```

Example queries:[page:0]

- `"What are the functional requirements?"` → 2 matches → 0.60
- `"Show me requirement REQ-001"` → 2 matches → 0.60
- `"Explain the authentication requirements and specifications"` → 2 matches → 0.60


#### Limitations

- Simple substring matching (no stemming or lemmatization)
- Doesn't consider keyword importance/weights
- No phrase matching
- Can have false positives (e.g., "design requirement" matches in design agent)


#### Recommended Enhancements

For production use, consider:[page:0]

- TF-IDF scoring for keyword weighting
- Semantic similarity using embeddings
- Learned classifiers trained on labeled query-agent pairs
- Hybrid approaches combining multiple signals

---

## Subclass Implementation Guide

### Minimal Implementation

To create a specialized agent, implement these two abstract methods:[page:0]

```
from agents.base_agent import BaseAgent
from agents.data_models import AgentContext

class RequirementsAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="requirements_agent",
            name="Requirements Analysis Agent",
            category_id=1,  # Requirements category ID
            temperature=0.1
        )
    
    def get_system_prompt(self) -> str:
        return """You are a Requirements Analysis Expert.
        
        Analyze software requirements documents focusing on:
        - Functional requirements (REQ-FUNC-*)
        - Non-functional requirements (REQ-NFR-*)
        - Requirement clarity and testability
        - Traceability information
        
        Always cite specific requirement IDs."""
    
    def can_handle_query(self, query: str, context: AgentContext) -> float:
        keywords = [
            "requirement", "functional", "non-functional",
            "shall", "must", "req-", "specification"
        ]
        return self._calculate_keyword_score(query, keywords)
```


### Advanced Customization

Override additional methods for specialized behavior:[page:0]

```
class DesignAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="design_agent",
            name="Design Documentation Agent",
            category_id=2,
            temperature=0.2  # Slightly higher for design explanations
        )
    
    def retrieve_context(self, query: str, context: AgentContext, top_k: int = 5):
        # Custom retrieval with design-specific filters
        sources = super().retrieve_context(query, context, top_k)
        
        # Boost architectural diagrams and UML sources
        for source in sources:
            if any(ext in source.filename for ext in ['.uml', '.drawio', 'architecture']):
                source.similarity_score *= 1.2
        
        # Re-sort by boosted scores
        sources.sort(key=lambda s: s.similarity_score, reverse=True)
        return sources[:top_k]
    
    def _build_prompt(self, query, retrieved_context, context):
        # Add design-specific instructions
        base_prompt = super()._build_prompt(query, retrieved_context, context)
        
        design_addendum = """
        
        DESIGN-SPECIFIC GUIDELINES:
        - Reference component names and architectural layers
        - Explain design patterns used
        - Mention relevant UML diagrams
        - Consider design trade-offs
        """
        
        return base_prompt + design_addendum
```


---

## Error Handling Strategy

The BaseAgent implements comprehensive error handling at multiple levels:[page:0]

### Level 1: LLM Call Failures

`_call_llm()` catches `OllamaException` and re-raises after logging.[page:0]

### Level 2: Response Parsing Failures

`_parse_response()` catches `json.JSONDecodeError` and returns fallback response with raw LLM output.[page:0]

### Level 3: Top-Level Exception Handling

`process_query()` catches all exceptions and returns error response:[page:0]

```
except Exception as e:
    logger.error(f"{self.name}: Error processing query: {e}")
    return AgentResponse(
        agent_id=self.agent_id,
        agent_name=self.name,
        content=f"Error: {str(e)}",
        confidence=ConfidenceLevel.LOW,
        sources=[],
        metadata={"error": str(e)},
        processing_time_ms=int((time.time() - start_time) * 1000)
    )
```


### Design Benefits

- **Never crashes**: Always returns a valid `AgentResponse`
- **Transparent errors**: Error messages preserved in response content and metadata
- **Graceful degradation**: Low confidence signals to orchestrator that response is unreliable
- **Debuggable**: Comprehensive logging at each failure point

---

## Logging Strategy

The BaseAgent uses structured logging for observability:[page:0]

### Initialization

```
logger.info(f"Initialized {self.name} (ID: {self.agent_id})")
```


### Context Retrieval

```
logger.info(f"{self.name}: Retrieving context for query")
logger.warning(f"{self.name}: Using mock retrieval (integration pending)")
```


### Response Generation

```
logger.info(f"{self.name}: Generating response")
logger.info(f"{self.name}: Response generated ({response.processing_time_ms}ms)")
```


### Errors

```
logger.error(f"{self.name}: LLM call failed: {e}")
logger.error(f"{self.name}: Failed to parse JSON response: {e}")
logger.debug(f"Response was: {llm_response[:200]}")
logger.error(f"{self.name}: Error processing query: {e}")
```


### Log Levels

- **INFO**: Normal operation milestones (initialization, retrieval start, response complete)
- **WARNING**: Expected but notable conditions (mock retrieval, missing data)
- **ERROR**: Failures and exceptions with context
- **DEBUG**: Detailed diagnostic information (truncated responses, internal state)

---

## Performance Considerations

### Processing Time Tracking

Every response includes `processing_time_ms` measured from the start of `process_query()` to completion.[page:0]

This enables:[page:0]

- Performance monitoring and alerting
- Identifying slow agents or queries
- Optimizing prompt size and retrieval depth
- SLA compliance tracking


### Conversation History Limiting

Only the last 5 messages are included in prompts to:[page:0]

- Prevent token limit exhaustion
- Reduce LLM processing time
- Focus on recent, relevant context
- Control costs (tokens per request)


### Prompt Size Management

The `_format_context()` method could be enhanced to truncate long chunks:[page:0]

```
def _format_context(self, sources: List[Source]) -> str:
    MAX_CHUNK_CHARS = 500
    formatted = ""
    for i, source in enumerate(sources, 1):
        chunk = source.chunk_text
        if len(chunk) > MAX_CHUNK_CHARS:
            chunk = chunk[:MAX_CHUNK_CHARS] + "... [truncated]"
        formatted += f"[Source {i}] - {source.filename}\n{chunk}\n---\n"
    return formatted
```


---

## Testing Recommendations

### Unit Testing Abstract Methods

Mock the abstract methods for testing base functionality:[page:0]

```
class TestAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="test_agent",
            name="Test Agent",
            category_id=99
        )
    
    def get_system_prompt(self) -> str:
        return "You are a test agent."
    
    def can_handle_query(self, query: str, context: AgentContext) -> float:
        return 0.5

# Test prompt building
agent = TestAgent()
prompt = agent._build_prompt("test query", [], AgentContext(project_id=1))
assert "You are a test agent" in prompt
```


### Testing Error Handling

Simulate failures to verify graceful degradation:[page:0]

```
def test_llm_failure_handling():
    agent = TestAgent()
    agent.llm_client = Mock()
    agent.llm_client.generate.side_effect = OllamaException("Connection failed")
    
    response = agent.process_query("test", AgentContext(project_id=1))
    
    assert response.confidence == ConfidenceLevel.LOW
    assert "error" in response.metadata
    assert response.processing_time_ms > 0
```


### Testing Response Parsing

Test both successful and failed JSON parsing:[page:0]

```
def test_parse_valid_json():
    agent = TestAgent()
    llm_response = '''{"answer": "Test answer", "confidence": "high"}'''
    sources = []
    
    response = agent._parse_response(llm_response, sources)
    
    assert response.content == "Test answer"
    assert response.confidence == ConfidenceLevel.HIGH

def test_parse_invalid_json():
    agent = TestAgent()
    llm_response = "This is not JSON"
    sources = []
    
    response = agent._parse_response(llm_response, sources)
    
    assert response.content == llm_response
    assert response.confidence == ConfidenceLevel.LOW
    assert "parse_error" in response.metadata
```


---

## Integration with Orchestrator

The orchestrator uses `BaseAgent` instances through this pattern:[page:0]

```
# 1. Agent selection based on relevance scores
scores = {agent: agent.can_handle_query(query, context) for agent in agents}
selected_agents = [a for a, score in scores.items() if score > 0.5]

# 2. Batch context retrieval (optimization)
all_sources = {}
for agent in selected_agents:
    all_sources[agent.agent_id] = agent.retrieve_context(query, context)

# 3. Parallel agent processing
responses = []
for agent in selected_agents:
    response = agent.process_query(
        query,
        context,
        retrieved_context=all_sources[agent.agent_id]
    )
    responses.append(response)

# 4. Response aggregation
final_answer = orchestrator.aggregate_responses(responses)
```


---

## Future Enhancement Opportunities

### Async/Await Support

Convert to async methods for concurrent agent execution:[page:0]

```
async def process_query(self, query: str, context: AgentContext) -> AgentResponse:
    retrieved_context = await self.retrieve_context_async(query, context)
    prompt = self._build_prompt(query, retrieved_context, context)
    response_text = await self._call_llm_async(prompt, context)
    return self._parse_response(response_text, retrieved_context)
```


### Response Caching

Cache responses for identical queries:[page:0]

```
def process_query(self, query: str, context: AgentContext) -> AgentResponse:
    cache_key = self._generate_cache_key(query, context)
    
    if cached := self.response_cache.get(cache_key):
        logger.info(f"{self.name}: Returning cached response")
        return cached
    
    response = self._process_query_impl(query, context)
    self.response_cache.set(cache_key, response, ttl=3600)
    return response
```


### Prompt Template System

Use Jinja2 or similar for flexible prompt templates:[page:0]

```
def _build_prompt(self, query, retrieved_context, context):
    template = self.prompt_template_loader.get_template("agent_prompt.j2")
    return template.render(
        system_prompt=self.get_system_prompt(),
        conversation_history=context.conversation_history[-5:],
        sources=retrieved_context,
        query=query,
        agent_name=self.name
    )
```


### Metrics and Monitoring

Add instrumentation for production observability:[page:0]

```
def process_query(self, query: str, context: AgentContext) -> AgentResponse:
    with metrics.timer(f"agent.{self.agent_id}.processing_time"):
        try:
            response = self._process_query_impl(query, context)
            metrics.counter(f"agent.{self.agent_id}.success").increment()
            return response
        except Exception as e:
            metrics.counter(f"agent.{self.agent_id}.error").increment()
            raise
```


### Structured Output with Pydantic

Replace JSON string parsing with structured outputs:[page:0]

```
from pydantic import BaseModel

class AgentLLMOutput(BaseModel):
    answer: str
    confidence: str
    key_sources: List[str]
    suggests_consulting: List[str]
    reasoning: str

def _parse_response(self, llm_response: str, sources: List[Source]) -> AgentResponse:
    parsed = AgentLLMOutput.parse_raw(llm_response)
    # Convert to AgentResponse...
```

