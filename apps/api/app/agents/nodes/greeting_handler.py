"""
Greeting & Identity Handler Node

Handles small talk, identity questions, and capabilities without requiring authentication.
"""

from langchain_core.messages import AIMessage
from app.agents.state import AgentState


AGENT_IDENTITY = {
    "name": "Alex",
    "role": "Vaulta Voice Assistant",
    "capabilities": [
        "Account inquiries (balance, transactions)",
        "Card services (lost/stolen cards, declined payments)",
        "Statement requests",
        "General banking help and routing"
    ]
}


async def handle_greeting(state: AgentState) -> AgentState:
    """
    Handle greeting and identity questions without authentication.
    
    This runs when user asks:
    - "Who are you?" / "What are you?"
    - "What can you do?" / "Help"
    - "Hi" / "Hello" / "Hey"
    """
    
    # Get the small_talk type from metadata
    metadata = state.get("metadata", {})
    small_talk_type = metadata.get("small_talk")
    
    if small_talk_type == "greeting":
        response_text = (
            "Hi! How can I help you today?"
        )
    
    elif small_talk_type == "thanks":
        response_text = (
            "You're welcome! Is there anything else I can help with?"
        )
    
    elif small_talk_type == "goodbye":
        response_text = (
            "Thank you for banking with Vaulta. Have a great day!"
        )
    
    elif small_talk_type == "help":
        response_text = (
            f"I'm {AGENT_IDENTITY['name']}, {AGENT_IDENTITY['role']}. "
            "I can help you with:\n\n"
            "• Check account balance\n"
            "• View recent transactions\n"
            "• Request statements\n"
            "• Report lost or stolen cards\n"
            "• Card declined issues\n"
            "• General banking support\n\n"
            "What would you like to do?"
        )
    
    elif small_talk_type == "identity":
        response_text = (
            f"I'm {AGENT_IDENTITY['name']}, {AGENT_IDENTITY['role']}. "
            "I'm designed specifically to help Vaulta customers with their "
            "banking needs, using advanced AI technology. I can help you with "
            "account inquiries, card services, and general banking questions. "
            "How may I assist you today?"
        )
    
    else:
        # Fallback for unknown small talk
        response_text = (
            "I'm here to help with your banking needs. "
            "What can I assist you with today?"
        )
    
    response = AIMessage(content=response_text)
    
    return {
        **state,
        "messages": [response]
    }
