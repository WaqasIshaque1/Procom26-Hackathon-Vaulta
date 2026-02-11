"""
Configuration Settings for Vaulta Backend.
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """
    Application settings using Pydantic Settings.
    Environment variables will override these defaults.
    """
    
    # API Configuration
    PROJECT_NAME: str = "Vaulta Voice Agent"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    
    # Security
    PIN_REDACTION_ENABLED: bool = True
    MAX_AUTH_ATTEMPTS: int = 3
    SESSION_TIMEOUT: int = 300  # 5 minutes

    # Logging
    LOG_ERRORS_ENABLED: bool = False
    LOG_REQUESTS_ENABLED: bool = False
    LOG_REQUEST_BODY: bool = False
    LOG_REQUEST_BODY_MAX_CHARS: int = 2000
    
    # LLM Provider Configuration
    LLM_PROVIDER: str = "auto"  # Options: auto, openai, gemini
    LLM_MODEL: str = "gemini-2.0-flash-exp"  # Model name (provider-specific)
    LLM_TEMPERATURE: float = 0.0
    LLM_FALLBACK_ENABLED: bool = True
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = None
    
    # Google Gemini Configuration
    GOOGLE_API_KEY: Optional[str] = None
    
    # Database Configuration
    DATABASE_URL: str = "postgresql://neondb_owner:npg_B9fYFZWk5Tld@ep-steep-forest-aiuvikcy-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"
    
    # LangChain / LangSmith
    LANGCHAIN_TRACING_V2: str = "true"
    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_PROJECT: str = "vaulta"
    
    # Vapi Integration
    VAPI_API_KEY: Optional[str] = None
    VAPI_WEBHOOK_SECRET: Optional[str] = None
    
    # CORS
    ALLOWED_ORIGINS: str | List[str] = "*"

    @field_validator('ALLOWED_ORIGINS', mode='before')
    @classmethod
    def parse_origins(cls, v):
        """Parse ALLOWED_ORIGINS from string or list."""
        if v is None:
            return ["*"]
        if isinstance(v, str):
            # Handle single value like "*" or comma-separated values
            return [origin.strip() for origin in v.split(",")]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
