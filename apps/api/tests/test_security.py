"""Tests for security module credential extraction."""
import pytest
from app.core.security import extract_credentials, _digits_after_label


class TestDigitsAfterLabel:
    """Test _digits_after_label function."""
    
    def test_single_digit(self):
        result = _digits_after_label("customer id 1", r'\b(customer id)\b')
        assert result == "1"
    
    def test_two_digits(self):
        result = _digits_after_label("customer id 42", r'\b(customer id)\b')
        assert result == "42"
    
    def test_four_digits(self):
        result = _digits_after_label("customer id 1234", r'\b(customer id)\b')
        assert result == "1234"
    
    def test_spaced_digits(self):
        result = _digits_after_label("customer id 1 2 3 4", r'\b(customer id)\b')
        assert result == "1234"
    
    def test_no_label_match(self):
        result = _digits_after_label("no match here", r'\b(customer id)\b')
        assert result is None
    
    def test_label_without_digits(self):
        result = _digits_after_label("customer id abc", r'\b(customer id)\b')
        assert result is None


class TestExtractCredentials:
    """Test extract_credentials function."""
    
    def test_short_customer_id_with_pin(self):
        """Test case that was failing: single-digit ID with 4-digit PIN."""
        cid, pin = extract_credentials("my id is 1 and pin is 1000")
        assert cid == "1", f"Expected customer_id='1', got '{cid}'"
        assert pin == "1000", f"Expected pin='1000', got '{pin}'"
    
    def test_standard_format(self):
        """Standard 4-digit ID and PIN."""
        cid, pin = extract_credentials("customer id 1234 pin 5678")
        assert cid == "1234"
        assert pin == "5678"
    
    def test_natural_language(self):
        """Natural conversational format."""
        cid, pin = extract_credentials("can you check my account my id is 42 and pin is 9999")
        assert cid == "42"
        assert pin == "9999"
    
    def test_spoken_numbers(self):
        """Voice-transcribed spoken numbers."""
        cid, pin = extract_credentials("id is one and pin is one zero zero zero")
        assert cid == "1"
        assert pin == "1000"
    
    def test_spaced_digits(self):
        """Spaced out digits."""
        cid, pin = extract_credentials("customer id 1 pin 1 0 0 0")
        assert cid == "1"
        assert pin == "1000"
    
    def test_two_digit_customer_id(self):
        """Two-digit customer ID."""
        cid, pin = extract_credentials("id 25 pin 4567")
        assert cid == "25"
        assert pin == "4567"
    
    def test_three_digit_customer_id(self):
        """Three-digit customer ID."""
        cid, pin = extract_credentials("customer id 999 and pin 1111")
        assert cid == "999"
        assert pin == "1111"
    
    def test_explicit_labels(self):
        """Explicit 'customer id is' format."""
        cid, pin = extract_credentials("customer id is 5 pin is 2000")
        assert cid == "5"
        assert pin == "2000"
    
    def test_no_credentials(self):
        """No credentials in text."""
        cid, pin = extract_credentials("hello how are you")
        assert cid is None
        assert pin is None
    
    def test_only_customer_id(self):
        """Only customer ID provided."""
        cid, pin = extract_credentials("my id is 123")
        assert cid == "123"
        assert pin is None
    
    def test_only_pin(self):
        """Only PIN provided."""
        cid, pin = extract_credentials("my pin is 5555")
        assert cid is None
        assert pin == "5555"
    
    def test_empty_input(self):
        """Empty input."""
        cid, pin = extract_credentials("")
        assert cid is None
        assert pin is None
    
    def test_none_input(self):
        """None input."""
        cid, pin = extract_credentials(None)
        assert cid is None
        assert pin is None
    
    def test_pin_longer_than_4_digits_truncated(self):
        """PIN with more than 4 digits should be truncated."""
        cid, pin = extract_credentials("id 10 pin 123456")
        assert cid == "10"
        assert pin == "1234"  # Should truncate to first 4 digits
