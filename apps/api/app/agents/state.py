"""
Agent State Definition

Defines the TypedDict structure for LangGraph state management.
"""

from typing import TypedDict, Annotated, List, Optional, Dict, Any
from langchain_core.messages import BaseMessage
import operator


class AgentState(TypedDict):
    """
    Complete state structure for the Vaulta agent.
    
    This state is passed between all nodes in the LangGraph workflow.
    Using Annotated[List, operator.add] allows the graph to append
    messages rather than replacing them.
    """
    
    # Conversation history
    messages: Annotated[List[BaseMessage], operator.add]
    
    # Authentication state
    customer_id: Optional[str]
    verified: bool
    
    # Flow routing
    current_flow: Optional[str]  # Which of the 6 flows we're in
    original_intent: Optional[str]  # NEW: Preserve intent through auth interruption
    
    # Pending confirmations
    pending_action: Optional[Dict[str, Any]]
    # Example: {"type": "block_card", "card_id": "CARD_001", "reason": "lost"}
    
    # Session management
    session_id: str
    
    # Human escalation flag
    requires_human: bool
    
    # Additional metadata
    metadata: Dict[str, Any]


def create_initial_state(session_id: str) -> AgentState:
    """
    Factory function to create initial agent state.
    
    Args:
        session_id: Unique identifier for this conversation
        
    Returns:
        Fresh AgentState with defaults
    """
    return {
        "messages": [],
        "customer_id": None,
        "verified": False,
        "current_flow": None,
        "original_intent": None,
        "pending_action": None,
        "session_id": session_id,
        "requires_human": False,
        "metadata": {}
    }
