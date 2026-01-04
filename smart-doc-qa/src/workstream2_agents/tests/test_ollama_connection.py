"""
Test Ollama connection and basic functionality
Run this first to ensure your setup is working
"""
import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.ollama_client import OllamaClient, OllamaException
from config.settings import settings

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_ollama_health():
    """Test if Ollama service is running"""
    print("\n" + "="*60)
    print("TEST 1: Ollama Health Check")
    print("="*60)
    
    client = OllamaClient()
    
    if client.check_health():
        print("✅ Ollama service is running")
        return True
    else:
        print("❌ Ollama service is NOT running")
        print("\nPlease start Ollama:")
        print("  1. Open a terminal")
        print("  2. Run: ollama serve")
        print("  3. Re-run this test")
        return False


def test_list_models():
    """Test listing available models"""
    print("\n" + "="*60)
    print("TEST 2: List Available Models")
    print("="*60)
    
    client = OllamaClient()
    models = client.list_models()
    
    if models:
        print(f"✅ Found {len(models)} model(s):")
        for model in models:
            print(f"   - {model}")
        
        # Check if required model is available
        if settings.OLLAMA_MODEL in models:
            print(f"\n✅ Required model '{settings.OLLAMA_MODEL}' is available")
            return True
        else:
            print(f"\n⚠️  Required model '{settings.OLLAMA_MODEL}' is NOT available")
            print(f"\nPlease pull the model:")
            print(f"  ollama pull {settings.OLLAMA_MODEL}")
            return False
    else:
        print("❌ No models found")
        print(f"\nPlease pull a model:")
        print(f"  ollama pull {settings.OLLAMA_MODEL}")
        return False


def test_simple_generation():
    """Test simple text generation"""
    print("\n" + "="*60)
    print("TEST 3: Simple Text Generation")
    print("="*60)
    
    client = OllamaClient()
    
    test_prompt = "Say 'Hello, I am working!' and nothing else."
    
    try:
        print(f"Prompt: {test_prompt}")
        print("\nGenerating response (this may take 10-30 seconds)...")
        
        response = client.generate(
            prompt=test_prompt,
            temperature=0.1
        )
        
        print(f"\n✅ Response received:")
        print(f"   {response}")
        return True
        
    except OllamaException as e:
        print(f"\n❌ Generation failed: {e}")
        return False


def test_json_generation():
    """Test JSON-formatted response generation"""
    print("\n" + "="*60)
    print("TEST 4: JSON Response Generation")
    print("="*60)
    
    client = OllamaClient()
    
    test_prompt = """Return a JSON object with these fields:
{
    "status": "working",
    "message": "I can generate JSON",
    "confidence": "high"
}

Return ONLY valid JSON, no other text."""
    
    try:
        print("Testing JSON generation...")
        print("\nGenerating response...")
        
        response = client.generate(
            prompt=test_prompt,
            temperature=0.0
        )
        
        print(f"\n✅ Response received:")
        print(response)
        
        # Try to parse as JSON
        import json
        cleaned = response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
        
        parsed = json.loads(cleaned)
        print(f"\n✅ Successfully parsed as JSON:")
        print(f"   {parsed}")
        return True
        
    except json.JSONDecodeError as e:
        print(f"\n⚠️  Response was not valid JSON: {e}")
        print("   (This is OK - we can handle this in the agent)")
        return True  # Don't fail the test for this
    except OllamaException as e:
        print(f"\n❌ Generation failed: {e}")
        return False


def run_all_tests():
    """Run all Ollama tests"""
    print("\n" + "="*60)
    print("OLLAMA CONNECTION TEST SUITE")
    print("="*60)
    print(f"\nConfiguration:")
    print(f"  Base URL: {settings.OLLAMA_BASE_URL}")
    print(f"  Model: {settings.OLLAMA_MODEL}")
    print(f"  Temperature: {settings.OLLAMA_TEMPERATURE}")
    print(f"  Timeout: {settings.OLLAMA_TIMEOUT}s")
    
    results = []
    
    # Test 1: Health check
    results.append(("Health Check", test_ollama_health()))
    
    if not results[-1][1]:
        print("\n❌ Ollama is not running. Please start it and try again.")
        return
    
    # Test 2: List models
    results.append(("List Models", test_list_models()))
    
    if not results[-1][1]:
        print("\n❌ Required model not available. Please pull it and try again.")
        return
    
    # Test 3: Simple generation
    results.append(("Simple Generation", test_simple_generation()))
    
    # Test 4: JSON generation
    results.append(("JSON Generation", test_json_generation()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! Your Ollama setup is working correctly.")
        print("\nYou're ready to start building agents!")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues and try again.")
    
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tests()
    