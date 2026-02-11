"""
Custom Exception Classes
"""

class VaultaError(Exception):
    """Base exception for Vaulta errors."""
    pass


class AuthenticationError(VaultaError):
    """Raised when authentication fails."""
    pass


class VerificationRequiredError(VaultaError):
    """Raised when operation requires verification."""
    pass


class InvalidActionError(VaultaError):
    """Raised when action is invalid or not allowed."""
    pass


class ToolExecutionError(VaultaError):
    """Raised when a banking tool fails."""
    pass
