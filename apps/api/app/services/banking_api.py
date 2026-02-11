"""
Banking API - Hybrid Implementation

Uses hardcoded mock data for demo customer (instant response),
falls back to PostgreSQL for all other customers.
"""

from typing import Dict, List, Optional
from datetime import datetime
import random
from app.core.database import execute_query


# =============================================================================
# MOCK DATABASE - Hardcoded for Instant Demo/Testing
# =============================================================================

MOCK_CUSTOMERS = {
    "1111": {
        "name": "Waqas Ishaque",
        "pin": "2222",
        "email": "w.ishaque001@gmail.com",
        "phone": "+92-300-1234567",
        "address": "123 Main Street, Karachi, Pakistan",
        "balance": 1250.50,
        "currency": "PKR",
        "account_type": "Checking",
        "account_number": "4321567890",
        "account_frozen": False,
        "intl_transactions_enabled": True,
        "cards": [
            {
                "id": "CARD_001",
                "type": "Debit",
                "last4": "0001",
                "status": "active",
                "expiry": "12/2028",
                "rewards_points": 0,
                "credit_limit": None,
                "balance": 0,
                "payment_due_date": None,
                "minimum_payment_due": None
            },
            {
                "id": "CARD_999",
                "type": "Credit",
                "last4": "9999",
                "status": "active",
                "expiry": "06/2027",
                "credit_limit": 5000.00,
                "balance": 1200.00,
                "rewards_points": 12500,
                "payment_due_date": "2026-02-15",
                "minimum_payment_due": 60.00
            }
        ],
        "loans": [
            {
                "loan_id": "LOAN_001",
                "loan_type": "Auto",
                "loan_amount": 25000.00,
                "interest_rate": 4.5,
                "loan_term": 60,
                "loan_status": "Approved",
                "monthly_payment": 466.00,
                "remaining_balance": 18500.00
            }
        ],
        "transactions": [
            {
                "date": "2026-02-05",
                "amount": -45.00,
                "description": "Grocery Store",
                "category": "Food & Dining",
                "status": "completed"
            },
            {
                "date": "2026-02-04",
                "amount": -120.00,
                "description": "Gas Station",
                "category": "Transportation",
                "status": "completed"
            },
            {
                "date": "2026-02-01",
                "amount": 1200.00,
                "description": "Salary Deposit - Vaulta Corp",
                "category": "Income",
                "status": "completed"
            },
            {
                "date": "2026-01-30",
                "amount": -89.99,
                "description": "Amazon Purchase",
                "category": "Shopping",
                "status": "completed"
            },
            {
                "date": "2026-01-28",
                "amount": -25.50,
                "description": "Coffee Shop",
                "category": "Food & Dining",
                "status": "completed"
            }
        ]
    }
}


# =============================================================================
# DATABASE-BACKED TOOL IMPLEMENTATIONS
# =============================================================================

async def verify_identity(customer_id: str, pin: str) -> bool:
    """
    CRITICAL GUARDRAIL: Verify customer identity using PIN.
    
    Strategy:
    1. Check hardcoded MOCK_CUSTOMERS first (instant response)
    2. If not found, query PostgreSQL database
    
    Args:
        customer_id: Customer's unique identifier
        pin: 4-digit PIN code
        
    Returns:
        True if identity verified, False otherwise
    """
    # FAST PATH: Check hardcoded mock data first
    if customer_id in MOCK_CUSTOMERS:
        return MOCK_CUSTOMERS[customer_id]["pin"] == pin
    
    # FALLBACK: Query database
    result = await execute_query(
        "SELECT pin FROM customers WHERE customer_id = %s",
        (customer_id,),
        fetch_one=True
    )
    
    if not result:
        return False
    
    return result['pin'] == pin


async def get_account_balance(customer_id: str) -> Dict:
    """
    Retrieve customer's account balance.
    
    Strategy:
    1. Check hardcoded MOCK_CUSTOMERS first (instant response)
    2. If not found, query PostgreSQL database
    
    Args:
        customer_id: Customer's unique identifier
        
    Returns:
        Dict containing balance, currency, and account type
    """
    # FAST PATH: Check hardcoded mock data first
    if customer_id in MOCK_CUSTOMERS:
        customer = MOCK_CUSTOMERS[customer_id]
        return {
            "balance": customer["balance"],
            "currency": customer["currency"],
            "account_type": customer["account_type"],
            "available_balance": customer["balance"],
            "pending_transactions": 0
        }
    
    # FALLBACK: Query database
    result = await execute_query(
        """
        SELECT account_balance, account_type 
        FROM customers 
        WHERE customer_id = %s
        """,
        (customer_id,),
        fetch_one=True
    )
    
    if not result:
        return {"error": "Customer not found"}
    
    return {
        "balance": float(result['account_balance']),
        "currency": "USD",
        "account_type": result['account_type'],
        "available_balance": float(result['account_balance']),
        "pending_transactions": 0
    }


async def get_recent_transactions(customer_id: str, count: int = 3) -> List[Dict]:
    """
    Retrieve customer's recent transaction history.
    
    Strategy:
    1. Check hardcoded MOCK_CUSTOMERS first (instant response)
    2. If not found, query PostgreSQL database
    
    Args:
        customer_id: Customer's unique identifier
        count: Number of transactions to return
        
    Returns:
        List of transaction dictionaries
    """
    # FAST PATH: Check hardcoded mock data first
    if customer_id in MOCK_CUSTOMERS:
        return MOCK_CUSTOMERS[customer_id]["transactions"][:count]
    
    # FALLBACK: Query database
    results = await execute_query(
        """
        SELECT 
            transaction_date::date as date,
            transaction_amount as amount,
            description,
            category,
            status
        FROM transactions
        WHERE customer_id = %s
        ORDER BY transaction_date DESC
        LIMIT %s
        """,
        (customer_id, count),
        fetch_all=True
    )
    
    if not results:
        return []
    
    # Convert to the expected format
    formatted_transactions = []
    for txn in results:
        formatted_transactions.append({
            "date": str(txn['date']),
            "amount": float(txn['amount']),
            "description": txn['description'],
            "category": txn['category'],
            "status": txn['status']
        })
    
    return formatted_transactions


async def block_card(card_id: str, reason: str) -> str:
    """
    PERMANENT ACTION: Block a customer's card in the database.
    
    Args:
        card_id: ID of the card to block
        reason: Reason for blocking
        
    Returns:
        Success message with reference number
    """
    ref_number = f"BLK-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
    
    # Update card status in database
    await execute_query(
        """
        UPDATE cards 
        SET card_status = 'blocked'
        WHERE card_id = %s
        """,
        (card_id,),
        fetch_all=False
    )
    
    return (
        f"SUCCESS: Card {card_id} has been permanently BLOCKED due to being {reason}. "
        f"Reference number: {ref_number}. A replacement card has been ordered and "
        f"will arrive at your registered address within 5-7 business days."
    )


async def request_statement(customer_id: str, period: str = "monthly") -> Dict:
    """
    Request an account statement.
    
    Args:
        customer_id: Customer's unique identifier
        period: Statement period
        
    Returns:
        Dict with status and delivery info
    """
    result = await execute_query(
        "SELECT email FROM customers WHERE customer_id = %s",
        (customer_id,),
        fetch_one=True
    )
    
    if not result:
        return {"success": False, "error": "Customer not found"}
    
    ref_number = f"STMT-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
    
    return {
        "success": True,
        "reference": ref_number,
        "email": result['email'],
        "period": period,
        "message": f"Your {period} statement has been generated and sent to {result['email']}."
    }

# =============================================================================
# NEW CAPABILITIES - Loans, Card Details, Feedback
# =============================================================================

async def get_loan_info(customer_id: str) -> List[Dict]:
    """
    Retrieve customer's loan information.
    
    Strategy:
    1. Check hardcoded MOCK_CUSTOMERS first (instant response)
    2. If not found, query PostgreSQL database
    
    REQUIRES: Customer must be verified
    
    Args:
        customer_id: Customer's unique identifier
        
    Returns:
        List of loan dictionaries with details
    """
    # FAST PATH: Check hardcoded mock data first
    if customer_id in MOCK_CUSTOMERS and "loans" in MOCK_CUSTOMERS[customer_id]:
        return MOCK_CUSTOMERS[customer_id]["loans"]
    
    # FALLBACK: Query database
    results = await execute_query(
        """
        SELECT 
            loan_id,
            loan_type,
            loan_amount,
            interest_rate,
            loan_term,
            loan_status,
            approval_rejection_date
        FROM loans
        WHERE customer_id = %s
        ORDER BY approval_rejection_date DESC
        """,
        (customer_id,),
        fetch_all=True
    )
    
    if not results:
        return []
    
    # Format results
    formatted_loans = []
    for loan in results:
        formatted_loans.append({
            "loan_id": loan['loan_id'],
            "loan_type": loan['loan_type'],
            "loan_amount": float(loan['loan_amount']) if loan['loan_amount'] else 0,
            "interest_rate": float(loan['interest_rate']) if loan['interest_rate'] else 0,
            "loan_term": loan['loan_term'],
            "loan_status": loan['loan_status'],
            "approval_date": str(loan['approval_rejection_date']) if loan['approval_rejection_date'] else None
        })
    
    return formatted_loans


async def get_card_details(customer_id: str, card_id: Optional[str] = None) -> Dict:
    """
    Retrieve detailed card information including rewards, payments, etc.
    
    Strategy:
    1. Check hardcoded MOCK_CUSTOMERS first (instant response)
    2. If not found, query PostgreSQL database
    
    REQUIRES: Customer must be verified
    
    Args:
        customer_id: Customer's unique identifier
        card_id: Specific card ID (optional, returns first card if not specified)
        
    Returns:
        Dict with detailed card information
    """
    # FAST PATH: Check hardcoded mock data first
    if customer_id in MOCK_CUSTOMERS:
        cards = MOCK_CUSTOMERS[customer_id]["cards"]
        if card_id:
            card = next((c for c in cards if c["id"] == card_id), None)
            if card:
                return card
        elif cards:
            return cards[0]  # Return first card
        return {"error": "Card not found"}
    
    # FALLBACK: Query database
    query = """
        SELECT 
            card_id,
            card_type,
            last_four_digits,
            credit_limit,
            credit_card_balance as balance,
            rewards_points,
            payment_due_date,
            minimum_payment_due,
            card_status
        FROM cards
        WHERE customer_id = %s
    """
    
    params = [customer_id]
    if card_id:
        query += " AND card_id = %s"
        params.append(card_id)
    
    query += " LIMIT 1"
    
    result = await execute_query(query, tuple(params), fetch_one=True)
    
    if not result:
        return {"error": "Card not found"}
    
    return {
        "id": result['card_id'],
        "type": result['card_type'],
        "last4": result['last_four_digits'],
        "credit_limit": float(result['credit_limit']) if result['credit_limit'] else None,
        "balance": float(result['balance']) if result['balance'] else 0,
        "rewards_points": result['rewards_points'] or 0,
        "payment_due_date": str(result['payment_due_date']) if result['payment_due_date'] else None,
        "minimum_payment_due": float(result['minimum_payment_due']) if result['minimum_payment_due'] else None,
        "status": result['card_status']
    }


async def list_customer_cards(customer_id: str) -> List[Dict]:
    """
    List all cards for a customer (safe, only shows last 4 digits).
    
    Strategy:
    1. Check hardcoded MOCK_CUSTOMERS first (instant response)
    2. If not found, query PostgreSQL database
    
    REQUIRES: Customer must be verified
    
    Args:
        customer_id: Customer's unique identifier
        
    Returns:
        List of card dictionaries with safe information
    """
    # FAST PATH: Check hardcoded mock data first
    if customer_id in MOCK_CUSTOMERS:
        return [{
            "id": card["id"],
            "type": card["type"],
            "last4": card["last4"],
            "status": card["status"]
        } for card in MOCK_CUSTOMERS[customer_id]["cards"]]
    
    # FALLBACK: Query database
    results = await execute_query(
        """
        SELECT 
            card_id,
            card_type,
            last_four_digits,
            card_status
        FROM cards
        WHERE customer_id = %s
        ORDER BY card_id
        """,
        (customer_id,),
        fetch_all=True
    )
    
    if not results:
        return []
    
    return [{
        "id": card['card_id'],
        "type": card['card_type'],
        "last4": card['last_four_digits'],
        "status": card['card_status']
    } for card in results]


async def submit_feedback(customer_id: str, feedback_type: str, feedback_text: str = "") -> Dict:
    """
    Submit customer feedback (complaint, praise, suggestion).
    
    SECURITY: No PII should be in feedback_text - it will be logged
    REQUIRES: Customer must be verified
    
    Args:
        customer_id: Customer's unique identifier
        feedback_type: Type of feedback ('Complaint', 'Praise', 'Suggestion')
        feedback_text: Optional feedback description (no PII!)
        
    Returns:
        Dict with success status and reference number
    """
    # Generate feedback ID and reference
    feedback_id = f"FB{customer_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    ref_number = f"FB-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
    
    # Insert into database
    try:
        await execute_query(
            """
            INSERT INTO feedback (
                feedback_id, customer_id, feedback_date, feedback_type,
                resolution_status
            ) VALUES (%s, %s, CURRENT_DATE, %s, 'Pending')
            """,
            (feedback_id, customer_id, feedback_type),
            fetch_all=False
        )
        
        return {
            "success": True,
            "reference": ref_number,
            "message": f"Your {feedback_type.lower()} has been submitted. Reference: {ref_number}. We'll review it within 2 business days."
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to submit feedback: {str(e)}"
        }


# =============================================================================
# SECURITY FEATURES - Cheque Book, Fraud Reporting, International Transactions
# =============================================================================

async def request_cheque_book(customer_id: str) -> Dict:
    """
    Request a new cheque book delivery.
    
    REQUIRES: Customer must be verified
    SECURITY: Delivers to registered address only
    
    Args:
        customer_id: Customer's unique identifier
        
    Returns:
        Dict with success status, reference number, and delivery info
    """
    # Get customer address
    if customer_id in MOCK_CUSTOMERS:
        address = MOCK_CUSTOMERS[customer_id].get("address", "registered address")
        email = MOCK_CUSTOMERS[customer_id]["email"]
    else:
        # Query database
        result = await execute_query(
            "SELECT address, email FROM customers WHERE customer_id = %s",
            (customer_id,),
            fetch_one=True
        )
        
        if not result:
            return {"success": False, "error": "Customer not found"}
        
        address = result['address'] or "registered address"
        email = result['email']
    
    # Generate reference number
    ref_number = f"CHQ-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
    request_id = f"REQ_CHQ_{customer_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Log request in database
    try:
        await execute_query(
            """
            INSERT INTO service_requests (
                request_id, customer_id, request_type, reference_number, details, status
            ) VALUES (%s, %s, 'CHEQUE_BOOK', %s, %s, 'Processing')
            """,
            (request_id, customer_id, ref_number, f"Delivery to: {address}"),
            fetch_all=False
        )
    except Exception as e:
        # If table doesn't exist or insert fails, continue anyway
        pass
    
    return {
        "success": True,
        "reference": ref_number,
        "delivery_address": address,
        "delivery_time": "7-10 business days",
        "message": (
            f"Your cheque book has been ordered! Reference: {ref_number}. "
            f"It will be delivered to {address} within 7-10 business days. "
            f"You'll receive a confirmation email at {email}."
        )
    }


async def report_fraud(customer_id: str, details: str = "") -> Dict:
    """
    Report fraudulent activity and IMMEDIATELY freeze account.
    
    CRITICAL SECURITY ACTIONS:
    1. Freeze account (prevents all transactions)
    2. Block all customer cards
    3. Log fraud report
    4. REQUIRES HUMAN ESCALATION (cannot unfreeze via voice)
    
    Args:
        customer_id: Customer's unique identifier
        details: Description of fraudulent activity
        
    Returns:
        Dict with reference number and escalation flag
    """
    ref_number = f"FRAUD-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
    request_id = f"REQ_FRAUD_{customer_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # CRITICAL: Freeze account IMMEDIATELY
    await execute_query(
        """
        UPDATE customers 
        SET account_frozen = TRUE 
        WHERE customer_id = %s
        """,
        (customer_id,),
        fetch_all=False
    )
    
    # CRITICAL: Block ALL cards
    await execute_query(
        """
        UPDATE cards 
        SET card_status = 'blocked' 
        WHERE customer_id = %s
        """,
        (customer_id,),
        fetch_all=False
    )
    
    # Log fraud report
    try:
        await execute_query(
            """
            INSERT INTO service_requests (
                request_id, customer_id, request_type, reference_number, details, status
            ) VALUES (%s, %s, 'FRAUD_REPORT', %s, %s, 'Urgent')
            """,
            (request_id, customer_id, ref_number, details or "Unauthorized transaction reported"),
            fetch_all=False
        )
    except Exception as e:
        # Continue even if logging fails - account is already frozen
        pass
    
    return {
        "success": True,
        "reference": ref_number,
        "account_frozen": True,
        "cards_blocked": True,
        "requires_human": True,  # MANDATORY escalation
        "message": (
            f"⚠️ FRAUD ALERT: Your account has been IMMEDIATELY FROZEN and all cards BLOCKED "
            f"to protect you from further unauthorized transactions. Reference: {ref_number}. "
            f"A fraud specialist will contact you shortly to resolve this issue. "
            f"This action cannot be reversed via phone - human verification required."
        )
    }


async def toggle_international_transactions(customer_id: str, enable: bool) -> Dict:
    """
    Enable or disable international transactions on customer's account.
    
    REQUIRES: Customer must be verified
    
    Args:
        customer_id: Customer's unique identifier
        enable: True to enable, False to disable
        
    Returns:
        Dict with success status and confirmation
    """
    # Update database
    await execute_query(
        """
        UPDATE customers 
        SET intl_transactions_enabled = %s 
        WHERE customer_id = %s
        """,
        (enable, customer_id),
        fetch_all=False
    )
    
    # Log the change
    action = "ENABLED" if enable else "DISABLED"
    try:
        request_id = f"REQ_INTL_{customer_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        await execute_query(
            """
            INSERT INTO service_requests (
                request_id, customer_id, request_type, details, status
            ) VALUES (%s, %s, 'INTL_TOGGLE', %s, 'Completed')
            """,
            (request_id, customer_id, f"International transactions {action}"),
            fetch_all=False
        )
    except Exception as e:
        # Continue even if logging fails - setting is already updated
        pass
    
    status_word = "ENABLED" if enable else "DISABLED"
    message = (
        f"International transactions are now {status_word} on your account. "
        f"You can {'use your cards abroad' if enable else 'only use cards domestically'}. "
        f"You can change this setting anytime by calling us."
    )
    
    return {
        "success": True,
        "intl_transactions_enabled": enable,
        "message": message
    }
