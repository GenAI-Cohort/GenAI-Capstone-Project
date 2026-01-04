# Install Ollama (macOS/Linux)
curl -fsSL https://ollama.com/install.sh | sh

# For Windows, download from: https://ollama.com/download/windows

# Verify installation
ollama --version

# Pull Llama 3.1 8B model (this will take a few minutes - 4.7GB)
ollama pull llama3.1:8b

# Test Ollama
ollama run llama3.1:8b "Hello, how are you?"

# Pull backup model (optional)
ollama pull mistral:7b

```

**Expected output:**
```
✓ Llama 3.1 8B model downloaded successfully
✓ Ollama server running at http://localhost:11434
