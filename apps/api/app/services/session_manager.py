"""
Session State Manager with Automatic Cleanup

Manages in-memory session state for active conversations.
"""

from typing import Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import time
import asyncio


@dataclass
class SessionState:
    """Single conversation session."""
    session_id: str
    customer_id: Optional[str] = None
    verified: bool = False
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    auth_attempts: int = 0
    conversation_history: list = field(default_factory=list)
    last_intent_message: Optional[str] = None
    pending_customer_id: Optional[str] = None
    current_flow: Optional[str] = None
    original_intent: Optional[str] = None  # NEW: Preserve intent through auth
    pending_action: Optional[dict] = None
    awaiting_confirmation: bool = False
    requires_human: bool = False
    locked: bool = False


_UNSET = object()


class SessionManager:
    """
    Manages all active sessions with automatic cleanup.
    
    In production: Replace with Redis or database.
    For POC: In-memory dictionary.
    """
    
    def __init__(self, session_timeout: int = 300):
        """
        Args:
            session_timeout: Session timeout in seconds (default: 5 minutes)
        """
        self.sessions: Dict[str, SessionState] = {}
        self.session_timeout = session_timeout
        self._cleanup_task = None
    
    def get_or_create_session(self, session_id: str) -> SessionState:
        """Get existing session or create new one."""
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionState(session_id=session_id)
        else:
            # Update last activity
            self.sessions[session_id].last_activity = time.time()
        
        return self.sessions[session_id]
    
    def get_session(self, session_id: str) -> Optional[SessionState]:
        """Retrieve session by ID."""
        return self.sessions.get(session_id)
    
    def update_session(
        self,
        session_id: str,
        verified: Optional[bool] = _UNSET,
        customer_id: Optional[str] = _UNSET,
        increment_auth_attempts: bool = False,
        current_flow: Optional[str] = _UNSET,
        original_intent: Optional[str] = _UNSET,
        pending_action: Optional[dict] = _UNSET,
        awaiting_confirmation: Optional[bool] = _UNSET,
        requires_human: Optional[bool] = _UNSET,
        locked: Optional[bool] = _UNSET,
        conversation_history: Optional[list] = _UNSET,
        last_intent_message: Optional[str] = _UNSET
    ):
        """Update session state."""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            
            if verified is not _UNSET:
                session.verified = verified
            if customer_id is not _UNSET:
                session.customer_id = customer_id
            if increment_auth_attempts:
                session.auth_attempts += 1
            if current_flow is not _UNSET:
                session.current_flow = current_flow
            if original_intent is not _UNSET:
                session.original_intent = original_intent
            if pending_action is not _UNSET:
                session.pending_action = pending_action
            if awaiting_confirmation is not _UNSET:
                session.awaiting_confirmation = awaiting_confirmation
            if requires_human is not _UNSET:
                session.requires_human = requires_human
            if locked is not _UNSET:
                session.locked = locked
            if conversation_history is not _UNSET:
                session.conversation_history = conversation_history
            if last_intent_message is not _UNSET:
                session.last_intent_message = last_intent_message
            
            session.last_activity = time.time()

    def list_sessions(self) -> Dict[str, SessionState]:
        """Return all sessions."""
        return self.sessions

    def reset_session(self, session_id: Optional[str] = None) -> int:
        """Reset a single session or all sessions. Returns count reset."""
        if session_id:
            if session_id in self.sessions:
                del self.sessions[session_id]
                return 1
            return 0
        count = len(self.sessions)
        self.sessions = {}
        return count
    
    def cleanup_expired_sessions(self):
        """Remove sessions exceeding timeout."""
        current_time = time.time()
        expired = [
            sid for sid, session in self.sessions.items()
            if current_time - session.last_activity > self.session_timeout
        ]
        
        for sid in expired:
            del self.sessions[sid]
        
        return len(expired)
    
    async def start_cleanup_task(self):
        """Start background task for periodic cleanup."""
        while True:
            await asyncio.sleep(60)  # Run every minute
            expired_count = self.cleanup_expired_sessions()
            if expired_count > 0:
                print(f"🧹 Cleaned up {expired_count} expired sessions")


# Global session manager instance
session_manager = SessionManager()
