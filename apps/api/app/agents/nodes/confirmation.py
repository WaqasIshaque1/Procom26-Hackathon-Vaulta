"""
Confirmation Node for Critical Actions
"""

from langchain_core.messages import AIMessage
from app.agents.state import AgentState
from app.services.banking_api import block_card
from app.core.exceptions import VerificationRequiredError


async def handle_confirmation(state: AgentState) -> AgentState:
    """
    Handle user confirmation for pending actions.
    
    Checks if user confirmed (yes/proceed) or declined (no/cancel).
    """
    
    pending = state.get("pending_action")

    if not pending:
        return state

    if not state.get("verified", False):
        raise VerificationRequiredError("Confirmation requires verification")
    
    # Check user's response
    user_messages = [msg for msg in state["messages"] if msg.type == "human"]
    latest_input = user_messages[-1].content.lower() if user_messages else ""
    
    if any(word in latest_input for word in ["yes", "confirm", "proceed", "sure"]):
        # Execute action
        if pending["type"] == "block_card":
            result = await block_card(pending["card_id"], pending["reason"])
            response = AIMessage(content=result)
        else:
            response = AIMessage(content="Action completed successfully.")
        
        return {
            **state,
            "pending_action": None,
            "messages": [response],
            "metadata": {
                **state.get("metadata", {}),
                "awaiting_confirmation": False,
                "asked_for_confirmation": False
            }
        }
    
    elif any(word in latest_input for word in ["no", "cancel", "stop", "wait"]):
        # User cancelled
        response = AIMessage(content=(
            f"Okay, I've cancelled the {pending['description']}. "
            f"Your card remains active. Is there anything else I can help with?"
        ))
        
        return {
            **state,
            "pending_action": None,
            "messages": [response],
            "metadata": {
                **state.get("metadata", {}),
                "awaiting_confirmation": False,
                "asked_for_confirmation": False
            }
        }
    
    else:
        # Unclear response - ask again
        response = AIMessage(content=(
            f"I need a clear confirmation. Do you want to {pending['description']}? "
            f"Please say YES to proceed or NO to cancel."
        ))
        
        return {
            **state,
            "messages": [response],
            "metadata": {
                **state.get("metadata", {}),
                "awaiting_confirmation": True,
                "asked_for_confirmation": False
            }
        }
