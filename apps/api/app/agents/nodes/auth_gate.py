"""
Authentication Gate Node

Enforces identity verification before accessing sensitive operations.
"""

from langchain_core.messages import AIMessage
from app.agents.state import AgentState


async def check_authentication(state: AgentState) -> AgentState:
    """
    Check if customer is authenticated.
    """
    
    # Already verified
    if state.get("verified", False):
        return state

        # # Check if user just provided credentials
        # user_messages = [msg for msg in state["messages"] if msg.type == "human"]
        #
        # if not user_messages:
        #     return state
        #
        # latest_input = user_messages[-1].content
        #
        # # Simple credential extraction
    # customer_id_match = re.search(r'\d{4}', latest_input)
        # pin_match = re.search(r'\b\d{4}\b', latest_input)
        #
        # if customer_id_match and pin_match:
        #     customer_id = customer_id_match.group()
        #     pin = pin_match.group()
        #
        #     # Verify identity
        #     is_verified = await verify_identity(customer_id, pin)
        #
        #     if is_verified:
        #         return {
        #             **state,
        #             "verified": True,
        #             "customer_id": customer_id
        #         }
        #     else:
        #         # Failed verification
        #         response = AIMessage(content=(
        #             "I couldn't verify your identity with those credentials. "
        #             "Please check your Customer ID and PIN and try again."
        #         ))
        #         return {**state, "messages": [response]}

    auth = state.get("metadata", {}).get("auth", {})

    # Locked out after too many attempts -> escalate
    if auth.get("locked"):
        response = AIMessage(content=(
            "For your security, I've locked verification after too many failed attempts. "
            "I'll connect you with a specialist to complete this safely."
        ))
        return {**state, "messages": [response], "requires_human": True}

    # If an auth attempt just occurred and failed, surface the error clearly
    if auth.get("attempted") and auth.get("success") is False:
        remaining = auth.get("remaining_attempts")
        remaining_msg = f" You have {remaining} attempt(s) remaining." if remaining is not None else ""
        response = AIMessage(content=(
            "I couldn't verify your identity with those credentials. "
            "Please check your Customer ID and PIN and try again." + remaining_msg
        ))
        return {**state, "messages": [response]}

    return state


async def request_verification(state: AgentState) -> AgentState:
    """
    Prompt user for identity verification.
    """

    auth = state.get("metadata", {}).get("auth", {})
    if auth.get("needs_pin"):
        prompt = "Thanks. Please provide your 4-digit PIN."
    elif auth.get("needs_customer_id"):
        prompt = "Thanks. Please provide your 4-digit Customer ID."
    else:
        prompt = (
            "For security, I need to verify your identity before we proceed. "
            "Please provide your Customer ID and your 4-digit PIN."
        )

    response = AIMessage(content=prompt)
    
    return {**state, "messages": [response]}
