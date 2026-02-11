"""
Intent Classification & Routing Node

Analyzes user input and routes to one of 6 banking flows.
"""

import re
from langchain_core.messages import AIMessage, SystemMessage
from app.agents.state import AgentState
from app.agents.prompts import INTENT_CLASSIFICATION_PROMPT
from app.core.llm_factory import llm


async def route_intent(state: AgentState) -> AgentState:
    """
    Classify user intent and set current_flow.
    
    Uses LLM to determine which of 6 banking flows applies.
    """
    
    # Get latest user message
    user_messages = [msg for msg in state["messages"] if msg.type == "human"]
    
    if not user_messages:
        # No user input yet
        return state
    
    latest_input = user_messages[-1].content.lower().strip()

    # Quick small-talk detection (only when message isn't about a banking intent)
    intent_keywords = [
        "card", "atm", "lost", "stolen", "declined", "cash not dispensed",
        "balance", "statement", "transaction", "profile", "address", "recent",
        "open account", "new account", "onboard",
        "login", "otp", "app", "device", "crash",
        "transfer", "bill pay", "beneficiary", "wire", "ach",
        "close account", "closure", "retain",
    ]
    has_intent_keywords = any(kw in latest_input for kw in intent_keywords)
    has_digits = bool(re.search(r'\d', latest_input))
    if not has_intent_keywords and not has_digits:
        if re.search(r'\b(hi|hello|hey|good morning|good afternoon|good evening)\b', latest_input):
            return {
                **state,
                "current_flow": None,
                "metadata": {**state.get("metadata", {}), "small_talk": "greeting"},
            }
        if re.search(r'\b(thank you|thanks|thx|appreciate)\b', latest_input):
            return {
                **state,
                "current_flow": None,
                "metadata": {**state.get("metadata", {}), "small_talk": "thanks"},
            }
        if re.search(r'\b(bye|goodbye|see you|later)\b', latest_input):
            return {
                **state,
                "current_flow": None,
                "metadata": {**state.get("metadata", {}), "small_talk": "goodbye"},
            }
        if re.search(r'\b(what can you do|help|services|capabilities)\b', latest_input):
            return {
                **state,
                "current_flow": None,
                "metadata": {**state.get("metadata", {}), "small_talk": "help"},
            }
        # Identity questions - "Who are you?", "What are you?", "What AI model?"
        if re.search(r'\b(who are you|what are you|who made you|what (ai )?model)\b', latest_input):
            return {
                **state,
                "current_flow": None,
                "metadata": {**state.get("metadata", {}), "small_talk": "identity"},
            }

    # If we are in a locked flow (e.g., awaiting confirmation), skip rerouting.
    meta = state.get("metadata", {})
    current_flow = state.get("current_flow")
    
    # NEW: Flow locking - if already in a flow, maintain it unless user explicitly changes topic
    if current_flow and not meta.get("force_reroute"):
        # Check if user is explicitly changing topic
        topic_change_keywords = [
            "actually", "instead", "never mind", "wait", "hold on",
            "let me", "i want to", "can you help me with something else",
            "different", "something else"
        ]
        
        is_topic_change = any(kw in latest_input for kw in topic_change_keywords)
        
        if not is_topic_change:
            # User is continuing current conversation - don't re-route
            return state
    
    if meta.get("lock_flow") or (meta.get("auth", {}).get("attempted") and current_flow):
        return state
    
    # Fast keyword routing first (avoids LLM latency where possible)
    if any(kw in latest_input for kw in ["card", "atm", "lost", "stolen", "declined", "cash not dispensed"]):
        flow = "card_issues"
    elif any(kw in latest_input for kw in ["balance", "statement", "transaction", "profile", "address", "recent"]):
        flow = "account_servicing"
    elif any(kw in latest_input for kw in ["open account", "new account", "onboard"]):
        flow = "account_opening"
    elif any(kw in latest_input for kw in ["login", "otp", "app", "device", "crash"]):
        flow = "digital_support"
    elif any(kw in latest_input for kw in ["transfer", "bill pay", "beneficiary", "wire", "ach"]):
        flow = "transfers"
    elif any(kw in latest_input for kw in ["close account", "closure", "retain"]):
        flow = "account_closure"
    else:
        # Build classification prompt (LLM fallback)
        classification_messages = [
            SystemMessage(content=INTENT_CLASSIFICATION_PROMPT),
            user_messages[-1]
        ]
        
        # Get LLM classification
        response = await llm.ainvoke(classification_messages)
        
        # Parse response to extract flow
        response_text = response.content.lower()
        
        if "card_issues" in response_text:
            flow = "card_issues"
        elif "account_servicing" in response_text:
            flow = "account_servicing"
        elif "account_opening" in response_text:
            flow = "account_opening"
        elif "digital_support" in response_text:
            flow = "digital_support"
        elif "transfers" in response_text:
            flow = "transfers"
        elif "account_closure" in response_text:
            flow = "account_closure"
        else:
            flow = None
    
    return {
        **state,
        "current_flow": flow
    }
