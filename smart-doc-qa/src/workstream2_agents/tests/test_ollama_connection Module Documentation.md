<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Test Ollama Connection Module Documentation

The `tests/test_ollama_connection.py` module provides a comprehensive test suite for validating the Ollama LLM setup and verifying that all components are correctly configured and operational before building agents.

## Module Overview

This test module serves as a **pre-flight checklist** for the workstream2 agent system, ensuring that:

- The Ollama service is running and accessible
- Required models are available locally
- Basic text generation works correctly
- JSON-formatted responses can be generated and parsed

The tests are designed to run sequentially with early exit if critical components fail, providing clear diagnostic messages and actionable remediation steps.

### Design Philosophy

- **Fail Fast**: Stop testing if foundational requirements aren't met (service running, model available)
- **User-Friendly Output**: Clear visual indicators (✅ ❌ ⚠️) and formatted console output
- **Actionable Diagnostics**: Specific instructions for fixing failures
- **Progressive Validation**: Tests build on each other, from simple to complex
- **Non-Destructive**: Read-only operations, safe to run repeatedly

***

## Module Header and Purpose

```python
"""
Test Ollama connection and basic functionality
Run this first to ensure your setup is working
"""
```


### Purpose Statement

This docstring clearly indicates:

- **What**: Tests Ollama connection and functionality
- **When**: Should be run first, before other development
- **Why**: Ensures setup is correct before proceeding

***

## Dependencies and Imports

### Standard Library

```python
import sys
import logging
from pathlib import Path
```

- **sys**: Used for path manipulation to enable relative imports
- **logging**: Provides structured logging for test execution
- **pathlib.Path**: Modern path handling for cross-platform compatibility


### Path Setup

```python
sys.path.insert(0, str(Path(__file__).parent.parent))
```

**Purpose**: Adds the parent directory (`workstream2_agents/`) to Python's module search path.

**Why**: Enables importing from `utils`, `config`, and other project modules when running the test file directly (e.g., `python tests/test_ollama_connection.py`).

**Directory Structure**:

```
workstream2_agents/
├── utils/
├── config/
├── tests/
│   └── test_ollama_connection.py  ← We are here
```


### Internal Dependencies

```python
from utils.ollama_client import OllamaClient, OllamaException
from config.settings import settings
```

- **OllamaClient**: The main client class for interacting with Ollama
- **OllamaException**: Custom exception for Ollama-related errors
- **settings**: Configuration object containing Ollama connection parameters


### JSON Import

```python
import json
```

Imported inside `test_json_generation()` function for JSON parsing validation. Scoped import keeps the module header clean and only imports when needed.

***

## Logging Configuration

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
```


### Configuration Details

- **Level**: `logging.INFO` - Logs informational messages and above (INFO, WARNING, ERROR, CRITICAL)
- **Format**: Includes timestamp, logger name, level, and message
- **Logger**: Module-level logger with name `tests.test_ollama_connection`


### Log Format Example

```
2025-12-30 15:10:23,456 - tests.test_ollama_connection - INFO - Testing Ollama connection
```


### Rationale

- **INFO level**: Provides visibility into test execution without excessive debug noise
- **Timestamped logs**: Helps diagnose timing issues or performance problems
- **Named loggers**: Distinguishes test output from other module logs

***

## Test Functions

### test_ollama_health()

```python
def test_ollama_health():
    """Test if Ollama service is running"""
```


#### Purpose

Verifies that the Ollama service is running and responding to API requests. This is the **most critical test** - if it fails, no other tests can succeed.

#### Workflow

**Step 1: Display Header**

```python
print("\n" + "="*60)
print("TEST 1: Ollama Health Check")
print("="*60)
```

Creates a visually distinct section separator.

**Step 2: Create Client**

```python
client = OllamaClient()
```

Instantiates an Ollama client using default settings.

**Step 3: Check Health**

```python
if client.check_health():
    print("✅ Ollama service is running")
    return True
```

Calls the `check_health()` method which queries the `/api/tags` endpoint with a 5-second timeout.

**Step 4: Handle Failure**

```python
else:
    print("❌ Ollama service is NOT running")
    print("\nPlease start Ollama:")
    print("  1. Open a terminal")
    print("  2. Run: ollama serve")
    print("  3. Re-run this test")
    return False
```

Provides step-by-step instructions for starting Ollama.

#### Returns

- **bool**: `True` if Ollama is running, `False` otherwise


#### Example Output (Success)

```
============================================================
TEST 1: Ollama Health Check
============================================================
✅ Ollama service is running
```


#### Example Output (Failure)

```
============================================================
TEST 1: Ollama Health Check
============================================================
❌ Ollama service is NOT running

Please start Ollama:
  1. Open a terminal
  2. Run: ollama serve
  3. Re-run this test
```


#### Technical Details

The `check_health()` method:

- Sends GET request to `http://localhost:11434/api/tags` (or configured base URL)
- Expects HTTP 200 response
- Uses 5-second timeout to avoid hanging
- Returns `False` for any exception (timeout, connection error, HTTP error)

***

### test_list_models()

```python
def test_list_models():
    """Test listing available models"""
```


#### Purpose

Verifies that:

1. The Ollama service can list available models
2. At least one model is available
3. The required model (from settings) is present

#### Workflow

**Step 1: Display Header**

```python
print("\n" + "="*60)
print("TEST 2: List Available Models")
print("="*60)
```

**Step 2: List Models**

```python
client = OllamaClient()
models = client.list_models()
```

Calls `list_models()` which queries `/api/tags` and extracts model names.

**Step 3: Check if Models Found**

```python
if models:
    print(f"✅ Found {len(models)} model(s):")
    for model in models:
        print(f"  - {model}")
```

Lists all available models with bullet points.

**Step 4: Verify Required Model**

```python
if settings.OLLAMA_MODEL in models:
    print(f"\n✅ Required model '{settings.OLLAMA_MODEL}' is available")
    return True
else:
    print(f"\n⚠️ Required model '{settings.OLLAMA_MODEL}' is NOT available")
    print(f"\nPlease pull the model:")
    print(f"  ollama pull {settings.OLLAMA_MODEL}")
    return False
```

Checks specifically for the configured model and provides exact command to pull it if missing.

**Step 5: Handle No Models Case**

```python
else:
    print("❌ No models found")
    print(f"\nPlease pull a model:")
    print(f"  ollama pull {settings.OLLAMA_MODEL}")
    return False
```

Handles edge case where Ollama is running but no models are installed.

#### Returns

- **bool**: `True` if required model is available, `False` otherwise


#### Example Output (Success)

```
============================================================
TEST 2: List Available Models
============================================================
✅ Found 3 model(s):
  - llama3.1:8b
  - mistral:7b
  - codellama:13b

✅ Required model 'llama3.1:8b' is available
```


#### Example Output (Model Missing)

```
============================================================
TEST 2: List Available Models
============================================================
✅ Found 2 model(s):
  - mistral:7b
  - codellama:13b

⚠️ Required model 'llama3.1:8b' is NOT available

Please pull the model:
  ollama pull llama3.1:8b
```


#### Technical Details

The `list_models()` method:

- Queries `/api/tags` endpoint
- Parses JSON response: `{"models": [{"name": "llama3.1:8b", ...}, ...]}`
- Extracts just the model names into a list
- Returns empty list on any error

***

### test_simple_generation()

```python
def test_simple_generation():
    """Test simple text generation"""
```


#### Purpose

Validates that the LLM can generate text responses successfully. This is the **core functionality test** - if this fails, the agent system won't work.

#### Test Prompt

```python
test_prompt = "Say 'Hello, I am working!' and nothing else."
```

**Why This Prompt**:

- **Simple**: Minimal cognitive load on the model
- **Deterministic**: Expected output is clear
- **Fast**: Should generate quickly (10-30 seconds)
- **Verifiable**: Easy to see if it worked


#### Workflow

**Step 1: Display Header and Prompt**

```python
print("\n" + "="*60)
print("TEST 3: Simple Text Generation")
print("="*60)
print(f"Prompt: {test_prompt}")
print("\nGenerating response (this may take 10-30 seconds)...")
```

Sets user expectations about wait time.

**Step 2: Generate Response**

```python
response = client.generate(
    prompt=test_prompt,
    temperature=0.1
)
```

- Uses low temperature (0.1) for deterministic output
- No system prompt needed for this simple test
- Uses default timeout (120 seconds from settings)

**Step 3: Display Result**

```python
print(f"\n✅ Response received:")
print(f"  {response}")
return True
```

Shows the actual LLM response for manual verification.

**Step 4: Handle Errors**

```python
except OllamaException as e:
    print(f"\n❌ Generation failed: {e}")
    return False
```

Catches all Ollama-related errors (timeout, connection, HTTP errors).

#### Returns

- **bool**: `True` if generation succeeds, `False` on any error


#### Example Output (Success)

```
============================================================
TEST 3: Simple Text Generation
============================================================
Prompt: Say 'Hello, I am working!' and nothing else.

Generating response (this may take 10-30 seconds)...

✅ Response received:
  Hello, I am working!
```


#### Example Output (Timeout)

```
============================================================
TEST 3: Simple Text Generation
============================================================
Prompt: Say 'Hello, I am working!' and nothing else.

Generating response (this may take 10-30 seconds)...

❌ Generation failed: Request timed out. Try a simpler query or increase timeout.
```


#### Technical Details

- First generation is often slower (model loading)
- Subsequent generations are faster (model cached in memory)
- Temperature=0.1 produces very consistent outputs
- Timeout is critical for preventing hangs on model loading issues

***

### test_json_generation()

```python
def test_json_generation():
    """Test JSON-formatted response generation"""
```


#### Purpose

Validates that the LLM can generate structured JSON output, which is **critical for agent responses**. All agents expect JSON-formatted responses with specific fields.

#### Test Prompt

```python
test_prompt = """Return a JSON object with these fields:
{
  "status": "working",
  "message": "I can generate JSON",
  "confidence": "high"
}

Return ONLY valid JSON, no other text."""
```

**Design Features**:

- **Explicit format**: Shows exact expected structure
- **Clear instruction**: "Return ONLY valid JSON, no other text"
- **Simple schema**: Just 3 string fields
- **Example values**: Provides template to follow


#### Workflow

**Step 1: Display Header**

```python
print("\n" + "="*60)
print("TEST 4: JSON Response Generation")
print("="*60)
print("Testing JSON generation...")
print("\nGenerating response...")
```

**Step 2: Generate Response**

```python
response = client.generate(
    prompt=test_prompt,
    temperature=0.0
)
```

- **Temperature=0.0**: Maximum determinism for structured output
- Lower temperature increases likelihood of valid JSON

**Step 3: Display Raw Response**

```python
print(f"\n✅ Response received:")
print(response)
```

Shows what the LLM actually returned (may include markdown formatting).

**Step 4: Clean Response**

```python
cleaned = response.strip()
if cleaned.startswith("```
    cleaned = cleaned[7:]
if cleaned.startswith("```"):
    cleaned = cleaned[3:]
if cleaned.endswith("```
    cleaned = cleaned[:-3]
cleaned = cleaned.strip()
```

**Cleaning Steps**:[page:0]

1. Strip whitespace
2. Remove ` ```
3. Remove ````` prefix if present (without json)
4. Remove ` ```
5. Strip whitespace again

**Why Needed**: Many LLMs wrap JSON in markdown code blocks despite instructions not to.

**Step 5: Parse JSON**

```python
parsed = json.loads(cleaned)
print(f"\n✅ Successfully parsed as JSON:")
print(f"  {parsed}")
return True
```

Attempts to parse as JSON. If successful, displays parsed object.

**Step 6: Handle Parse Errors (Gracefully)**

```python
except json.JSONDecodeError as e:
    print(f"\n⚠️ Response was not valid JSON: {e}")
    print("  (This is OK - we can handle this in the agent)")
    return True  # Don't fail the test for this
```

**Important**: Returns `True` even on parse failure because:

- Agents have fallback handling for unparsed responses
- Model may need fine-tuning but basic generation works
- Doesn't block other agent development

**Step 7: Handle Generation Errors**

```python
except OllamaException as e:
    print(f"\n❌ Generation failed: {e}")
    return False
```

Only fails if generation itself fails (timeout, connection error).

#### Returns

- **bool**: `True` if generation succeeds (even if JSON invalid), `False` only on generation failure


#### Example Output (Success)

```
============================================================
TEST 4: JSON Response Generation
============================================================
Testing JSON generation...

Generating response...

✅ Response received:
```

{
"status": "working",
"message": "I can generate JSON",
"confidence": "high"
}

```

✅ Successfully parsed as JSON:
  {'status': 'working', 'message': 'I can generate JSON', 'confidence': 'high'}
```


#### Example Output (Invalid JSON, Still Pass)

```
============================================================
TEST 4: JSON Response Generation
============================================================
Testing JSON generation...

Generating response...

✅ Response received:
The JSON object would be: {"status": "working", "message": "I can generate JSON", "confidence": "high"}

⚠️ Response was not valid JSON: Expecting value: line 1 column 1 (char 0)
  (This is OK - we can handle this in the agent)
```


#### Technical Details

**Why JSON Matters**:

- Agents parse JSON to extract: answer, confidence, key sources, suggested agents
- Structured output enables programmatic response handling
- JSON parsing failures are handled gracefully by `BaseAgent._parse_response()`

**Model Behavior**:

- Temperature=0.0 increases JSON validity rate
- Markdown wrapping is common with instruction-tuned models
- Cleaning logic matches the agent's response parser

***

## Main Test Runner

### run_all_tests()

```python
def run_all_tests():
    """Run all Ollama tests"""
```


#### Purpose

Orchestrates the complete test suite with:

- Configuration display
- Sequential test execution
- Early exit on critical failures
- Summary report


#### Workflow

**Step 1: Display Suite Header**

```python
print("\n" + "="*60)
print("OLLAMA CONNECTION TEST SUITE")
print("="*60)
```

**Step 2: Display Configuration**

```python
print(f"\nConfiguration:")
print(f"  Base URL: {settings.OLLAMA_BASE_URL}")
print(f"  Model: {settings.OLLAMA_MODEL}")
print(f"  Temperature: {settings.OLLAMA_TEMPERATURE}")
print(f"  Timeout: {settings.OLLAMA_TIMEOUT}s")
```

Shows all Ollama settings being used for the tests.

**Example Output**:

```
Configuration:
  Base URL: http://localhost:11434
  Model: llama3.1:8b
  Temperature: 0.1
  Timeout: 120s
```

**Step 3: Initialize Results Tracking**

```python
results = []
```

List of tuples: `[(test_name, passed), ...]`

**Step 4: Test 1 - Health Check (Critical)**

```python
results.append(("Health Check", test_ollama_health()))
if not results[-1][1]:
    print("\n❌ Ollama is not running. Please start it and try again.")
    return
```

**Early Exit**: If health check fails, stops all testing because nothing else will work.

**Step 5: Test 2 - List Models (Critical)**

```python
results.append(("List Models", test_list_models()))
if not results[-1][1]:
    print("\n❌ Required model not available. Please pull it and try again.")
    return
```

**Early Exit**: If required model is missing, stops testing because generation will fail.

**Step 6: Test 3 - Simple Generation**

```python
results.append(("Simple Generation", test_simple_generation()))
```

No early exit - continue to JSON test even if this fails.

**Step 7: Test 4 - JSON Generation**

```python
results.append(("JSON Generation", test_json_generation()))
```

Final test, no early exit.

**Step 8: Display Summary**

```python
print("\n" + "="*60)
print("TEST SUMMARY")
print("="*60)
for test_name, passed in results:
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {test_name}")
```

Lists all tests with pass/fail status.

**Step 9: Display Final Message**

```python
all_passed = all(result[1] for result in results)
if all_passed:
    print("\n🎉 All tests passed! Your Ollama setup is working correctly.")
    print("\nYou're ready to start building agents!")
else:
    print("\n⚠️ Some tests failed. Please fix the issues and try again.")
print("="*60 + "\n")
```

Provides clear next steps based on results.

#### Example Output (All Pass)

```
============================================================
OLLAMA CONNECTION TEST SUITE
============================================================

Configuration:
  Base URL: http://localhost:11434
  Model: llama3.1:8b
  Temperature: 0.1
  Timeout: 120s

[... individual test output ...]

============================================================
TEST SUMMARY
============================================================
✅ PASS - Health Check
✅ PASS - List Models
✅ PASS - Simple Generation
✅ PASS - JSON Generation

🎉 All tests passed! Your Ollama setup is working correctly.

You're ready to start building agents!
============================================================
```


#### Example Output (Health Check Fail)

```
============================================================
OLLAMA CONNECTION TEST SUITE
============================================================

Configuration:
  Base URL: http://localhost:11434
  Model: llama3.1:8b
  Temperature: 0.1
  Timeout: 120s

============================================================
TEST 1: Ollama Health Check
============================================================
❌ Ollama service is NOT running

Please start Ollama:
  1. Open a terminal
  2. Run: ollama serve
  3. Re-run this test

❌ Ollama is not running. Please start it and try again.
```


***

## Entry Point

```python
if __name__ == "__main__":
    run_all_tests()
```


### Purpose

Allows the test file to be executed directly:

```bash
python tests/test_ollama_connection.py
```

Or:

```bash
python -m tests.test_ollama_connection
```


### Behavior

- When imported as a module: Functions are available but tests don't run automatically
- When executed directly: `run_all_tests()` is called immediately

***

## Testing Strategy and Design Patterns

### Progressive Validation

Tests are ordered from simple to complex:

1. **Service Running**: Most basic check
2. **Models Available**: Requires service running
3. **Text Generation**: Requires service + models
4. **JSON Generation**: Requires all above + structured output capability

### Fail Fast with Early Exit

Critical failures stop testing immediately:

- **Health check fails**: Exit (nothing else will work)
- **Model missing**: Exit (generation will fail)
- **Generation fails**: Continue (JSON test provides additional diagnostic info)


### Clear Visual Feedback

Consistent use of Unicode symbols:

- ✅ Success/Pass
- ❌ Failure/Fail
- ⚠️ Warning/Non-critical issue
- 🎉 Complete success


### Actionable Error Messages

Every failure includes:

- Clear statement of what failed
- Explanation of why it matters
- Step-by-step instructions to fix it
- Exact commands to run

Example:

```
❌ Required model 'llama3.1:8b' is NOT available

Please pull the model:
  ollama pull llama3.1:8b
```


### Non-Blocking JSON Validation

The JSON generation test returns `True` even on parse failures because:

- Agents have fallback logic for non-JSON responses
- Model tuning is separate from setup validation
- Allows development to continue while improving prompts

***

## Integration with Development Workflow

### When to Run

**Required**:

- First time setting up the project
- After changing Ollama configuration
- After pulling new models
- When troubleshooting agent issues

**Optional**:

- Before starting development sessions
- As part of CI/CD pipeline (if Ollama in CI environment)


### Expected Runtime

- Health check: ~1 second
- List models: ~1 second
- Simple generation: 10-30 seconds (first run), 5-10 seconds (cached)
- JSON generation: 10-30 seconds (first run), 5-10 seconds (cached)

**Total**: ~1-2 minutes on first run, ~30-60 seconds on subsequent runs

### Common Failure Scenarios

#### Scenario 1: Ollama Not Running

```
❌ Ollama service is NOT running
```

**Fix**:

```bash
ollama serve
```


#### Scenario 2: Model Not Pulled

```
⚠️ Required model 'llama3.1:8b' is NOT available
```

**Fix**:

```bash
ollama pull llama3.1:8b
```


#### Scenario 3: Wrong Base URL

```
❌ Generation failed: Cannot connect to Ollama. Is it running?
```

**Fix**: Check `.env` file:

```
OLLAMA_BASE_URL=http://localhost:11434
```


#### Scenario 4: Timeout

```
❌ Generation failed: Request timed out.
```

**Fix**: Increase timeout in `.env`:

```
OLLAMA_TIMEOUT=180
```


***

## Environment Configuration

The test suite reads these settings from `config/settings.py`:

```python
settings.OLLAMA_BASE_URL    # Default: http://localhost:11434
settings.OLLAMA_MODEL       # Default: llama3.1:8b
settings.OLLAMA_TEMPERATURE # Default: 0.1
settings.OLLAMA_TIMEOUT     # Default: 120
```

These are loaded from `.env` file:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
OLLAMA_BACKUP_MODEL=mistral:7b
OLLAMA_TEMPERATURE=0.1
OLLAMA_TIMEOUT=120
```


***

## Logging and Debugging

### Log Output

The configured logging shows internal operations:

```
2025-12-30 15:10:45,123 - utils.ollama_client - INFO - Initialized llama3.1:8b
2025-12-30 15:10:46,234 - utils.ollama_client - DEBUG - Sending request to /api/generate
2025-12-30 15:11:15,456 - utils.ollama_client - DEBUG - Received response (1234 chars)
```


### Debugging Failed Tests

**Enable DEBUG logging**:

```python
logging.basicConfig(
    level=logging.DEBUG,  # Changed from INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

This will show:

- Full request payloads
- Response bodies (truncated)
- Retry attempts
- Network errors

***

## Extension Opportunities

### Add Model Performance Test

```python
def test_generation_speed():
    """Test generation speed for performance baseline"""
    import time
    
    client = OllamaClient()
    start = time.time()
    
    client.generate("Count to 10.", temperature=0.0)
    
    elapsed = time.time() - start
    print(f"Generation took {elapsed:.2f} seconds")
    
    if elapsed > 60:
        print("⚠️ Generation is slow. Consider using a smaller model.")
    
    return True
```


### Add Chat Endpoint Test

```python
def test_chat_functionality():
    """Test chat endpoint with conversation"""
    client = OllamaClient()
    
    messages = [
        {"role": "user", "content": "Say hello"},
        {"role": "assistant", "content": "Hello!"},
        {"role": "user", "content": "What did you just say?"}
    ]
    
    try:
        response = client.chat(messages)
        print(f"✅ Chat response: {response}")
        return True
    except OllamaException as e:
        print(f"❌ Chat failed: {e}")
        return False
```


### Add Embedding Test

```python
def test_embeddings():
    """Test embedding generation for RAG"""
    client = OllamaClient()
    
    try:
        # Note: Would need to add embed() method to OllamaClient
        embedding = client.embed("Test sentence")
        print(f"✅ Embedding generated: {len(embedding)} dimensions")
        return True
    except OllamaException as e:
        print(f"❌ Embedding failed: {e}")
        return False
```


***

## Best Practices Demonstrated

### 1. Visual Organization

- Consistent header formatting with `=` characters
- Clear section separation
- Unicode symbols for status indication


### 2. User Experience

- Progress messages ("this may take 10-30 seconds")
- Actionable error messages with exact commands
- Summary report at the end


### 3. Defensive Programming

- Try-except blocks around all LLM calls
- Graceful handling of JSON parse failures
- Early exit on critical failures


### 4. Testability

- Each test is independent function
- Clear boolean return values
- Results tracking for reporting


### 5. Configuration Display

- Shows all settings being used
- Helps diagnose configuration issues
- Documents expected values

***

## Summary

The `test_ollama_connection.py` module provides:

✅ **Comprehensive Validation**: Tests all critical components of the Ollama setup
✅ **User-Friendly Output**: Clear visual indicators and actionable error messages
✅ **Fail-Fast Design**: Stops early on critical failures to save time
✅ **Progressive Testing**: Builds from simple to complex validations
✅ **Production-Ready**: Handles edge cases and provides debugging information

**Recommended Usage**: Run this test suite as the first step in any new development environment setup or when troubleshooting agent issues.

