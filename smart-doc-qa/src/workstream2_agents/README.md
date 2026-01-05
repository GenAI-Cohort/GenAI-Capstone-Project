# Workstream 2: Agent Framework & Orchestration

## 📋 Overview

This workstream implements the multi-agent AI system using **100% FREE, local technologies**:

- **Ollama** for LLM inference (Llama 3.1 8B)
- **Python** for agent framework
- **No API costs** - everything runs locally

## 🏗️ Architecture

```txt
workstream2_agents/
├── agents/              # Specialized agents
│   ├── base_agent.py    # Base class for all agents
│   ├── requirements_agent.py
│   ├── business_rules_agent.py
│   ├── design_agent.py
│   ├── tech_specs_agent.py
│   ├── contracts_agent.py
│   └── proposals_agent.py
├── orchestrator/        # Orchestration logic
│   └── orchestrator_agent.py
├── utils/               # Utilities
│   ├── ollama_client.py
│   ├── prompt_builder.py
│   └── response_parser.py
├── prompts/             # System prompts
│   └── agent_prompts.py
├── config/              # Configuration
│   └── settings.py
└── tests/               # Tests
    ├── test_ollama_connection.py
    ├── test_agents.py
    └── test_orchestrator.py
```

## 🚀 Setup Instructions

### Step 1: Install Ollama

```bash
# macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Download from: https://ollama.com/download/windows

# Verify installation
ollama --version
```

### Step 2: Pull LLM Models

```bash
# Primary model (4.7GB)
ollama pull llama3.1:8b

# Backup model (optional)
ollama pull mistral:7b

# Test the model
ollama run llama3.1:8b "Hello!"
```

### Step 3: Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit .env if needed (defaults should work)
```

### Step 5: Test Ollama Connection

```bash
# Run connection tests
python tests/test_ollama_connection.py
```

**Expected output:**

```txt
✅ Ollama service is running
✅ Required model 'llama3.1:8b' is available
✅ Response received
✅ Successfully parsed as JSON
🎉 All tests passed!
```

## 📦 Dependencies

See `requirements.txt`:

- `requests` - HTTP client for Ollama API
- `pydantic` - Data validation
- `python-dotenv` - Environment variables
- `pytest` - Testing framework

## 🧪 Testing

```bash
# Test Ollama connection
python tests/test_ollama_connection.py

# Run unit tests (once agents are implemented)
pytest tests/test_agents.py

# Run all tests
pytest tests/
```

## 🔧 Configuration

Edit `.env` file:

```bash
# Ollama settings
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
OLLAMA_TEMPERATURE=0.1
OLLAMA_TIMEOUT=120

# Logging
LOG_LEVEL=INFO
```

## 📚 Usage Examples

### Basic Agent Usage

```python
from agents.requirements_agent import RequirementsAgent
from agents.data_models import AgentContext

# Create agent
agent = RequirementsAgent()

# Create context
context = AgentContext(
    project_id=1,
    current_query="What are the high-priority requirements?"
)

# Process query
response = agent.process_query(
    query="What are the high-priority requirements?",
    context=context
)

print(response.content)
print(f"Confidence: {response.confidence}")
print(f"Sources: {len(response.sources)}")
```

### Using Ollama Client Directly

```python
from utils.ollama_client import OllamaClient

client = OllamaClient()

# Check if Ollama is running
if client.check_health():
    print("✅ Ollama is ready")
    
    # Generate response
    response = client.generate(
        prompt="Explain what a requirement is in software development",
        temperature=0.1
    )
    print(response)
```

## 🎯 Development Roadmap

### Week 1: Foundation (Current)

- [x] Set up project structure
- [x] Install Ollama
- [x] Create configuration system
- [x] Build Ollama client wrapper
- [x] Implement data models
- [x] Create base agent class
- [x] Set up testing infrastructure
- [ ] Implement first specialized agent (Requirements)
- [ ] Test agent with mock data

### Week 2: Specialized Agents

- [ ] Implement all 6 specialized agents
- [ ] Test each agent individually
- [ ] Create system prompts for each agent
- [ ] Optimize prompts for Llama 3.1

### Week 3: Orchestration

- [ ] Build orchestrator agent
- [ ] Implement query analysis
- [ ] Create agent selection logic
- [ ] Build response synthesis
- [ ] Test multi-agent workflows

### Week 4: Integration & Polish

- [ ] Integrate with Workstream 1 (retrieval)
- [ ] End-to-end testing
- [ ] Performance optimization
- [ ] Documentation

## 🐛 Troubleshooting

### Ollama not running

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start it
ollama serve
```

### Model not found

```bash
# Pull the model
ollama pull llama3.1:8b

# List available models
ollama list
```

### Slow responses

- **Expected**: Local LLM takes 10-30s per query on CPU
- **Solution**: Use GPU if available, or reduce prompt complexity
- **Alternative**: Switch to smaller model (`mistral:7b`)

### JSON parsing errors

- **Expected**: Llama 3.1 sometimes adds markdown formatting
- **Solution**: Implemented in `_parse_response()` method
- **Workaround**: Adjust prompts to be more explicit

### Connection timeout

```bash
# Increase timeout in .env
OLLAMA_TIMEOUT=180
```

## 📖 Next Steps

1. **Run the connection test** to verify your setup
2. **Review the base agent code** to understand the architecture
3. **Implement your first specialized agent** (see Week 1 tasks)
4. **Test with mock data** before Workstream 1 integration

## 🤝 Integration Points

### With Workstream 1 (Data Platform)

- Agents will call `retrieve_context()` which connects to vector search
- Currently using mock data (see `base_agent.py`)
- Integration planned for Week 4

### With Workstream 3 (UI/API)

- API will call orchestrator's `process_query()` method
- Returns structured `OrchestratorResponse` objects
- Integration planned for Week 2-3

## 📝 Notes

- **Local LLM Performance**: Expect 10-30s response times on CPU
- **Cost**: $0 - Everything runs locally!
- **Privacy**: All data stays on your machine
- **Prompt Engineering**: Llama 3.1 prefers simpler, more direct prompts than GPT-4

## 🎓 Learning Resources

- [Ollama Documentation](https://github.com/ollama/ollama)
- [Llama 3.1 Model Card](https://ollama.com/library/llama3.1)
- [Prompt Engineering for Llama](https://llama.meta.com/docs/how-to-guides/prompting/)

---

## **Ready to build agents! 🚀**
