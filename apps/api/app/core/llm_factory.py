"""
LLM Factory - Multi-Provider Support with Automatic Fallback

Provides intelligent LLM provider selection and fallback logic.
Supports OpenAI and Google Gemini with automatic switching based on:
- Available API keys
- User configuration (LLM_PROVIDER setting)
- Runtime failures (fallback)
"""

from typing import Optional, Literal
import logging
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings

logger = logging.getLogger(__name__)

ProviderType = Literal["openai", "gemini"]


class LLMProviderError(Exception):
    """Raised when no LLM provider is available or configured."""
    pass


def _try_openai() -> Optional[BaseChatModel]:
    """
    Attempt to create OpenAI LLM instance.
    
    Returns:
        ChatOpenAI instance if successful, None otherwise
    """
    if not settings.OPENAI_API_KEY:
        logger.debug("OpenAI API key not found, skipping OpenAI")
        return None
    
    try:
        llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            api_key=settings.OPENAI_API_KEY
        )
        logger.info(f"✓ Initialized OpenAI with model: {settings.LLM_MODEL}")
        return llm
    except Exception as e:
        logger.warning(f"Failed to initialize OpenAI: {e}")
        return None


def _try_gemini() -> Optional[BaseChatModel]:
    """
    Attempt to create Google Gemini LLM instance.
    
    Returns:
        ChatGoogleGenerativeAI instance if successful, None otherwise
    """
    if not settings.GOOGLE_API_KEY:
        logger.debug("Google API key not found, skipping Gemini")
        return None
    
    try:
        llm = ChatGoogleGenerativeAI(
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            google_api_key=settings.GOOGLE_API_KEY
        )
        logger.info(f"✓ Initialized Gemini with model: {settings.LLM_MODEL}")
        return llm
    except Exception as e:
        logger.warning(f"Failed to initialize Gemini: {e}")
        return None


def _detect_provider_from_model(model_name: str) -> ProviderType:
    """
    Detect provider from model name pattern.
    
    Args:
        model_name: Model name to analyze
        
    Returns:
        "gemini" if model name contains gemini, otherwise "openai"
    """
    if "gemini" in model_name.lower():
        return "gemini"
    return "openai"


def get_llm() -> BaseChatModel:
    """
    Get configured LLM instance with automatic provider selection and fallback.
    
    Provider Selection Logic:
    1. If LLM_PROVIDER is "openai" or "gemini", try that provider first
    2. If LLM_PROVIDER is "auto", detect from model name or prefer Gemini
    3. If primary provider fails and fallback is enabled, try secondary provider
    4. Raise error if no providers are available
    
    Returns:
        Configured LLM instance (ChatOpenAI or ChatGoogleGenerativeAI)
        
    Raises:
        LLMProviderError: If no providers are available or configured
    """
    provider_preference = settings.LLM_PROVIDER.lower()
    
    # Determine primary and secondary providers
    if provider_preference == "openai":
        primary, secondary = "openai", "gemini"
    elif provider_preference == "gemini":
        primary, secondary = "gemini", "openai"
    else:  # "auto"
        # Auto-detect from model name
        detected = _detect_provider_from_model(settings.LLM_MODEL)
        if detected == "gemini":
            primary, secondary = "gemini", "openai"
        else:
            primary, secondary = "openai", "gemini"
    
    # Try primary provider
    logger.info(f"Attempting to initialize primary provider: {primary}")
    llm = None
    if primary == "openai":
        llm = _try_openai()
    else:
        llm = _try_gemini()
    
    if llm:
        return llm
    
    # Try fallback if enabled
    if settings.LLM_FALLBACK_ENABLED:
        logger.warning(f"Primary provider '{primary}' failed, trying fallback: {secondary}")
        if secondary == "openai":
            llm = _try_openai()
        else:
            llm = _try_gemini()
        
        if llm:
            return llm
    
    # No providers available
    error_msg = (
        "No LLM provider available. Please configure at least one of:\n"
        f"  - OPENAI_API_KEY (currently: {'set' if settings.OPENAI_API_KEY else 'not set'})\n"
        f"  - GOOGLE_API_KEY (currently: {'set' if settings.GOOGLE_API_KEY else 'not set'})"
    )
    logger.error(error_msg)
    raise LLMProviderError(error_msg)


# Create singleton LLM instance at module import
# This ensures consistency across all agent nodes
try:
    llm = get_llm()
except LLMProviderError as e:
    logger.error(f"Failed to initialize LLM on startup: {e}")
    # In production, you might want to raise this or handle gracefully
    # For now, set to None and it will fail at runtime if used
    llm = None
