"""
Helper script to set up Python path for imports
"""
# Add parent directory to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


"""
Ollama API client wrapper for LLM interactions
"""
import requests
import json
import logging
from typing import Dict, Any, Optional
from config.settings import settings

logger = logging.getLogger(__name__)

class OllamaClient:
    """Wrapper for Ollama API interactions"""
    
    def __init__(
        self,
        model: str = None,
        base_url: str = None,
        temperature: float = None,
        timeout: int = None
    ):
        self.model = model or settings.OLLAMA_MODEL
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.temperature = temperature if temperature is not None else settings.OLLAMA_TEMPERATURE
        self.timeout = timeout or settings.OLLAMA_TIMEOUT
        
        # API endpoints
        self.generate_url = f"{self.base_url}/api/generate"
        self.chat_url = f"{self.base_url}/api/chat"
        
        logger.info(f"OllamaClient initialized with model: {self.model}")
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate a response from the LLM
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Override default temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response
        """
        try:
            # Build the full prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Prepare request payload
            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": temperature if temperature is not None else self.temperature,
                }
            }
            
            if max_tokens:
                payload["options"]["num_predict"] = max_tokens
            
            logger.debug(f"Sending request to Ollama: {payload['model']}")
            
            # Make API request
            response = requests.post(
                self.generate_url,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            generated_text = result.get("response", "")
            
            logger.debug(f"Received response ({len(generated_text)} chars)")
            
            return generated_text
            
        except requests.exceptions.Timeout:
            logger.error("Ollama request timed out")
            raise OllamaException("Request timed out. Try a simpler query or increase timeout.")
        except requests.exceptions.ConnectionError:
            logger.error("Could not connect to Ollama")
            raise OllamaException("Cannot connect to Ollama. Is it running? Try: ollama serve")
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            raise OllamaException(f"HTTP error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise OllamaException(f"Unexpected error: {e}")
    
    def chat(
        self,
        messages: list,
        temperature: Optional[float] = None
    ) -> str:
        """
        Chat-style interaction (maintains conversation context)
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Override default temperature
            
        Returns:
            Generated text response
        """
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature if temperature is not None else self.temperature
                }
            }
            
            response = requests.post(
                self.chat_url,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            generated_text = result.get("message", {}).get("content", "")
            
            return generated_text
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            raise OllamaException(f"Chat error: {e}")
    
    def check_health(self) -> bool:
        """
        Check if Ollama service is available
        
        Returns:
            True if service is healthy, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def list_models(self) -> list:
        """
        List available models
        
        Returns:
            List of model names
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            models = response.json().get("models", [])
            return [model["name"] for model in models]
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []


class OllamaException(Exception):
    """Custom exception for Ollama-related errors"""
    pass


# Global client instance (can be imported elsewhere)
ollama_client = OllamaClient()
