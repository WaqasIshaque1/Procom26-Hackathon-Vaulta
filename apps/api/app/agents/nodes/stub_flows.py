"""
Stub Flow Handlers for Flows 3-6
"""

from langchain_core.messages import AIMessage
from app.agents.state import AgentState
from app.agents.prompts import STUB_FLOW_RESPONSES, GENERAL_HELP_RESPONSE, SMALL_TALK_RESPONSES


async def handle_stub_flow(state: AgentState) -> AgentState:
    """
    Route to stub response based on current_flow.
    """
    
    current_flow = state.get("current_flow")
    small_talk = state.get("metadata", {}).get("small_talk")

    if small_talk in SMALL_TALK_RESPONSES:
        response = AIMessage(content=SMALL_TALK_RESPONSES[small_talk])
        return {
            **state,
            "messages": [response],
            "metadata": {**state.get("metadata", {}), "small_talk": None}
        }
    response_text = STUB_FLOW_RESPONSES.get(current_flow, GENERAL_HELP_RESPONSE)
    
    response = AIMessage(content=response_text)
    
    return {**state, "messages": [response]}
