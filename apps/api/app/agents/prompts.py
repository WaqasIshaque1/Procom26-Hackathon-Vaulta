"""
System Prompts & Templates
"""

INTENT_CLASSIFICATION_PROMPT = """You are an intent classifier for Vaulta's voice assistant.

Analyze the user's message and classify it into one of these categories:

1. card_issues - Lost/stolen cards, declined payments, ATM problems
2. account_servicing - Balance inquiries, transactions, statements, profile updates
3. account_opening - New account applications, onboarding
4. digital_support - Mobile app issues, login problems, OTP
5. transfers - Money transfers, bill payments, beneficiaries
6. account_closure - Account closure requests, retention

Respond with ONLY the category name (e.g., "card_issues").

Examples:
User: "I lost my debit card" → card_issues
User: "What's my balance?" → account_servicing
User: "Can't login to the app" → digital_support
User: "I want to close my account" → account_closure
"""

STUB_FLOW_RESPONSES = {
    "account_opening": """Thank you for your interest in Vaulta!

To open a new account, you can:
1. Visit vaulta.com/apply
2. Schedule an appointment at a branch
3. Call our new accounts team at 1-800-VAULTA

Would you like me to send you the application link via SMS?""",
    
    "digital_support": """I can help with app issues!

Common solutions:
• Login problems: Reset password at vaulta.com/reset
• OTP not received: Check spam, request new code
• App crashes: Update to latest version

If these don't help, I'll transfer you to digital support.""",
    
    "transfers": """I can assist with transfers and payments.

Currently, I can route you to:
• Domestic Transfers (ACH/Wire)
• International Payments
• Bill Pay Support
• Beneficiary Management

Which area do you need help with?""",
    
    "account_closure": """We're sorry to hear you're considering closing your account.

To ensure this is handled correctly and to discuss alternatives that might better suit your needs, I'll need to connect you with our Account Specialist team.

Would you like to speak with them now?"""
}

# Fallback for unknown or general requests
GENERAL_HELP_RESPONSE = """I can help with account balances, recent transactions, statements, card issues, and general banking support.
If you have a specific request, just tell me and I'll take care of it."""

SMALL_TALK_RESPONSES = {
    "greeting": "Hi! How can I help you today?",
    "thanks": "You're welcome! Is there anything else I can help with?",
    "goodbye": "Thanks for calling Vaulta. Have a great day!",
    "help": "I can help with balances, transactions, statements, card issues, and general banking support. What would you like to do?"
}
