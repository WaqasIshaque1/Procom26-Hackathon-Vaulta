"""
Deep Logic Flow: Account Servicing (Flow 2)

Handles:
- Balance inquiries → get_account_balance()
- Transaction history → get_recent_transactions()
- Statements → request_statement()
- Profile updates → escalate to human
"""

from langchain_core.messages import AIMessage
from app.agents.state import AgentState
from app.core.exceptions import VerificationRequiredError
from app.services.session_manager import session_manager
from app.services.banking_api import (
    get_account_balance,
    get_recent_transactions,
    request_statement,
    get_loan_info,
    get_card_details,
    list_customer_cards,
    submit_feedback,
    request_cheque_book,
    report_fraud,
    toggle_international_transactions
)


async def handle_account_flow(state: AgentState) -> AgentState:
    """
    Main handler for account servicing.
    
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
                "I'd be happy to help you check your account information. "
                "For your security, I'll need to verify your identity first. "
                "Could you please provide your Customer ID and your 4-digit PIN?"
            )
        
        response = AIMessage(content=prompt)
        return {**state, "messages": [response]}
    
    session = session_manager.get_session(state.get("session_id"))
    customer_id = session.customer_id if session else None
    if not customer_id:
        response = AIMessage(content=(
            "I'm having trouble verifying your account details. "
            "I'll connect you with a specialist to complete this securely."
        ))
        return {**state, "messages": [response], "requires_human": True}
    
    # Analyze user intent
    user_messages = [msg for msg in state["messages"] if msg.type == "human"]
    latest_input = user_messages[-1].content.lower() if user_messages else ""
    
    # CRITICAL: Fraud reporting has highest priority
    if any(kw in latest_input for kw in ["fraud", "unauthorized", "stolen", "suspicious transaction", "didn't make"]):
        return await handle_fraud_report(state, customer_id)
    
    elif any(kw in latest_input for kw in ["cheque", "checkbook", "check book", "chequebook"]):
        return await handle_cheque_book_request(state, customer_id)
    
    elif any(kw in latest_input for kw in ["international", "overseas", "abroad", "travel"]):
        # Determine if enabling or disabling
        enable = any(kw in latest_input for kw in ["enable", "turn on", "activate", "allow"])
        disable = any(kw in latest_input for kw in ["disable", "turn off", "deactivate", "block"])
        
        if enable or disable:
            return await handle_intl_transactions(state, customer_id, enable)
        else:
            # Ask for clarification
            response = AIMessage(content=(
                "Would you like to enable or disable international transactions on your account?"
            ))
            return {**state, "messages": [response]}
    
    elif any(kw in latest_input for kw in ["balance", "how much", "money"]):
        return await handle_balance_inquiry(state, customer_id)
    
    elif any(kw in latest_input for kw in ["transaction", "history", "recent"]):
        return await handle_transaction_history(state, customer_id)
    
    elif "statement" in latest_input:
        return await handle_statement_request(state, customer_id)
    
    elif any(kw in latest_input for kw in ["loan", "mortgage", "borrow"]):
        return await handle_loan_inquiry(state,customer_id)
    
    elif any(kw in latest_input for kw in ["reward", "points"]):
        return await handle_rewards_inquiry(state, customer_id)
    
    elif any(kw in latest_input for kw in ["card", "cards", "credit card"]) and "block" not in latest_input:
        return await handle_card_inquiry(state, customer_id)
    
    elif any(kw in latest_input for kw in ["feedback", "complaint", "complain", "praise", "suggest"]):
        return await handle_feedback_submission(state, customer_id, latest_input)
    
    elif any(kw in latest_input for kw in ["update", "change", "address"]):
        return await handle_profile_update(state)
    
    else:
        response = AIMessage(content=(
            "I can help you with:\n"
            "• Check account balance\n"
            "• View recent transactions\n"
            "• Request statements\n"
            "• Check loan information\n"
            "• View card details and rewards\n"
            "• Submit feedback\n"
            "• Update profile information\n\n"
            "What would you like to do?"
        ))
        return {**state, "messages": [response]}


async def handle_balance_inquiry(state: AgentState, customer_id: str) -> AgentState:
    """Retrieve and present account balance."""
    
    balance_data = await get_account_balance(customer_id)
    
    if "error" in balance_data:
        response = AIMessage(content="I'm having trouble retrieving your balance. Please try again.")
    else:
        balance = balance_data["balance"]
        account_type = balance_data["account_type"]
        
        response = AIMessage(content=(
            f"Your {account_type.lower()} balance is ${balance:,.2f}. "
            f"Would you like to see recent transactions as well?"
        ))
    
    return {**state, "messages": [response]}


async def handle_transaction_history(state: AgentState, customer_id: str) -> AgentState:
    """Retrieve and narrate transactions."""
    
    transactions = await get_recent_transactions(customer_id, count=3)
    
    if not transactions:
        response = AIMessage(content="You don't have any recent transactions.")
        return {**state, "messages": [response]}
    
    # Format for voice
    txn_list = []
    for txn in transactions:
        amount = txn["amount"]
        desc = txn["description"]
        date = txn["date"]
        
        if amount < 0:
            txn_list.append(f"• {date}: Spent ${abs(amount):.2f} at {desc}")
        else:
            txn_list.append(f"• {date}: Received ${amount:.2f} from {desc}")
    
    response = AIMessage(content=(
        "Here are your last 3 transactions:\n\n" + "\n".join(txn_list) +
        "\n\nWould you like to see more?"
    ))
    
    return {**state, "messages": [response]}


async def handle_statement_request(state: AgentState, customer_id: str) -> AgentState:
    """Process statement request."""
    
    result = await request_statement(customer_id, "monthly")
    
    if result.get("success"):
        response = AIMessage(content=(
            f"Perfect! Your monthly statement will be emailed to {result['email']} "
            f"within 24 hours. Reference: {result['reference']}"
        ))
    else:
        response = AIMessage(content=(
            "I'm having trouble processing your statement request. "
            "Let me transfer you to someone who can help."
        ))
        state["requires_human"] = True
    
    return {**state, "messages": [response]}


async def handle_profile_update(state: AgentState) -> AgentState:
    """Handle profile updates - requires human."""
    
    response = AIMessage(content=(
        "For security, profile updates require verification by a representative. "
        "I'll transfer you now. They can update your information safely."
    ))
    
    state["requires_human"] = True
    
    return {**state, "messages": [response]}


async def handle_loan_inquiry(state: AgentState, customer_id: str) -> AgentState:
    """Retrieve and present loan information."""
    
    loans = await get_loan_info(customer_id)
    
    if not loans:
        response = AIMessage(content="You don't have any active loans on file.")
        return {**state, "messages": [response]}
    
    # Format loan info for voice
    loan_list = []
    for loan in loans:
        loan_type = loan["loan_type"]
        amount = loan["loan_amount"]
        rate = loan["interest_rate"]
        status = loan["loan_status"]
        term = loan["loan_term"]
        
        loan_list.append(
            f"• {loan_type} Loan: ${amount:,.2f} at {rate}% interest, "
            f"{term} month term, Status: {status}"
        )
    
    response = AIMessage(content=(
        "Here's your loan information:\n\n" + "\n".join(loan_list) +
        "\n\nWould you like more details about any specific loan?"
    ))
    
    return {**state, "messages": [response]}


async def handle_rewards_inquiry(state: AgentState, customer_id: str) -> AgentState:
    """Show rewards points for credit cards."""
    
    # Get first credit card with rewards
    card = await get_card_details(customer_id)
    
    if "error" in card:
        response = AIMessage(content="I'm having trouble retrieving your card information.")
        return {**state, "messages": [response]}
    
    rewards = card.get("rewards_points", 0)
    card_type = card.get("type", "Card")
    last4 = card.get("last4", "****")
    
    if rewards == 0:
        response = AIMessage(content=f"Your {card_type} card ending in {last4} currently has no rewards points.")
    else:
        # Estimate cash value (typical: 1 point = 1 cent)
        cash_value = rewards / 100
        response = AIMessage(content=(
            f"Your {card_type} card ending in {last4} has {rewards:,} rewards points! "
            f"That's approximately ${cash_value:.2f} in rewards value. "
            f"Would you like to know about redeeming these points?"
        ))
    
    return {**state, "messages": [response]}


async def handle_card_inquiry(state: AgentState, customer_id: str) -> AgentState:
    """List all customer cards with details."""
    
    cards = await list_customer_cards(customer_id)
    
    if not cards:
        response = AIMessage(content="You don't have any cards on file.")
        return {**state, "messages": [response]}
    
    # Format card list
    card_list = []
    for card in cards:
        card_type = card["type"]
        last4 = card["last4"]
        status = card["status"]
        
        card_list.append(f"• {card_type} card ending in {last4} ({status})")
    
    response = AIMessage(content=(
        f"You have {len(cards)} card(s) on file:\n\n" + "\n".join(card_list) +
        "\n\nWould you like details about any specific card?"
    ))
    
    return {**state, "messages": [response]}


async def handle_feedback_submission(state: AgentState, customer_id: str, user_input: str) -> AgentState:
    """Process feedback submission."""
    
    # Determine feedback type from input
    if any(kw in user_input for kw in ["complaint", "complain", "issue", "problem"]):
        feedback_type = "Complaint"
    elif any(kw in user_input for kw in ["praise", "thank", "great", "excellent"]):
        feedback_type = "Praise"
    else:
        feedback_type = "Suggestion"
    
    result = await submit_feedback(customer_id, feedback_type, "")
    
    if result.get("success"):
        response = AIMessage(content=(
            f"Thank you for your {feedback_type.lower()}! {result['message']}"
        ))
    else:
        response = AIMessage(content=(
            "I'm having trouble submitting your feedback right now. "
            "Please try again or let me connect you with a representative."
        ))
    
    return {**state, "messages": [response]}


# =============================================================================
# SECURITY FEATURE HANDLERS
# =============================================================================

async def handle_cheque_book_request(state: AgentState, customer_id: str) -> AgentState:
    """Process cheque book request."""
    
    result = await request_cheque_book(customer_id)
    
    if result.get("success"):
        response = AIMessage(content=result["message"])
    else:
        response = AIMessage(content=(
            "I'm having trouble processing your cheque book request. "
            "Let me connect you with a representative who can help."
        ))
        state["requires_human"] = True
    
    return {**state, "messages": [response]}


async def handle_fraud_report(state: AgentState, customer_id: str) -> AgentState:
    """
    CRITICAL: Report fraud and freeze account immediately.
    ALWAYS escalates to human.
    """
    
    result = await report_fraud(customer_id, "Unauthorized transaction reported via voice")
    
    # CRITICAL: Set human escalation flag
    state["requires_human"] = True
    
    response = AIMessage(content=result["message"])
    
    return {**state, "messages": [response], "requires_human": True}


async def handle_intl_transactions(state: AgentState, customer_id: str, enable: bool) -> AgentState:
    """Toggle international transactions on/off."""
    
    result = await toggle_international_transactions(customer_id, enable)
    
    if result.get("success"):
        response = AIMessage(content=result["message"])
    else:
        response = AIMessage(content=(
            "I'm having trouble updating your international transaction settings. "
            "Please try again or let me connect you with a representative."
        ))
    
    return {**state, "messages": [response]}
