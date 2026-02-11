"""
Admin and observability endpoints.
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException

from app.services.session_manager import session_manager
from app.core.security import sanitize_for_logging
from app.core.config import settings


router = APIRouter()


@router.get("/api/sessions")
async def list_sessions():
    """List all active sessions (sanitized)."""
    sessions = session_manager.list_sessions()
    data = []
    for sid, session in sessions.items():
        data.append({
            "session_id": sid,
            "verified": session.verified,
            "customer_id": session.customer_id,
            "current_flow": session.current_flow,
            "pending_action": session.pending_action,
            "awaiting_confirmation": session.awaiting_confirmation,
            "requires_human": session.requires_human,
            "auth_attempts": session.auth_attempts,
            "locked": session.locked,
            "last_activity": session.last_activity,
            "message_count": len(session.conversation_history),
        })
    return sanitize_for_logging({"count": len(data), "sessions": data})


@router.post("/api/sessions/reset")
async def reset_sessions(payload: Dict[str, Any]):
    """Reset a session or all sessions."""
    session_id = payload.get("session_id") if payload else None
    reset_all = payload.get("reset_all") if payload else False
    if session_id and reset_all:
        raise HTTPException(status_code=400, detail="Provide either session_id or reset_all")

    if session_id:
        count = session_manager.reset_session(session_id)
    elif reset_all:
        count = session_manager.reset_session(None)
    else:
        raise HTTPException(status_code=400, detail="Provide session_id or reset_all=true")

    return {"reset": count}


@router.get("/api/observability/status")
async def observability_status():
    """Return tracing configuration status."""
    tracing_enabled = str(settings.LANGCHAIN_TRACING_V2).lower() == "true"
    return {
        "provider": "LangSmith",
        "tracing_enabled": tracing_enabled,
        "project": settings.LANGCHAIN_PROJECT,
        "pii_redaction": settings.PIN_REDACTION_ENABLED,
    }
