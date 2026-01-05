"""
Configuration settings for the Agent Framework
"""
import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()


class Settings:
    """Application settings loaded from environment variables"""
    
    # Ollama Configuration
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    OLLAMA_BACKUP_MODEL: str = os.getenv("OLLAMA_BACKUP_MODEL", "mistral:7b")
    OLLAMA_TEMPERATURE: float = float(os.getenv("OLLAMA_TEMPERATURE", "0.1"))
    OLLAMA_TIMEOUT: int = int(os.getenv("OLLAMA_TIMEOUT", "120"))
    
    # Database Configuration (for future integration)
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Agent Configuration
    MAX_RETRIES: int = 3
    MIN_CONFIDENCE_SCORE: float = 0.3
    
    @classmethod
    def validate(cls):
        """Validate that all required settings are present"""
        if not cls.OLLAMA_BASE_URL:
            raise ValueError("OLLAMA_BASE_URL is required")
        return True


# Create global settings instance
settings = Settings()
settings.validate()
