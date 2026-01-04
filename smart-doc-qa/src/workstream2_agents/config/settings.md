# Config - settings.py

The `config/settings.py` module centralizes configuration for the workstream2 agent framework by loading environment variables, applying defaults, and validating required settings at import time.

## Module overview

- Defines a **Settings** class whose class attributes mirror key configuration options for Ollama, logging, and future database usage.  
- Uses `python-dotenv` to load a `.env` file into process environment variables before reading them.  
- Instantiates a global `settings` object and validates required configuration as soon as the module is imported.

## Dependencies and imports

- `os`  
  - Used for `os.getenv` to read environment variables with optional default values.  
- `dotenv.load_dotenv`  
  - Loads variables from a `.env` file in the current working directory (or parent chain) into the environment when the module is imported.  
- `typing.Optional`  
  - Used to indicate that `DATABASE_URL` may be `None` if not provided.

Usage pattern:

```python
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()
```

This ensures `.env` values are available before the `Settings` class reads them.

## Settings class

### Purpose

The **Settings** class acts as a simple configuration container, storing configuration as class attributes typed to basic Python types.  
It does not use `pydantic` or dynamic validation; instead, it performs a minimal manual check via the `validate` classmethod.

### Ollama configuration

These attributes control how agents connect to and use the Ollama model server.

- `OLLAMA_BASE_URL: str`  
  - Source: `os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")`.  
  - Default: `"http://localhost:11434"` if the env variable is not set.  
  - Purpose: Base URL for the Ollama HTTP API (host and port used to send completions/embeddings requests).

- `OLLAMA_MODEL: str`  
  - Source: `os.getenv("OLLAMA_MODEL", "llama3.1:8b")`.  
  - Default: `"llama3.1:8b"`.  
  - Purpose: Primary model identifier used by agents when generating responses.

- `OLLAMA_BACKUP_MODEL: str`  
  - Source: `os.getenv("OLLAMA_BACKUP_MODEL", "mistral:7b")`.  
  - Default: `"mistral:7b"`.  
  - Purpose: Secondary model to fall back to if the primary model fails or is not available.

- `OLLAMA_TEMPERATURE: float`  
  - Source: `float(os.getenv("OLLAMA_TEMPERATURE", "0.1"))`.  
  - Default: `0.1`.  
  - Purpose: Controls randomness in generated text; lower values produce more deterministic, focused outputs, higher values more creative outputs.  
  - Notes: If the environment variable is set to a non-numeric value, importing this module will raise a `ValueError` due to the `float()` cast.

- `OLLAMA_TIMEOUT: int`  
  - Source: `int(os.getenv("OLLAMA_TIMEOUT", "120"))`.  
  - Default: `120` (seconds).  
  - Purpose: Maximum time agents will wait for an Ollama response before timing out.  
  - Notes: Non-numeric values in the environment will cause a `ValueError` during import due to the `int()` cast.

### Database configuration

- `DATABASE_URL: Optional[str]`  
  - Source: `os.getenv("DATABASE_URL")`.  
  - Default: `None` if not set.  
  - Purpose: Reserved for future integration with a database (e.g., PostgreSQL, MySQL, SQLite, etc.).  
  - Notes: Since it is optional and not validated, the rest of the codebase must handle `None` gracefully.

### Logging configuration

- `LOG_LEVEL: str`  
  - Source: `os.getenv("LOG_LEVEL", "INFO")`.  
  - Default: `"INFO"`.  
  - Purpose: Controls the verbosity of logging (commonly `"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"`, `"CRITICAL"`).  
  - Notes: This is not validated against a set of allowed values; logging configuration downstream must map this string correctly.

### Agent behavior configuration

These settings define baseline behavior for agents, such as retry policies and confidence thresholds.

- `MAX_RETRIES: int = 3`  
  - Hard-coded class attribute (not from environment).  
  - Purpose: Maximum number of times an agent may retry a failed operation (for example, retrying model calls or orchestration steps).

- `MIN_CONFIDENCE_SCORE: float = 0.3`  
  - Hard-coded class attribute.  
  - Purpose: Lower bound on confidence scores for accepting model outputs or decisions (e.g., classification or extraction confidence).  
  - Notes: Downstream components must define what a “confidence score” means and how this threshold is applied.

## Validation behavior

The class defines a `validate` classmethod:

```python
@classmethod
def validate(cls):
    """Validate that all required settings are present"""
    if not cls.OLLAMA_BASE_URL:
        raise ValueError("OLLAMA_BASE_URL is required")
    return True
```

Key points:

- Only `OLLAMA_BASE_URL` is considered required and validated.  
- If `OLLAMA_BASE_URL` is missing or empty after environment loading, a `ValueError` is raised with a clear message.  
- The method returns `True` when configuration passes validation, which can be used for checks in tests or startup scripts.

## Global instance and import-time side effects

At the bottom of the module:

```python
settings = Settings()
settings.validate()
```

Effects:

- A single global `settings` object is created when `config.settings` is imported.  
- Validation is executed immediately; if `OLLAMA_BASE_URL` is invalid, the import will fail and stop application startup early.  
- Code elsewhere uses `from workstream2_agents.config.settings import settings` (or similar) to access configuration attributes.

Example usage:

```python
from workstream2_agents.config.settings import settings

base_url = settings.OLLAMA_BASE_URL
model_name = settings.OLLAMA_MODEL
timeout = settings.OLLAMA_TIMEOUT
```

This pattern centralizes configuration and ensures consistent access across agents and orchestrators.

## Environment variables reference

To configure this module in a deployment or development environment, define these variables (typically in a `.env` file):

```env
# Required
OLLAMA_BASE_URL=http://localhost:11434

# Recommended
OLLAMA_MODEL=llama3.1:8b
OLLAMA_BACKUP_MODEL=mistral:7b
OLLAMA_TEMPERATURE=0.1
OLLAMA_TIMEOUT=120
LOG_LEVEL=INFO

# Optional / future
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

Considerations:

- All numeric values must be valid strings convertible to `float` or `int` respectively.  
- If `.env` is missing, the module will fall back to default values where defined but still require `OLLAMA_BASE_URL` not to be empty.

## Extension and customization guidance

When extending this configuration module, keep these patterns in mind:

- Add new settings as class attributes on `Settings`, using `os.getenv("NAME", default)` when environment configurability is desired.  
- Update `validate` to enforce additional required settings (for example API keys, storage URLs, or queue endpoints).  
- If configuration grows significantly, consider introducing a **typed** configuration layer (e.g., `pydantic.BaseSettings`) to improve validation and error reporting.
