"""
PII Protection & Security Utilities

CRITICAL: This module ensures sensitive data NEVER reaches LangSmith.
"""

import re
import hashlib
from typing import Any, Dict, List, Optional, Tuple


def redact_pin(text: str) -> str:
    """
    Redact 4-digit PIN codes from text.
    
    Pattern: Replaces any 4 consecutive digits with ****
    
    Examples:
        "My PIN is 5678" → "My PIN is ****"
        "5678" → "****"
        "Card 1234 PIN 5678" → "Card **** PIN ****"
    
    Args:
        text: Input text that may contain PINs
        
    Returns:
        Text with PINs redacted
    """
    # Match exactly 4 digits (with word boundaries to avoid matching card numbers)
    pattern = r'\b\d{4}\b'
    return re.sub(pattern, '****', text)


def redact_customer_ids(text: str) -> str:
    """
    Redact customer IDs from free-form text.

    Example:
        "Customer ID 1234" -> "Customer ID ****"
    """
    pattern = r'\b(customer id|customer_id|cust id)\s*[:#-]?\s*(\d{4,10})\b'
    def _mask(match: re.Match) -> str:
        label = match.group(1)
        return f"{label} ****"
    return re.sub(pattern, _mask, text, flags=re.IGNORECASE)


def mask_long_numbers(text: str) -> str:
    """
    Mask long numeric sequences that could be account numbers.

    Example:
        "4321567890" -> "******7890"
    """
    def _mask(match: re.Match) -> str:
        num = match.group()
        if len(num) <= 4:
            return "****"
        return "*" * (len(num) - 4) + num[-4:]

    pattern = r'\b\d{8,16}\b'
    return re.sub(pattern, _mask, text)


def redact_sensitive_text(text: str) -> str:
    """
    Redact sensitive data from free-form user text before logging or tracing.
    """
    if not text:
        return text
    # Redact labeled PINs (including ASR "ping") and customer IDs even when digits are spaced (e.g., "1 2 3 4")
    text = re.sub(r'\bpin\b|\bping\b', 'PIN', text, flags=re.IGNORECASE)
    text = re.sub(r'\bPIN\b(?:\s*[:#-]?\s*(?:\d\D*){4})', 'PIN ****', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(customer id|customer_id|cust id)\b(?:\s*[:#-]?\s*(?:\d\D*){4})', r'\1 ****', text, flags=re.IGNORECASE)
    text = redact_pin(text)
    text = redact_customer_ids(text)
    text = mask_long_numbers(text)
    return text


def _digits_after_label(text: str, label_pattern: str) -> Optional[str]:
    """
    Extract digits immediately after a label pattern.
    
    Extracts consecutive digits or spaced digits that appear immediately after 
    the label, stopping at the next word boundary or label.
    
    Returns:
        1-10 digits after the label, or None if not found
    """
    match = re.search(label_pattern, text, flags=re.IGNORECASE)
    if not match:
        return None
    after = text[match.end():]
    
    # Match optional "is" keyword and then digits (possibly spaced)
    # Stop at next alphabetic word or label (pin, customer, id, etc)
    # Pattern: optional spaces, optional "is", then capture digits and spaces until next word (allowing punctuation)
    digit_match = re.match(r'\s*(?:is\s+)?([0-9\s]+?)(?:[.,?!]*(?:\s+(?:and|pin|customer|id|cust|my|the|a)\b|$))', after, re.IGNORECASE)
    
    if digit_match:
        # Extract just the digits (remove spaces)
        digits = re.findall(r'\d', digit_match.group(1))
        if digits:
            # Return 1-10 digits
            return ''.join(digits[:10])
    
    return None


def extract_credentials(text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract customer_id and PIN from user input without persisting them.
    Handles both typed digits and voice-transcribed spoken numbers.

    Returns:
        (customer_id, pin) tuple if found, otherwise (None, None)
    """
    if not text:
        return None, None
    
    # Import voice normalization utility
    try:
        from app.core.voice_utils import normalize_spoken_digits
        # Normalize spoken numbers like "one two three four" → "1234"
        text = normalize_spoken_digits(text)
    except ImportError:
        pass  # Fallback if voice_utils not available
    
    # Extract using labels first (now supports any length)
    customer_id = _digits_after_label(text, r'\b(customer id|customer_id|cust id|id)\b')
    pin = _digits_after_label(text, r'\bpin\b|\bping\b')
    
    # If PIN is extracted via label, enforce 4-digit requirement
    if pin and len(pin) > 4:
        pin = pin[:4]
    
    # If no labeled extraction, try pattern matching
    if not customer_id or not pin:
        # Look for "id X pin Y" or "id X and pin Y" patterns
        pattern = re.search(r'\bid\s+(?:is\s+)?(\d+).*?\bpin\s+(?:is\s+)?(\d+)', text, re.IGNORECASE)
        if pattern:
            if not customer_id:
                customer_id = pattern.group(1)
            if not pin:
                pin = pattern.group(2)
                if len(pin) > 4:
                    pin = pin[:4]
    
    # Fallback: Contiguous 4-digit sequences only if still missing
    if not customer_id or not pin:
        sequences = re.findall(r'\b\d{4}\b', text)
        
        # If we already have a PIN, remove one instance of it from sequences
        # to prevent treating the PIN we already found as a new ID
        if pin and pin in sequences:
            sequences.remove(pin)
            
        if sequences:
            if not customer_id:
                customer_id = sequences[0]
                # If we used this sequence for ID, check if we have a second one for PIN
                if len(sequences) > 1 and not pin:
                    pin = sequences[1]
            elif not pin and len(sequences) > 0:
                # We have ID but no PIN, use first sequence as PIN
                pin = sequences[0]
    
    return customer_id, pin


def remove_credentials(text: str) -> str:
    """
    Remove credential-like patterns from text to detect intent-only content.
    """
    if not text:
        return text
    text = re.sub(r'\b(customer id|customer_id|cust id)\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\b\d{4}\b', '', text)
    text = re.sub(r'\bpin\b|\bping\b', '', text, flags=re.IGNORECASE)
    return text


def mask_account_number(account_num: str) -> str:
    """
    Mask account number to show only last 4 digits.
    
    Examples:
        "1234567890" → "******7890"
        "ACCT123456" → "******3456"
    
    Args:
        account_num: Full account number
        
    Returns:
        Masked account number
    """
    if len(account_num) <= 4:
        return "****"
    return "*" * (len(account_num) - 4) + account_num[-4:]


def hash_customer_id(customer_id: str) -> str:
    """
    Create a hash of customer ID for logging.
    
    This allows us to track the same customer across logs
    without exposing their actual ID.
    
    Args:
        customer_id: Customer's unique identifier
        
    Returns:
        SHA256 hash (first 8 characters)
    """
    return hashlib.sha256(customer_id.encode()).hexdigest()[:8]


def sanitize_for_logging(data: Any) -> Any:
    """
    Recursively sanitize data structure for safe logging.
    
    Removes/masks:
    - PINs (4-digit codes)
    - Account numbers (shows last 4 only)
    - Customer IDs (hashed)
    - SSNs
    - Passwords
    
    Args:
        data: Any data structure (dict, list, str, etc.)
        
    Returns:
        Sanitized version safe for LangSmith
    """
    
    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            # Check if key is sensitive
            if key.lower() in ["pin", "password", "ssn", "secret", "token"]:
                sanitized[key] = "***REDACTED***"
            elif key.lower() == "customer_id":
                sanitized[key] = hash_customer_id(str(value)) if value else None
            elif key.lower() in ["account_number", "account_num"]:
                sanitized[key] = mask_account_number(str(value)) if value else None
            else:
                sanitized[key] = sanitize_for_logging(value)
        return sanitized
    
    elif isinstance(data, list):
        return [sanitize_for_logging(item) for item in data]
    
    elif isinstance(data, str):
        # Redact PINs from strings
        return redact_sensitive_text(data)
    
    else:
        return data


# Custom exception classes
class SecurityError(Exception):
    """Base class for security-related errors"""
    pass


class PINRedactionError(SecurityError):
    """Raised when PIN redaction fails"""
    pass
