"""
Helper script to set up Python path for imports
Run this before importing config.settings in a Python terminal

Usage:
    python3 setup_path.py
    # or in Python terminal:
    exec(open('setup_path.py').read())
"""
import sys
import os

# Get the directory where this file is located
try:
    workstream_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # If __file__ is not defined (e.g., when using exec), use current working directory
    workstream_dir = os.path.abspath(os.getcwd())
    # Try to find workstream2_agents directory
    if not workstream_dir.endswith('workstream2_agents'):
        # Look for it in the path
        for path in sys.path:
            if 'workstream2_agents' in path:
                workstream_dir = path
                break
        else:
            # Default fallback
            workstream_dir = '/Users/balaji/Documents/Learning/Outskill/GenAI-Capstone-Project/smart-doc-qa/src/workstream2_agents'

# Add to Python path if not already there
if workstream_dir not in sys.path:
    sys.path.insert(0, workstream_dir)
    print(f"Added {workstream_dir} to Python path")
else:
    print(f"{workstream_dir} is already in Python path")

# Now you can import
try:
    from config.settings import settings
    print("✓ Successfully imported config.settings")
    print(f"  OLLAMA_MODEL: {settings.OLLAMA_MODEL}")
    print(f"  OLLAMA_BASE_URL: {settings.OLLAMA_BASE_URL}")
except ImportError as e:
    print(f"✗ Import failed: {e}")

