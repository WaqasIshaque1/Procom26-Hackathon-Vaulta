"""
Human Escalation Node
"""

from langchain_core.messages import AIMessage
from app.agents.state import AgentState


async def escalate_to_human(state: AgentState) -> AgentState:
    """
    Transfer conversation to human agent.
    """
    
    response = AIMessage(content=(
        "I'll connect you with a specialist who can better assist with your request. "
        "Please hold for a moment..."
    ))
    
    return {
        **state,
        "messages": [response],
        "requires_human": True
    }
