"""
LangGraph Workflow Definition

This is the BRAIN of the Vaulta Voice Agent.
Orchestrates the entire conversation flow through a state machine architecture.

ARCHITECTURE OVERVIEW:
======================
- Uses LangGraph for stateful conversation management
- State flows through nodes (functions) via edges (transitions)
- Conditional edges enable dynamic routing based on state
- Each node receives AgentState, processes it, returns updated state

KEY DESIGN DECISIONS:
=====================
1. Separate greeting handler to avoid premature auth requests
2. Auth gate only checks sensitive flows (card_issues, account_servicing)  
3. Flow locking prevents unintended topic switching mid-conversation
4. Confirmation node handles high-risk actions (card blocking, account closure)
5. Intent preservation through authentication interruptions

FLOW DIAGRAM:
=============
                      ┌──────────────┐
                      │ intent_router│  ← Entry point
                      └──────┬───────┘
                             │
                    ┌────────┴─────────┐
              small_talk?              intent
                    │                   │
              ┌─────▼─────┐       ┌────▼────────┐
              │  greeting │       │  auth_gate  │  ← Checks if auth needed
              └─────┬─────┘       └────┬────────┘
                    │                  │
                   END         ┌───────┴────────┐
                               │                │
                          needs_auth      verified/non-sensitive
                               │                │
                        ┌──────▼──────┐   ┌─────▼────────┐
                        │request_auth │   │route_by_intent│  ← Dummy router node
                        └──────┬──────┘   └─────┬────────┘
                               │                │
                              END        ┌──────┴──────┐
                                         │             │
                                    card_flow    account_flow
                                         │             │
                                         └─────┬───────┘
                                               │
                                       ┌───────▼────────┐
                                       │ confirmation?  │  ← If high-risk action
                                       └───────┬────────┘
                                               │
                                              END
"""

from typing import Literal
from langgraph.graph import StateGraph, END

from app.agents.state import AgentState
from app.agents.nodes.intent_router import route_intent
from app.agents.nodes.auth_gate import check_authentication, request_verification
from app.agents.nodes.greeting_handler import handle_greeting
from app.agents.nodes.card_flow import handle_card_flow
from app.agents.nodes.account_flow import handle_account_flow
from app.agents.nodes.stub_flows import handle_stub_flow
from app.agents.nodes.confirmation import handle_confirmation
from app.agents.nodes.escalation import escalate_to_human
from app.core.llm_factory import llm


# =============================================================================
# CONDITIONAL EDGE FUNCTIONS
# 
# These functions determine graph routing based on current state.
# CRITICAL: Must return node NAME (string), not function reference.
# =============================================================================

def should_handle_small_talk(state: AgentState) -> Literal["greeting", "auth_gate"]:
    """
    Determines if message is small talk that doesn't require authentication.
    
    ASSESSMENT REQUIREMENT: Identity verification only when needed for relevant actions.
    This prevents premature auth requests for greetings like "Hello" or "Who are you?".
    
    Args:
        state: Current agent state with message history and metadata
        
    Returns:
        "greeting" - Route to greeting handler (no auth needed)
        "auth_gate" - Route to normal flow (may need auth)
        
    Flow Impact:
        greeting → END (conversation completes)
        auth_gate → check if flow needs authentication
    """
    metadata = state.get("metadata", {})
    # intent_router sets "small_talk" metadata flag if detected
    if metadata.get("small_talk"):
        return "greeting"
    return "auth_gate"


def should_request_auth(state: AgentState) -> Literal["request_auth", "route_by_intent", "end"]:
    """
    Determines if authentication is required before proceeding.
    
    SECURITY DESIGN:
    - Only sensitive flows (card_issues, account_servicing) require auth
    - Non-sensitive flows (account opening, digital support) proceed without auth
    - Failed/locked auth immediately ends conversation
    
    Args:
        state: Current agent state
        
    Returns:
        "request_auth" - Not authenticated and needs auth
        "route_by_intent" - Already authenticated OR flow doesn't need auth
        "end" - Auth is locked (too many failed attempts)
        
    State Checks:
        - state["verified"]: Boolean, True if successfully authenticated
        - state["current_flow"]: String, the classified intent
        - metadata["auth"]["locked"]: Boolean, True if too many failed attempts
        - metadata["auth"]["attempted"]: Boolean, True if auth was just tried
    """
    auth = state.get("metadata", {}).get("auth", {})
    
    # If account is locked or auth just failed, end conversation
    if auth.get("locked") or (auth.get("attempted") and auth.get("success") is False):
        return "end"
    
    # Only card_issues and account_servicing require authentication
    # This aligns with ASSESSMENT REQUIREMENT: minimal friction for non-sensitive queries
    sensitive = state.get("current_flow") in ["card_issues", "account_servicing"]
    if not sensitive:
        return "route_by_intent"
    
    # Sensitive flow: check if already verified
    return "route_by_intent" if state.get("verified", False) else "request_auth"


def route_to_flow(state: AgentState) -> str:
    """
    Routes authenticated/authorized requests to appropriate flow handler.
    
    6 BANKING FLOWS (from assessment requirements):
    1. card_issues - Lost/stolen cards, declined payments, ATM issues
    2. account_servicing - Balance, statements, profile updates
    3. account_opening - New account onboarding
    4. digital_support - Login issues, OTP, app crashes
    5. transfers - Money transfers, bill pay, beneficiaries
    6. account_closure - Account closing, retention
    
    Args:
        state: Current agent state
        
    Returns:
        Node name corresponding to flow handler
        
    Implementation:
        - Flows 1-2: Full implementations (card_flow, account_flow)
        - Flows 3-6: Stub implementations (stub_flow)
    """
    current_flow = state.get("current_flow")

    if current_flow == "card_issues":
        return "card_flow"
    elif current_flow == "account_servicing":
        return "account_flow"
    elif current_flow in ["account_opening", "digital_support", "transfers", "account_closure"]:
        return "stub_flow"
    else:
        # Fallback for unknown/unclassified intents
        return "stub_flow"


def should_confirm(state: AgentState) -> Literal["confirm", "execute"]:
    """
    Determines if pending action requires explicit user confirmation.
    
    HIGH-RISK ACTIONS REQUIRING CONFIRMATION:
    - block_card: Permanent, cannot be undone
    - close_account: Permanent, cannot be undone
    
   CONFIRMATION FLOW:
    1. Flow node sets pending_action and asked_for_confirmation=True
    2. This turn: Return "execute" (don't confirm yet, just asked)
    3. Next turn: User responds, awaiting_confirmation=True
    4. This function returns "confirm" to process user's yes/no
    
    Args:
        state: Current agent state
        
    Returns:
        "confirm" - Route to confirmation handler to process yes/no
        "execute" - Skip confirmation (not needed or already asked)
        
    State Flags:
        - pending_action: Dict with action details
        - asked_for_confirmation: Just asked this turn
        - awaiting_confirmation: Awaiting response from previous ask
    """
    pending = state.get("pending_action")

    # Only these action types require confirmation
    if pending and pending.get("type") in ["block_card", "close_account"]:
        meta = state.get("metadata", {})
        
        # If we JUST asked for confirmation this turn, end now (don't confirm yet)
        if meta.get("asked_for_confirmation"):
            return "execute"
        
        # If we're AWAITING confirmation from prior turn, process it now
        if meta.get("awaiting_confirmation"):
            return "confirm"

    return "execute"


def should_escalate(state: AgentState) -> Literal["escalate", "continue"]:
    """
    Checks if conversation should escalate to human agent.
    
    ESCALATION TRIGGERS:
    - User explicitly requests human agent
    - Complex issue outside agent capabilities
    - Sensitive complaint or dispute
    
    Args:
        state: Current agent state
        
    Returns:
        "escalate" - Route to human escalation
        "continue" - Continue with AI agent
        
    Note: Currently only triggered by explicit user request or flow logic.
    Future: Could add sentiment analysis for frustrated users.
    """
    return "escalate" if state.get("requires_human", False) else "continue"


# =============================================================================
# DUMMY NODE FOR ROUTING
# 
# LangGraph requires conditional edge destinations to be NODE NAMES.
# This dummy node enables routing without processing.
# =============================================================================

async def route_by_intent(state: AgentState) -> AgentState:
    """
    Passthrough node for routing decisions.
    
    PURPOSE:
    LangGraph's conditional edges must point to node names, not functions.
    This node acts as a junction point where route_to_flow() decides the path.
    
    WHY NEEDED:
    - Can't use conditional edges directly from auth_gate to flow nodes
    - Need intermediate node for clean routing logic separation
    
    Args:
        state: Current agent state (unchanged)
        
    Returns:
        Same state (no processing)
        
    Flow:
        auth_gate → route_by_intent → [card_flow|account_flow|stub_flow]
    """
    return state


# =============================================================================
# BUILD LANGGRAPH WORKFLOW
# 
# Assembles all nodes and edges into compiled StateGraph.
# =============================================================================

def build_agent_graph() -> StateGraph:
    """
    Constructs the complete LangGraph workflow.
    
    GRAPH STRUCTURE:
    1. Add all nodes (functions that process state)
    2. Set entry point (first node when graph starts)
    3. Add edges (connections between nodes)
       - Simple edges: Always go to next node
       - Conditional edges: Use function to decide next node
    4. Compile graph into executable workflow
    
    Returns:
        Compiled StateGraph ready for execution
        
    Usage:
        state = create_initial_state(session_id)
        result = await agent_graph.ainvoke(state, config)
    """

    # Initialize graph with AgentState schema
    workflow = StateGraph(AgentState)

    # =========================================================================
    # ADD NODES - Each node is a function that processes state
    # =========================================================================
    workflow.add_node("intent_router", route_intent)      # Classify user intent
    workflow.add_node("greeting", handle_greeting)         # Handle small talk
    workflow.add_node("auth_gate", check_authentication)   # Check if auth needed
    workflow.add_node("request_auth", request_verification) # Request credentials
    workflow.add_node("route_by_intent", route_by_intent)  # Dummy router
    workflow.add_node("card_flow", handle_card_flow)       # Card issues flow
    workflow.add_node("account_flow", handle_account_flow) # Account flow
    workflow.add_node("stub_flow", handle_stub_flow)       # Stub flows 3-6
    workflow.add_node("confirmation", handle_confirmation)  # Handle yes/no confirmation
    workflow.add_node("escalation", escalate_to_human)     # Escalate to human

    # =========================================================================
    # SET ENTRY POINT - First node when conversation starts
    # =========================================================================
    workflow.set_entry_point("intent_router")

    # =========================================================================
    # ADD EDGES - Define conversation flow paths
    # =========================================================================
    
    # From intent_router: Check if small talk FIRST (avoids premature auth)
    workflow.add_conditional_edges(
        "intent_router",
        should_handle_small_talk,  # Function that returns "greeting" or "auth_gate"
        {
            "greeting": "greeting",      # Small talk → greeting handler
            "auth_gate": "auth_gate"     # Banking intent → auth check
        }
    )
    
    # Greeting completes conversation (no further processing needed)
    workflow.add_edge("greeting", END)

    # From auth_gate: Determine if authentication required
    workflow.add_conditional_edges(
        "auth_gate",
        should_request_auth,  # Returns "request_auth", "route_by_intent", or "end"
        {
            "request_auth": "request_auth",       # Need auth → request credentials
            "route_by_intent": "route_by_intent", # Verified OR non-sensitive → route to flow
            "end": END                             # Locked/failed auth → end
        }
    )

    # After requesting auth, end conversation (user will provide credentials next turn)
    workflow.add_edge("request_auth", END)

    # From route_by_intent: Route to appropriate flow handler
    workflow.add_conditional_edges(
        "route_by_intent",
        route_to_flow,  # Returns flow node name based on current_flow
        {
            "card_flow": "card_flow",
            "account_flow": "account_flow",
            "stub_flow": "stub_flow",
            "escalation": "escalation"
        }
    )

    # From card_flow: Check if high-risk action needs confirmation
    workflow.add_conditional_edges(
        "card_flow",
        should_confirm,  # Returns "confirm" or "execute"
        {
            "confirm": "confirmation",  # High-risk action → get confirmation
            "execute": END              # Normal action or already confirmed → end
        }
    )

    # All other flows end conversation after processing
    workflow.add_edge("account_flow", END)
    workflow.add_edge("stub_flow", END)
    workflow.add_edge("confirmation", END)
    workflow.add_edge("escalation", END)

    # =========================================================================
    # COMPILE AND RETURN
    # =========================================================================
    # Compiling converts the graph definition into an executable workflow
    return workflow.compile()


# Create global agent graph instance (used by vapi_routes.py)
agent_graph = build_agent_graph()
