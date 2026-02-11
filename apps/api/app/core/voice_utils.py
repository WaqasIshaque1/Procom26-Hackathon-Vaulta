"""
Voice-to-Text Number Normalization

Converts spoken numbers (e.g., "one two three four") to digits ("1234").
This is essential for voice-based authentication where users speak their credentials.
"""

import re
from typing import Optional


# Mapping of spoken words to digits
WORD_TO_DIGIT = {
    "zero": "0", "oh": "0", "o": "0",
    "one": "1", "won": "1",
    "two": "2", "to": "2", "too": "2",
    "three": "3", "tree": "3",
    "four": "4", "for": "4", "fore": "4",
    "five": "5",
    "six": "6", "sex": "6",
    "seven": "7",
    "eight": "8", "ate": "8",
    "nine": "9", "niner": "9",

    "thousand": "000",
    "hundred": "00",
}


def normalize_spoken_digits(text: str) -> str:
    """
    Convert spoken numbers to digits in text.
    
    Examples:
        "one two three four" → "1234"
        "my pin is five six seven eight" → "my pin is 5678"
        "customer id one two three four pin five six seven eight" 
            → "customer id 1234 pin 5678"
    
    Args:
        text: Input text that may contain spoken numbers
        
    Returns:
        Text with spoken numbers converted to digits
    """
    if not text:
        return text
    
    # Convert to lowercase for matching
    normalized = text.lower()
    
    # Replace each spoken number with its digit
    for word, digit in WORD_TO_DIGIT.items():
        # Use word boundaries to avoid partial matches
        pattern = r'\b' + re.escape(word) + r'\b'
        normalized = re.sub(pattern, digit, normalized)
    
    return normalized


def extract_digits_from_voice(text: str) -> Optional[str]:
    """
    Extract a sequence of digits from voice-transcribed text.
    
    Handles both actual digits and spoken number words.
    
    Examples:
        "one two three four" → "1234"
        "1 2 3 4" → "1234"
        "my number is one two three four" → "1234"
    
    Args:
        text: Voice-transcribed text
        
    Returns:
        Extracted digit sequence, or None if not found
    """
    # First normalize spoken numbers to digits
    normalized = normalize_spoken_digits(text)
    
    # Extract all digits (ignoring spaces/punctuation)
    digits = re.findall(r'\d', normalized)
    
    if digits:
        return ''.join(digits)
    
    return None


# Test function
if __name__ == "__main__":
    test_cases = [
        ("one two three four", "1234"),
        ("my pin is five six seven eight", "my pin is 5678"),
        ("customer id one two three four and pin five six seven eight", 
         "customer id 1234 and pin 5678"),
        ("1 2 3 4", "1234"),  # Already digits
        ("my id is one oh two three", "my id is 1023"),
    ]
    
    print("Testing normalize_spoken_digits:")
    for input_text, expected in test_cases:
        result = normalize_spoken_digits(input_text)
        status = "✓" if expected in result else "✗"
        print(f"{status} '{input_text}' → '{result}'")
