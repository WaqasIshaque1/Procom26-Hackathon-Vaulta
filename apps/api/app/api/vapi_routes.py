"""
Vapi-compatible Endpoints

Implements OpenAI-compatible /chat/completions and Vapi webhooks.
"""

import json
import time
import uuid
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, HTTPException, Request, Header
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from pydantic import ConfigDict
from langchain_core.messages import HumanMessage, AIMessage

from app.agents.graph import agent_graph
from app.agents.state import create_initial_state
from app.services.session_manager import session_manager
from app.services.banking_api import verify_identity
from app.core.security import (
    redact_sensitive_text,
    extract_credentials,
    remove_credentials,
    sanitize_for_logging,
    hash_customer_id,
)
from app.core.logging_utils import log_exception
from app.core.config import settings


router = APIRouter()


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = None
    stream: Optional[bool] = False
    session_id: Optional[str] = None
    user: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    call: Optional[Dict[str, Any]] = None
    call: Optional[Dict[str, Any]] = None  # Vapi includes call.id here

    model_config = ConfigDict(extra="allow")


class VapiCallRequest(BaseModel):
    """Flexible payload for Vapi-style calls."""
    session_id: Optional[str] = None
    message: Optional[Dict[str, Any]] = None
    call: Optional[Dict[str, Any]] = None
    input: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(extra="allow")


# =============================================================================
# Helpers
# =============================================================================

def _resolve_session_id(
    request: Optional[ChatCompletionRequest] = None,
    payload: Optional[Dict[str, Any]] = None,
    header_session_id: Optional[str] = None,
) -> str:
    # Priority 1: Explicit session_id
    if request and request.session_id:
        return request.session_id
    # Priority 2: User field (sometimes used as session identifier)
    if request and request.user:
        return request.user
    # Priority 3: Vapi Custom LLM includes call.id in the request
    if request and request.call and request.call.get("id"):
        return request.call["id"]
    # Priority 4: Session ID in metadata
    if request and request.metadata and request.metadata.get("session_id"):
        return request.metadata["session_id"]
    if request and request.call and request.call.get("id"):
        return request.call["id"]
    # Priority 5: From raw payload (for VapiCallRequest)
    if payload:
        if payload.get("session_id"):
            return payload["session_id"]
        if payload.get("call") and payload["call"].get("id"):
            return payload["call"]["id"]
        if payload.get("metadata") and payload["metadata"].get("session_id"):
            return payload["metadata"]["session_id"]
        if payload.get("conversation_id"):
            return payload["conversation_id"]
    # Priority 6: Session ID from header
    if header_session_id:
        return header_session_id
    # Fallback: Generate new session ID
    return f"session-{uuid.uuid4()}"


def _extract_latest_user_input(messages: List[ChatMessage]) -> str:
    user_messages = [m for m in messages if m.role == "user"]
    if not user_messages:
        raise HTTPException(status_code=400, detail="No user message provided")
    return user_messages[-1].content


def _extract_last_user_from_turns(turns: Any) -> Optional[str]:
    if not isinstance(turns, list):
        return None
    for item in reversed(turns):
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        if role != "user":
            continue
        return item.get("content") or item.get("message") or item.get("text")
    return None


def _extract_user_text_from_payload(payload: Dict[str, Any]) -> Optional[str]:
    # Common Vapi-style shapes
    message = payload.get("message")
    if isinstance(message, dict):
        if message.get("type") == "conversation-update":
            # Vapi can send full conversation arrays
            text = _extract_last_user_from_turns(message.get("conversation"))
            if text:
                return text
            text = _extract_last_user_from_turns(message.get("messages"))
            if text:
                return text
        if message.get("content"):
            return message.get("content")
        if message.get("text"):
            return message.get("text")

    # Some payloads include top-level conversation/messages arrays
    text = _extract_last_user_from_turns(payload.get("conversation"))
    if text:
        return text
    text = _extract_last_user_from_turns(payload.get("messages"))
    if text:
        return text

    if payload.get("input") and isinstance(payload["input"], dict):
        if payload["input"].get("text"):
            return payload["input"]["text"]
    if payload.get("text"):
        return payload["text"]
    return None


async def _process_auth_attempt(session, raw_text: str) -> Dict[str, Any]:
    auth = {
        "attempted": False,
        "success": None,
        "remaining_attempts": None,
        "locked": session.locked,
        "needs_customer_id": False,
        "needs_pin": False,
    }

    if session.verified:
        return auth

    customer_id, pin = extract_credentials(raw_text)

    if session.pending_customer_id and customer_id and not pin:
        # Treat single 4-digit input as PIN when customer_id is already pending
        pin = customer_id
        customer_id = session.pending_customer_id

    if customer_id and not pin:
        session.pending_customer_id = customer_id
        auth["needs_pin"] = True
        return auth

    if pin and not customer_id and session.pending_customer_id:
        customer_id = session.pending_customer_id
    elif pin and not customer_id:
        auth["needs_customer_id"] = True
        return auth

    if not (customer_id and pin):
        return auth

    auth["attempted"] = True

    # Lockout check
    if session.locked or session.auth_attempts >= settings.MAX_AUTH_ATTEMPTS:
        session.locked = True
        auth["locked"] = True
        auth["success"] = False
        return auth

    is_verified = await verify_identity(customer_id, pin)
    if is_verified:
        session.verified = True
        session.customer_id = customer_id
        session.auth_attempts = 0
        session.pending_customer_id = None
        auth["success"] = True
    else:
        session.auth_attempts += 1
        remaining = max(0, settings.MAX_AUTH_ATTEMPTS - session.auth_attempts)
        auth["success"] = False
        auth["remaining_attempts"] = remaining
        if remaining == 0:
            session.locked = True
            auth["locked"] = True

    return auth


async def _run_agent(
    session_id: str,
    sanitized_input: str,
    auth: Dict[str, Any],
) -> Dict[str, Any]:
    session = session_manager.get_or_create_session(session_id)

    # Limit conversation history to prevent LangSmith payload from exceeding 20MB limit
    # Each message can be ~100-500 bytes, so 10 messages = max ~5KB for history
    # This prevents the 37MB payload issue seen in logs
    MAX_HISTORY_MESSAGES = 10  # Last 5 exchanges (user + assistant)
    history = session.conversation_history or []
    
    if len(history) > MAX_HISTORY_MESSAGES:
        # Keep only the most recent messages
        history = history[-MAX_HISTORY_MESSAGES:]

    # Build state with sanitized messages only
    current_state = create_initial_state(session_id)
    current_state["messages"] = history + [HumanMessage(content=sanitized_input)]
    current_state["verified"] = session.verified
    current_state["customer_id"] = hash_customer_id(session.customer_id) if session.customer_id else None
    current_state["current_flow"] = session.current_flow
    current_state["original_intent"] = session.original_intent
    current_state["pending_action"] = session.pending_action
    current_state["requires_human"] = session.requires_human
    
    # NEW: Check if user just authenticated and has a stored original intent
    if session.original_intent and session.verified and len(history) <= 4:
        # Just authenticated - restore flow and add a flag to skip intent router
        current_state["current_flow"] = session.original_intent
        current_state["metadata"] = {
            "auth": auth,
            "awaiting_confirmation": session.awaiting_confirmation,
            "asked_for_confirmation": False,
            "lock_flow": True,  # Lock flow so we don't re-route
            "timestamp": int(time.time()),
        }
        # Clear original_intent from session after restoring
        session_manager.update_session(session_id, original_intent=None)
    else:
        current_state["metadata"] = {
            "auth": auth,
            "awaiting_confirmation": session.awaiting_confirmation,
            "asked_for_confirmation": False,
            "lock_flow": bool(session.awaiting_confirmation or session.pending_action),
            "timestamp": int(time.time()),
        }

    # LangSmith tracing config (sanitized state only)
    config = {
        "configurable": {"thread_id": session_id},
        "tags": ["vaulta", "api:chat"],
        "run_name": "vaulta-agent",
    }

    result = await agent_graph.ainvoke(current_state, config=config)

    # NEW: Check if auth was just requested - store current flow as original_intent
    last_message_content = result.get("messages", [])[-1].content if result.get("messages") else ""
    is_auth_request = ("customer id" in last_message_content.lower() and "pin" in last_message_content.lower())
    
    if is_auth_request and result.get("current_flow") and not session.verified:
        # Auth just requested - save the current flow so we can restore it after auth
        session_manager.update_session(session_id, original_intent=result.get("current_flow"))

    # Update session state
    session_manager.update_session(
        session_id,
        verified=result.get("verified"),
        current_flow=result.get("current_flow"),
        pending_action=result.get("pending_action"),
        awaiting_confirmation=result.get("metadata", {}).get("awaiting_confirmation"),
        requires_human=result.get("requires_human"),
        conversation_history=result.get("messages"),
        locked=session.locked,
    )

    # Extract assistant response
    assistant_messages = [m for m in result["messages"] if isinstance(m, AIMessage)]
    response_content = assistant_messages[-1].content if assistant_messages else "I'm not sure how to respond to that."

    return {
        "response": response_content,
        "state": result,
    }


def _format_openai_response(response_content: str, session_id: str) -> Dict[str, Any]:
    return {
        "id": f"chatcmpl-{uuid.uuid4()}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "vaulta-agent",
        "session_id": session_id,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_content,
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        },
    }


def _sse_response(payload: Dict[str, Any]) -> StreamingResponse:
    async def event_stream():
        data = json.dumps({
            "id": payload["id"],
            "object": "chat.completion.chunk",
            "created": payload["created"],
            "model": payload["model"],
            "choices": [
                {
                    "index": 0,
                    "delta": {"content": payload["choices"][0]["message"]["content"]},
                    "finish_reason": None,
                }
            ],
        })
        yield f"data: {data}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# =============================================================================
# Routes
# =============================================================================

@router.post("/chat/completions")
async def chat_completions(request: ChatCompletionRequest, x_session_id: Optional[str] = Header(None)):
    """
    OpenAI-compatible chat completions endpoint.
    """
    session_id = _resolve_session_id(request=request, header_session_id=x_session_id)
    session = session_manager.get_or_create_session(session_id)

    raw_user_input = _extract_latest_user_input(request.messages)

    # Process auth attempt using raw input (never stored or traced)
    auth = await _process_auth_attempt(session, raw_user_input)

    # Sanitize user input before tracing/logging
    sanitized_input = redact_sensitive_text(raw_user_input)

    # Detect auth-only messages and keep last intent for routing
    intent_text = remove_credentials(raw_user_input)
    auth_only = bool(auth.get("attempted") or auth.get("needs_pin") or auth.get("needs_customer_id"))
    if not auth_only:
        session.last_intent_message = sanitized_input
    effective_input = session.last_intent_message if auth_only and session.last_intent_message else sanitized_input

    try:
        result = await _run_agent(session_id, effective_input, auth)
        response_content = result["response"]
    except Exception as e:
        log_exception("Agent execution failed", e)
        raise HTTPException(status_code=500, detail="Agent execution failed") from e

    payload = _format_openai_response(response_content, session_id)

    if request.stream:
        return _sse_response(payload)

    return payload


@router.post("/api/call")
async def vapi_call(request: VapiCallRequest, x_session_id: Optional[str] = Header(None)):
    """
    Vapi-style call endpoint for direct webhook integrations.
    """
    payload = request.model_dump()
    session_id = _resolve_session_id(payload=payload, header_session_id=x_session_id)
    session = session_manager.get_or_create_session(session_id)

    raw_user_input = _extract_user_text_from_payload(payload)
    if not raw_user_input:
        raise HTTPException(status_code=400, detail="No user input provided")

    auth = await _process_auth_attempt(session, raw_user_input)
    sanitized_input = redact_sensitive_text(raw_user_input)

    intent_text = remove_credentials(raw_user_input)
    auth_only = bool(auth.get("attempted") or auth.get("needs_pin") or auth.get("needs_customer_id"))
    if not auth_only:
        session.last_intent_message = sanitized_input
    effective_input = session.last_intent_message if auth_only and session.last_intent_message else sanitized_input

    try:
        result = await _run_agent(session_id, effective_input, auth)
        response_content = result["response"]
    except Exception as e:
        log_exception("Agent execution failed", e)
        raise HTTPException(status_code=500, detail="Agent execution failed") from e

    return {
        "session_id": session_id,
        "response": response_content,
    }


@router.post("/api/vapi/webhook")
async def vapi_webhook(request: Request, x_vapi_signature: Optional[str] = Header(None)):
    """
    Vapi webhook handler for tool calls and assistant coordination.
    """
    if settings.VAPI_WEBHOOK_SECRET:
        if not x_vapi_signature or x_vapi_signature != settings.VAPI_WEBHOOK_SECRET:
            raise HTTPException(status_code=401, detail="Invalid webhook signature")

    payload = await request.json()
    # Basic ack - can be extended to handle tool call events
    return {"status": "received", "payload": sanitize_for_logging(payload)}


@router.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Fetch a single session state (sanitized)."""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    data = {
        "session_id": session.session_id,
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
    }
    return sanitize_for_logging(data)
