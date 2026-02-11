"""
Database Schema Creation for Vaulta Banking System

Creates normalized tables based on the column list provided:
- customers (main customer data)
- cards (credit/debit cards)
- transactions (transaction history)
- loans (loan information)
- feedback (customer feedback)
"""

CREATE_SCHEMA_SQL = """
-- Drop existing tables if they exist
DROP TABLE IF EXISTS feedback CASCADE;
DROP TABLE IF EXISTS loans CASCADE;
DROP TABLE IF EXISTS transactions CASCADE;
DROP TABLE IF EXISTS cards CASCADE;
DROP TABLE IF EXISTS customers CASCADE;

-- Main customers table
CREATE TABLE customers (
    customer_id VARCHAR(10) PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    age INTEGER,
    gender VARCHAR(10),
    address TEXT,
    city VARCHAR(100),
    contact_number VARCHAR(20),
    email VARCHAR(255),
    account_type VARCHAR(50),
    account_balance DECIMAL(15, 2) DEFAULT 0.00,
    date_of_account_opening DATE,
    last_transaction_date DATE,
    branch_id VARCHAR(10),
    pi VARCHAR(4),  -- PIN (4 digits)
    anomaly BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cards table (credit/debit cards)
CREATE TABLE cards (
    card_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(10) REFERENCES customers(customer_id) ON DELETE CASCADE,
    card_type VARCHAR(20),  -- 'Credit' or 'Debit'
    credit_limit DECIMAL(15, 2),
    credit_card_balance DECIMAL(15, 2) DEFAULT 0.00,
    minimum_payment_due DECIMAL(15, 2),
    payment_due_date DATE,
    last_credit_card_payment_date DATE,
    rewards_points INTEGER DEFAULT 0,
    card_status VARCHAR(20) DEFAULT 'active',  -- 'active', 'blocked', 'expired'
    last_four_digits VARCHAR(4),
    expiry_date VARCHAR(7),  -- Format: MM/YYYY
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transactions table
CREATE TABLE transactions (
    transaction_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(10) REFERENCES customers(customer_id) ON DELETE CASCADE,
    transaction_date TIMESTAMP NOT NULL,
    transaction_type VARCHAR(50),  -- 'debit', 'credit', 'transfer', etc.
    transaction_amount DECIMAL(15, 2) NOT NULL,
    account_balance_after_transaction DECIMAL(15, 2),
    description TEXT,
    category VARCHAR(100),
    status VARCHAR(20) DEFAULT 'completed',  -- 'pending', 'completed', 'failed'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Loans table
CREATE TABLE loans (
    loan_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(10) REFERENCES customers(customer_id) ON DELETE CASCADE,
    loan_amount DECIMAL(15, 2) NOT NULL,
    loan_type VARCHAR(50),
    interest_rate DECIMAL(5, 2),
    loan_term INTEGER,  -- in months
    approval_rejection_date DATE,
    loan_status VARCHAR(20),  -- 'approved', 'rejected', 'pending', 'closed'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Feedback table
CREATE TABLE feedback (
    feedback_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(10) REFERENCES customers(customer_id) ON DELETE CASCADE,
    feedback_date DATE NOT NULL,
    feedback_type VARCHAR(50),
    feedback_text TEXT,
    resolution_status VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'resolved', 'closed'
    resolution_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_contact ON customers(contact_number);
CREATE INDEX idx_cards_customer ON cards(customer_id);
CREATE INDEX idx_cards_status ON cards(card_status);
CREATE INDEX idx_transactions_customer ON transactions(customer_id);
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_loans_customer ON loans(customer_id);
CREATE INDEX idx_feedback_customer ON feedback(customer_id);

-- Seed test data (same as your mock data)
INSERT INTO customers (
    customer_id, first_name, last_name, age, gender, address, city,
    contact_number, email, account_type, account_balance,
    date_of_account_opening, pi, branch_id
) VALUES (
    '1234', 'Sahan', 'Madusanka', 28, 'Male',
    '123 Main Street', 'San Francisco',
    '+1-555-0123', 'sahan@example.com', 'Checking', 1250.50,
    '2020-01-15', '5678', 'BR001'
);

-- Insert cards for customer 1234
INSERT INTO cards (
    card_id, customer_id, card_type, card_status, last_four_digits, expiry_date
) VALUES
    ('CARD_001', '1234', 'Debit', 'active', '0001', '12/2028'),
    ('CARD_999', '1234', 'Credit', 'active', '9999', '06/2027');

UPDATE cards 
SET credit_limit = 5000.00, credit_card_balance = 1200.00
WHERE card_id = 'CARD_999';

-- Insert sample transactions
INSERT INTO transactions (
    transaction_id, customer_id, transaction_date, transaction_type,
    transaction_amount, account_balance_after_transaction, description, category, status
) VALUES
    ('TXN_001', '1234', '2026-02-05 10:30:00', 'debit', -45.00, 1250.50, 'Grocery Store', 'Food & Dining', 'completed'),
    ('TXN_002', '1234', '2026-02-04 14:20:00', 'debit', -120.00, 1295.50, 'Gas Station', 'Transportation', 'completed'),
    ('TXN_003', '1234', '2026-02-01 09:00:00', 'credit', 1200.00, 1415.50, 'Salary Deposit - Vaulta Corp', 'Income', 'completed'),
    ('TXN_004', '1234', '2026-01-30 16:45:00', 'debit', -89.99, 215.50, 'Amazon Purchase', 'Shopping', 'completed'),
    ('TXN_005', '1234', '2026-01-28 08:15:00', 'debit', -25.50, 305.49, 'Coffee Shop', 'Food & Dining', 'completed');

-- Update customer's last transaction date
UPDATE customers SET last_transaction_date = '2026-02-05' WHERE customer_id = '1234';
"""

if __name__ == "__main__":
    import psycopg2
    
    DATABASE_URL = "postgresql://neondb_owner:npg_B9fYFZWk5Tld@ep-steep-forest-aiuvikcy-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"
    
    try:
        print("Connecting to database...")
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("Creating schema and seeding data...")
        cur.execute(CREATE_SCHEMA_SQL)
        conn.commit()
        
        print("✓ Schema created successfully!")
        
        # Verify
        cur.execute("SELECT COUNT(*) FROM customers;")
        customer_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM transactions;")
        txn_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM cards;")
        card_count = cur.fetchone()[0]
        
        print(f"✓ Seeded {customer_count} customer(s)")
        print(f"✓ Seeded {txn_count} transaction(s)")
        print(f"✓ Seeded {card_count} card(s)")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
