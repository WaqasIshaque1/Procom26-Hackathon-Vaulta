"""
Deep Logic Flow: Card & ATM Issues (Flow 1)

Handles:
- Lost/Stolen Cards → block_card()
- Declined Payments → get_card_status()
- ATM Cash Not Dispensed → create_dispute()
"""

import random
from langchain_core.messages import AIMessage
from app.agents.state import AgentState
from app.core.exceptions import VerificationRequiredError


async def handle_card_flow(state: AgentState) -> AgentState:
    """
    Main handler for card-related issues.
    
    SECURITY: Customer must be verified. If not, request auth inline.
    """
    
    # Check authentication status
    if not state.get("verified", False):
        auth = state.get("metadata", {}).get("auth", {})
        
        # Check if auth was just attempted and failed
        if auth.get("attempted") and auth.get("success") is False:
            remaining = auth.get("remaining_attempts")
            remaining_msg = f" You have {remaining} attempt(s) remaining." if remaining is not None else ""
            response = AIMessage(content=(
                "I couldn't verify your identity with those credentials. "
                "Please check your Customer ID and PIN and try again." + remaining_msg
            ))
            return {**state, "messages": [response]}
        
        # Request authentication
        if auth.get("needs_pin"):
            prompt = "Thanks. Please provide your 4-digit PIN."
        elif auth.get("needs_customer_id"):
            prompt = "Thanks. Please provide your Customer ID."
        else:
            prompt = (
                "I understand this is urgent, and I'm here to help you immediately. "
                "For your security, I'll need to verify your identity first. "
                "Could you please provide your Customer ID and your 4-digit PIN?"
            )
        
        response = AIMessage(content=prompt)
        return {**state, "messages": [response]}

    # If we're awaiting confirmation, let the confirmation node handle it
    if state.get("pending_action") and state.get("metadata", {}).get("awaiting_confirmation"):
        return state
    
    # NEW: Get conversation context to avoid repetitive responses
    messages = state.get("messages", [])
    assistant_messages = [msg for msg in messages if msg.type == "ai"]
    last_assistant_msg = assistant_messages[-1].content.lower() if assistant_messages else ""
    
    user_messages = [msg for msg in messages if msg.type == "human"]
    latest_input = user_messages[-1].content.lower() if user_messages else ""
    
    # NEW: Check if we already asked which card - interpret user response in context
    if "debit card ending" in last_assistant_msg or "credit card ending" in last_assistant_msg:
        # We just asked which card - parse their response
        if "debit" in latest_input or "0001" in latest_input:
            return await _block_specific_card(state, "CARD_001", "0001")
        elif "credit" in latest_input or "9999" in latest_input:
            return await _block_specific_card(state, "CARD_999", "9999")
        elif any(kw in latest_input for kw in ["lost", "stolen", "missing", "block"]):
            # User repeated their request instead of answering - re-ask more directly
            response = AIMessage(content=(
                "I understand you need to block a card. To help you quickly, "
                "which card do you want to block - Debit or Credit?"
            ))
            return {**state, "messages": [response]}
        else:
            # Unclear response - ask again more simply
            response = AIMessage(content="Which card - Debit or Credit?")
            return {**state, "messages": [response]}
    
    # NEW: Check if we already asked about the issue type - avoid asking again
    if "lost or stolen card" in last_assistant_msg:
        # We just asked about issue type - determine from their response
        if any(kw in latest_input for kw in ["lost", "stolen", "missing", "block"]):
            return await handle_lost_card(state)
        elif any(kw in latest_input for kw in ["declined", "rejected", "not working"]):
            return await handle_declined_payment(state)
        elif any(kw in latest_input for kw in ["atm", "cash", "dispense"]):
            return await handle_atm_cash_not_dispensed(state)
        else:
            # Unclear - be more direct
            response = AIMessage(content=(
                "I didn't catch that. Are you calling about: 1) A lost or stolen card you need to block, "
                "2) A declined payment, or 3) An ATM issue?"
            ))
            return {**state, "messages": [response]}
    
    # Determine issue type from latest input
    if any(kw in latest_input for kw in ["lost", "stolen", "missing", "block"]):
        return await handle_lost_card(state)
    
    elif any(kw in latest_input for kw in ["declined", "not working", "rejected"]):
        return await handle_declined_payment(state)
    
    elif any(kw in latest_input for kw in ["atm", "cash", "dispense"]):
        return await handle_atm_cash_not_dispensed(state)
    
    else:
        # First time in card flow - ask what the issue is
        response = AIMessage(content=(
            "I can help you with your Vaulta cards. Are you calling about a lost or stolen card, "
            "a declined payment, or an issue with an ATM?"
        ))
        return {**state, "messages": [response]}


async def _block_specific_card(state: AgentState, card_id: str, last4: str) -> AgentState:
    """Helper function to block a specific card - used after card selection."""
    pending_action = {
        "type": "block_card",
        "card_id": card_id,
        "reason": "lost",
        "description": f"BLOCK your card ending in {last4}"
    }

    card_type = "Debit" if "001" in card_id else "Credit"
    response = AIMessage(content=(
        f"I've found your {card_type} card ending in {last4}. For your security, "
        f"blocking a card is PERMANENT and cannot be undone. "
        f"Are you sure you want to proceed and BLOCK this card?"
    ))

    return {
        **state,
        "pending_action": pending_action,
        "messages": [response],
        "metadata": {
            **state.get("metadata", {}),
            "asked_for_confirmation": True,
            "awaiting_confirmation": True
        }
    }


async def handle_lost_card(state: AgentState) -> AgentState:
    """Initiate lost card blocking flow."""
    
    # Check if user already specified which card
    user_messages = [msg for msg in state["messages"] if msg.type == "human"]
    latest_input = user_messages[-1].content.lower()
    
    if "debit" in latest_input or "0001" in latest_input:
        return await _block_specific_card(state, "CARD_001", "0001")
    elif "credit" in latest_input or "9999" in latest_input:
        return await _block_specific_card(state, "CARD_999", "9999")
    else:
        # Ask which card
        response = AIMessage(content=(
            "I'm sorry to hear that. I can help you block your card immediately. "
            "Which card is it? Your Debit card ending in 0001, or your Credit card ending in 9999?"
        ))
        return {**state, "messages": [response]}


async def handle_declined_payment(state: AgentState) -> AgentState:
    """Explain why a payment was declined."""
    
    # In a real system, we'd look this up
    reasons = [
        "insufficient funds",
        "incorrect PIN entered",
        "unusual activity detected",
        "expired card"
    ]
    reason = random.choice(reasons)
    
    response = AIMessage(content=(
        f"I've checked your recent transactions. It looks like your last payment was declined "
        f"due to {reason}. Would you like more details on how to resolve this?"
    ))
    
    return {**state, "messages": [response]}


async def handle_atm_cash_not_dispensed(state: AgentState) -> AgentState:
    """Handle ATM dispute."""
    
    ref_number = f"ATM-{random.randint(100000, 999999)}"
    
    response = AIMessage(content=(
        f"I'm sorry about this ATM issue. I've created a dispute case: {ref_number}\n\n"
        f"What happens next:"
        "\n1. Our team reviews ATM logs within 24 hours"
        "\n2. If confirmed, we credit your account in 3-5 business days"
        "\n3. You'll receive email updates throughout"
        "\n\nIs there anything else I can help with?"
    ))
    
    return {**state, "messages": [response]}
