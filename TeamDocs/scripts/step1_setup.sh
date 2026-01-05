#!/bin/bash

# Navigate to your project root
cd ~/Documents/Learning/Outskill/GenAI-Capstone-Project/smart-doc-qa/src

# Create Workstream 2 directory structure
mkdir -p workstream2_agents
cd workstream2_agents

# Create subdirectories
mkdir -p agents
mkdir -p orchestrator
mkdir -p utils
mkdir -p tests
mkdir -p config
mkdir -p prompts

# Create __init__.py files to make them Python packages
touch agents/__init__.py
touch orchestrator/__init__.py
touch utils/__init__.py
touch tests/__init__.py
touch config/__init__.py
touch prompts/__init__.py

# Create main files
touch main.py
touch requirements.txt
touch .env.example
touch README.md

cd agents
touch base_agent.py
touch requirements_agent.py
touch business_rules_agent.py
touch design_agent.py
touch tech_specs_agent.py
touch contracts_agent.py
touch proposals_agent.py

cd ../orchestrator
touch orchestrator_agent.py

cd ../utils
touch ollama_client.py
touch prompt_builder.py
touch response_parser.py

cd ../prompts
touch agent_prompts.py

cd ../config
touch settings.py

cd ../tests
touch test_agents.py
touch test_orchestrator.py

cd ../..

echo "Directory structure created successfully"

```

**Your directory structure should look like:**
```
workstream2_agents/
├── agents/
│   ├── __init__.py
│   ├── base_agent.py          # Base agent class
│   ├── requirements_agent.py  # Requirements specialist
│   ├── business_rules_agent.py
│   ├── design_agent.py
│   ├── tech_specs_agent.py
│   ├── contracts_agent.py
│   └── proposals_agent.py
├── orchestrator/
│   ├── __init__.py
│   └── orchestrator_agent.py  # Main orchestrator
├── utils/
│   ├── __init__.py
│   ├── ollama_client.py       # Ollama API wrapper
│   ├── prompt_builder.py      # Prompt utilities
│   └── response_parser.py     # Response parsing
├── prompts/
│   ├── __init__.py
│   └── agent_prompts.py       # All system prompts
├── config/
│   ├── __init__.py
│   └── settings.py            # Configuration
├── tests/
│   ├── __init__.py
│   ├── test_agents.py
│   └── test_orchestrator.py
├── main.py                     # Demo/testing script
├── requirements.txt
├── .env.example
└── README.md
