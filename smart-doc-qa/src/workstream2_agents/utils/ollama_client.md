# OllamaClient Module Documentation

The `utils/ollama_client.py` module provides a high-level Python wrapper around the Ollama HTTP API for interacting with local large language models (LLMs).

## Module Overview

This module encapsulates all HTTP communication with an Ollama server, providing convenient methods for text generation, chat-based interactions, health checks, and model discovery. It handles error scenarios gracefully, converting network and API errors into custom exceptions with user-friendly messages.

## Dependencies and Imports

### External Libraries

- `requests`  
  - Used for all HTTP communication with the Ollama REST API.  
  - Handles POST requests for generation/chat and GET requests for health checks and model listing.

- `json`  
  - Imported but not directly used in the current implementation (JSON serialization is handled by `requests.post(json=payload)`).

- `logging`  
  - Provides debug and error logging throughout the client lifecycle.  
  - Logger is instantiated as `logger = logging.getLogger(__name__)` following Python best practices.

### Typing Imports

- `Dict`, `Any`, `Optional`  
  - Used for type hints to improve code clarity and IDE support.  
  - `Optional[T]` indicates parameters that may be `None`.

### Internal Dependencies

- `config.settings`  
  - Imports the global `settings` object to retrieve default configuration values for Ollama URL, model name, temperature, and timeout.

### Path Setup

The module begins with a path manipulation block:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

**Purpose**: Adds the parent directory to `sys.path` to enable relative imports when running scripts directly from the `utils/` folder.  
**Note**: This pattern is typically used during development but may be unnecessary when the package is properly installed or when using absolute imports.

## OllamaClient Class

### Constructor

```python
def __init__(
    self,
    model: str = None,
    base_url: str = None,
    temperature: float = None,
    timeout: int = None
)
```

#### Parameters

- `model: str` (optional)  
  - The name of the Ollama model to use for generation (e.g., `"llama3.1:8b"`, `"mistral:7b"`).  
  - Defaults to `settings.OLLAMA_MODEL` if not provided.

- `base_url: str` (optional)  
  - The base URL of the Ollama API server (e.g., `"http://localhost:11434"`).  
  - Defaults to `settings.OLLAMA_BASE_URL` if not provided.

- `temperature: float` (optional)  
  - Controls randomness in text generation (range typically 0.0-1.0).  
  - Lower values produce more deterministic outputs; higher values increase creativity.  
  - Defaults to `settings.OLLAMA_TEMPERATURE` if not provided.  
  - Note: Uses `temperature if temperature is not None` to allow passing `0.0` explicitly.

- `timeout: int` (optional)  
  - Maximum seconds to wait for API responses.  
  - Defaults to `settings.OLLAMA_TIMEOUT` if not provided.

#### Initialization Behavior

1. Assigns parameters to instance attributes, falling back to settings for any `None` values.
2. Constructs API endpoint URLs by combining `base_url` with endpoint paths:
   - `self.generate_url = f"{self.base_url}/api/generate"`
   - `self.chat_url = f"{self.base_url}/api/chat"`
3. Logs initialization with the selected model name at INFO level.

#### Example Usage

```python
# Use all defaults from settings
client = OllamaClient()

# Override specific parameters
client = OllamaClient(
    model="llama3.1:70b",
    temperature=0.7,
    timeout=180
)
```

***

## Core Methods

### generate()

```python
def generate(
    self,
    prompt: str,
    system_prompt: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None
) -> str
```

Generates a text completion from the LLM using the `/api/generate` endpoint.

#### Parameters

- `prompt: str` (required)  
  - The user prompt or instruction to send to the model.

- `system_prompt: Optional[str]`  
  - Optional system-level instructions that set the model's behavior or role.  
  - If provided, prepended to the user prompt with a double newline separator: `f"{system_prompt}\n\n{prompt}"`.

- `temperature: Optional[float]`  
  - Per-request temperature override.  
  - If `None`, uses the instance's default temperature.

- `max_tokens: Optional[int]`  
  - Maximum number of tokens to generate in the response.  
  - Maps to Ollama's `num_predict` option.

#### Returns

- `str`: The generated text response from the model.

#### Request Payload Structure

```json
{
  "model": "llama3.1:8b",
  "prompt": "Combined system + user prompt",
  "stream": false,
  "options": {
    "temperature": 0.1,
    "num_predict": 500  // only if max_tokens is specified
  }
}
```

The `stream: false` parameter ensures the entire response is returned at once rather than streamed incrementally.

#### Error Handling

The method wraps API calls in a comprehensive try-except block:

- `requests.exceptions.Timeout`  
  - Raised when request exceeds `self.timeout` seconds.  
  - Logs error and raises `OllamaException` with message: `"Request timed out. Try a simpler query or increase timeout."`

- `requests.exceptions.ConnectionError`  
  - Raised when client cannot establish connection to Ollama server.  
  - Logs error and raises `OllamaException` with message: `"Cannot connect to Ollama. Is it running? Try: ollama serve"`

- `requests.exceptions.HTTPError`  
  - Raised via `response.raise_for_status()` for non-2xx HTTP status codes.  
  - Logs and wraps error in `OllamaException` with HTTP error details.

- `Exception`  
  - Catch-all for any unexpected errors.  
  - Logs and wraps in `OllamaException` with original error message.

#### Logging

- **DEBUG**: Logs request payload model and response character count.
- **ERROR**: Logs all exception scenarios with descriptive messages.

#### Example Usage

```python
# Simple generation
response = client.generate("What is the capital of France?")

# With system prompt
response = client.generate(
    prompt="Explain quantum computing",
    system_prompt="You are a physics professor. Use simple language."
)

# With constraints
response = client.generate(
    prompt="Write a haiku about coffee",
    temperature=0.8,
    max_tokens=50
)
```

***

### chat()

```python
def chat(
    self,
    messages: list,
    temperature: Optional[float] = None
) -> str
```

Enables chat-style interactions with conversation context using the `/api/chat` endpoint.

#### Parameters

- `messages: list` (required)  
  - List of message dictionaries, each containing `'role'` and `'content'` keys.  
  - Follows OpenAI-style message format.  
  - Valid roles: `"system"`, `"user"`, `"assistant"`.

- `temperature: Optional[float]`  
  - Per-request temperature override.  
  - Falls back to instance temperature if `None`.

#### Returns

- `str`: The assistant's generated response.

#### Request Payload Structure

```json
{
  "model": "llama3.1:8b",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"},
    {"role": "assistant", "content": "Hi! How can I help?"},
    {"role": "user", "content": "What's the weather?"}
  ],
  "stream": false,
  "options": {
    "temperature": 0.1
  }
}
```

#### Response Parsing

Extracts the assistant's message from the nested response structure:

```python
generated_text = result.get("message", {}).get("content", "")
```

Returns empty string if response structure is unexpected.

#### Error Handling

Uses a single catch-all exception handler:

- Logs error with `logger.error()`
- Raises `OllamaException` with error details
- Less granular than `generate()` but covers all failure modes

#### Example Usage

```python
# Multi-turn conversation
messages = [
    {"role": "system", "content": "You are a travel advisor."},
    {"role": "user", "content": "I want to visit Japan."},
    {"role": "assistant", "content": "Japan is wonderful! When are you planning to go?"},
    {"role": "user", "content": "In spring, during cherry blossom season."}
]

response = client.chat(messages, temperature=0.5)
```

***

## Utility Methods

### check_health()

```python
def check_health(self) -> bool
```

Performs a health check to verify Ollama service availability.

#### Returns

- `bool`  
  - `True` if Ollama service responds with HTTP 200 to `/api/tags` endpoint.  
  - `False` for any exception or non-200 status code.

#### Implementation Details

- Uses a short 5-second timeout (not the instance timeout).
- Queries `/api/tags` endpoint as a lightweight health probe.
- Silently catches all exceptions and returns `False`.
- Does not log errors to avoid noise during startup checks.

#### Example Usage

```python
if not client.check_health():
    print("Error: Ollama service is not available")
    exit(1)
```

***

### list_models()

```python
def list_models(self) -> list
```

Retrieves a list of models available on the Ollama server.

#### Returns

- `list[str]`: List of model names (e.g., `["llama3.1:8b", "mistral:7b", "codellama:13b"]`).
- Empty list `[]` if request fails or no models are available.

#### Implementation Details

- Queries `/api/tags` endpoint which returns model metadata.
- Extracts model names using list comprehension: `[model["name"] for model in models]`.
- Logs errors but returns empty list rather than raising exceptions.
- Uses 5-second timeout.

#### Example Usage

```python
available_models = client.list_models()
if "llama3.1:8b" not in available_models:
    print("Required model not found. Please run: ollama pull llama3.1:8b")
```

***

## Exception Handling

### OllamaException

```python
class OllamaException(Exception):
    """Custom exception for Ollama-related errors"""
    pass
```

#### Purpose

- Custom exception type for all Ollama client errors.
- Allows calling code to distinguish Ollama failures from other exceptions.
- Contains user-friendly error messages that can be displayed directly.

#### Exception Messages by Error Type

| Error Scenario | Exception Message |
|---------------|------------------|
| Timeout | `"Request timed out. Try a simpler query or increase timeout."`  |
| Connection Error | `"Cannot connect to Ollama. Is it running? Try: ollama serve"`  |
| HTTP Error | `"HTTP error: {original_error}"`  |
| Chat Error | `"Chat error: {original_error}"`  |
| Unexpected Error | `"Unexpected error: {original_error}"`  |

#### Example Usage

```python
try:
    response = client.generate("Explain AI")
except OllamaException as e:
    print(f"Ollama error: {e}")
    # Handle gracefully or retry
```

***

## Global Client Instance

At module level:

```python
ollama_client = OllamaClient()
```

### Purpose

- Provides a singleton-like instance using default settings.
- Can be imported directly for simple use cases without manual instantiation.
- Initialized immediately when module is imported.

### Usage Pattern

```python
from utils.ollama_client import ollama_client

# Use pre-configured global client
response = ollama_client.generate("Hello, world!")
```

### Considerations

- Global instance uses settings from `config.settings` at import time.
- If you need multiple clients with different configurations, instantiate `OllamaClient` directly.
- Global instance may complicate testing unless properly mocked.

***

## Architecture and Design Patterns

### Separation of Concerns

- **Configuration**: Delegates defaults to `config.settings` module.
- **HTTP Communication**: Encapsulates all `requests` library usage.
- **Error Translation**: Converts network/HTTP errors into domain-specific `OllamaException`.

### Flexibility

- All parameters can be overridden per-instance (constructor) or per-request (method arguments).
- Supports both completion-style (`generate`) and chat-style (`chat`) interactions.

### Observability

- Logging at appropriate levels (INFO for lifecycle, DEBUG for requests/responses, ERROR for failures).
- Error messages include actionable guidance for users.

### Robustness

- Graceful handling of connection failures, timeouts, and malformed responses.
- Health check and model listing methods fail silently to support startup validation.

***

## Integration Examples

### Agent Integration

```python
from utils.ollama_client import OllamaClient
from config.settings import settings

class RequirementsAgent:
    def __init__(self):
        self.client = OllamaClient(
            model=settings.OLLAMA_MODEL,
            temperature=0.3
        )
    
    def analyze_requirements(self, document: str) -> str:
        system_prompt = "You are a requirements analysis expert."
        prompt = f"Extract functional requirements from:\n\n{document}"
        return self.client.generate(prompt, system_prompt=system_prompt)
```

### Retry Logic with Backup Model

```python
def generate_with_fallback(prompt: str) -> str:
    primary_client = OllamaClient(model=settings.OLLAMA_MODEL)
    backup_client = OllamaClient(model=settings.OLLAMA_BACKUP_MODEL)
    
    try:
        return primary_client.generate(prompt)
    except OllamaException:
        logger.warning("Primary model failed, trying backup")
        return backup_client.generate(prompt)
```

### Startup Validation

```python
def validate_ollama_setup():
    client = OllamaClient()
    
    if not client.check_health():
        raise RuntimeError("Ollama service not available")
    
    models = client.list_models()
    required = settings.OLLAMA_MODEL
    
    if required not in models:
        raise RuntimeError(f"Model {required} not found. Run: ollama pull {required}")
    
    print("✓ Ollama setup validated")
```

***

## Testing Recommendations

### Unit Testing

- Mock `requests.post` and `requests.get` to test without running Ollama.
- Verify exception handling by simulating timeouts and connection errors.
- Test parameter overrides at both instance and method levels.

### Integration Testing

- Requires a running Ollama instance with test models pulled.
- Test actual generation with known prompts and verify response format.
- Validate health checks and model listing against real server.

### Example Test Structure

```python
import unittest
from unittest.mock import patch, Mock

class TestOllamaClient(unittest.TestCase):
    @patch('utils.ollama_client.requests.post')
    def test_generate_success(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {"response": "Test output"}
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        client = OllamaClient()
        result = client.generate("Test prompt")
        
        self.assertEqual(result, "Test output")
        mock_post.assert_called_once()
```

***

## Future Enhancement Opportunities

### Streaming Support

- Add a `generate_stream()` method that yields response chunks in real-time.
- Set `"stream": True` in payload and process Server-Sent Events (SSE).

### Embeddings

- Add `embed()` method to call `/api/embeddings` endpoint for vector generation.
- Useful for semantic search and RAG (Retrieval-Augmented Generation) workflows.

### Batch Processing

- Add `generate_batch()` to process multiple prompts efficiently.
- Consider concurrent requests with `ThreadPoolExecutor` or async/await.

### Advanced Error Recovery

- Implement exponential backoff retry logic within the client.
- Add circuit breaker pattern to prevent cascading failures.

### Metrics and Monitoring

- Track token usage, latency, and error rates.
- Expose metrics in Prometheus format for production observability.
