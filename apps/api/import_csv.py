"""
Fresh CSV Import - Clears database and imports updated CSV with PIN and last4 fields
"""

import csv
import psycopg2
from datetime import datetime

DATABASE_URL = "postgresql://neondb_owner:npg_B9fYFZWk5Tld@ep-steep-forest-aiuvikcy-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"
CSV_FILE = "/Users/mac/Downloads/db.csv"


def parse_date(date_str):
    """Parse various date formats."""
    if not date_str or date_str.strip() == '':
        return None
    
    formats = ['%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d', '%m/%d/%y']
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None


def import_csv():
    print("="*60)
    print("FRESH DATABASE IMPORT")
    print("="*60)
    
    print("\n1. Connecting to database...")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("2. Dropping and recreating all tables...")
    cur.execute("""
        DROP TABLE IF EXISTS feedback CASCADE;
        DROP TABLE IF EXISTS loans CASCADE;
        DROP TABLE IF EXISTS transactions CASCADE;
        DROP TABLE IF EXISTS cards CASCADE;
        DROP TABLE IF EXISTS customers CASCADE;
    """)
    
    print("3. Creating fresh schema...")
    cur.execute("""
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
            pin VARCHAR(4),
            anomaly BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE cards (
            card_id VARCHAR(20) PRIMARY KEY,
            customer_id VARCHAR(10) REFERENCES customers(customer_id) ON DELETE CASCADE,
            card_type VARCHAR(20),
            credit_limit DECIMAL(15, 2),
            credit_card_balance DECIMAL(15, 2) DEFAULT 0.00,
            minimum_payment_due DECIMAL(15, 2),
            payment_due_date DATE,
            last_credit_card_payment_date DATE,
            rewards_points INTEGER DEFAULT 0,
            card_status VARCHAR(20) DEFAULT 'active',
            last_four_digits VARCHAR(4),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE transactions (
            transaction_id VARCHAR(50) PRIMARY KEY,
            customer_id VARCHAR(10) REFERENCES customers(customer_id) ON DELETE CASCADE,
            transaction_date TIMESTAMP NOT NULL,
            transaction_type VARCHAR(50),
            transaction_amount DECIMAL(15, 2) NOT NULL,
            account_balance_after_transaction DECIMAL(15, 2),
            description TEXT,
            category VARCHAR(100),
            status VARCHAR(20) DEFAULT 'completed',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE loans (
            loan_id VARCHAR(20) PRIMARY KEY,
            customer_id VARCHAR(10) REFERENCES customers(customer_id) ON DELETE CASCADE,
            loan_amount DECIMAL(15, 2) NOT NULL,
            loan_type VARCHAR(50),
            interest_rate DECIMAL(5, 2),
            loan_term INTEGER,
            approval_rejection_date DATE,
            loan_status VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE feedback (
            feedback_id VARCHAR(20) PRIMARY KEY,
            customer_id VARCHAR(10) REFERENCES customers(customer_id) ON DELETE CASCADE,
            feedback_date DATE NOT NULL,
            feedback_type VARCHAR(50),
            resolution_status VARCHAR(20) DEFAULT 'pending',
            resolution_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX idx_customers_email ON customers(email);
        CREATE INDEX idx_cards_customer ON cards(customer_id);
        CREATE INDEX idx_transactions_customer ON transactions(customer_id);
        CREATE INDEX idx_loans_customer ON loans(customer_id);
        CREATE INDEX idx_feedback_customer ON feedback(customer_id);
    """)
    conn.commit()
    
    print(f"4. Reading CSV: {CSV_FILE}")
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        customers_added = set()
        cards_added = set()
        transactions_added = set()
        loans_added = set()
        feedback_added = set()
        
        for row_num, row in enumerate(reader, 1):
            customer_id = row['Customer ID']
            
            # Insert customer (only once)
            if customer_id not in customers_added:
                try:
                    cur.execute("""
                        INSERT INTO customers (
                            customer_id, first_name, last_name, age, gender, address, city,
                            contact_number, email, account_type, account_balance,
                            date_of_account_opening, last_transaction_date, branch_id, pin, anomaly
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (customer_id) DO NOTHING
                    """, (
                        customer_id,
                        row['First Name'],
                        row['Last Name'],
                        int(row['Age']) if row['Age'] else None,
                        row['Gender'],
                        row['Address'],
                        row['City'],
                        row['Contact Number'],
                        row['Email'],
                        row['Account Type'],
                        float(row['Account Balance']) if row['Account Balance'] else 0,
                        parse_date(row['Date Of Account Opening']),
                        parse_date(row['Last Transaction Date']),
                        row['Branch ID'],
                        row['PIN'],  # NEW: Using PIN from CSV
                        row['Anomaly'] == '1' or row['Anomaly'] == 'True'
                    ))
                    customers_added.add(customer_id)
                except Exception as e:
                    print(f"Error inserting customer {customer_id}: {e}")
            
            # Insert card
            card_id = row['CardID']
            if card_id and card_id not in cards_added:
                try:
                    cur.execute("""
                        INSERT INTO cards (
                            card_id, customer_id, card_type, credit_limit, credit_card_balance,
                            minimum_payment_due, payment_due_date, last_credit_card_payment_date,
                            rewards_points, card_status, last_four_digits
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (card_id) DO NOTHING
                    """, (
                        card_id,
                        customer_id,
                        row['Card Type'],
                        float(row['Credit Limit']) if row['Credit Limit'] else None,
                        float(row['Credit Card Balance']) if row['Credit Card Balance'] else 0,
                        float(row['Minimum Payment Due']) if row['Minimum Payment Due'] else None,
                        parse_date(row['Payment Due Date']),
                        parse_date(row['Last Credit Card Payment Date']),
                        int(row['Rewards Points']) if row['Rewards Points'] else 0,
                        'active',
                        row.get('last4', '0000')  # NEW: last 4 digits from CSV
                    ))
                    cards_added.add(card_id)
                except Exception as e:
                    print(f"Error inserting card {card_id}: {e}")
            
            # Insert transaction with auto-category
            txn_id = row['TransactionID']
            if txn_id and txn_id not in transactions_added:
                try:
                    txn_type = row['Transaction Type']
                    # Smart category assignment
                    if 'withdrawal' in txn_type.lower() or 'debit' in txn_type.lower():
                        category = ['Food & Dining', 'Transportation', 'Shopping', 'Utilities'][hash(txn_id) % 4]
                        description = {
                            'Food & Dining': ['Grocery Store', 'Restaurant', 'Coffee Shop'][hash(txn_id) % 3],
                            'Transportation': ['Gas Station', 'Uber', 'Parking'][hash(txn_id) % 3],
                            'Shopping': ['Amazon Purchase', 'Online Shopping', 'Clothing Store'][hash(txn_id) % 3],
                            'Utilities': ['Electric Bill', 'Internet Bill', 'Phone Bill'][hash(txn_id) % 3]
                        }.get(category, txn_type)
                    elif 'deposit' in txn_type.lower() or 'credit' in txn_type.lower():
                        category = 'Income'
                        description = 'Salary Deposit'
                    elif 'transfer' in txn_type.lower():
                        category = 'Transfer'
                        description = 'Account Transfer'
                    else:
                        category = 'Other'
                        description = txn_type
                    
                    cur.execute("""
                        INSERT INTO transactions (
                            transaction_id, customer_id, transaction_date, transaction_type,
                            transaction_amount, account_balance_after_transaction, description, category, status
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (transaction_id) DO NOTHING
                    """, (
                        txn_id,
                        customer_id,
                        parse_date(row['Transaction Date']),
                        txn_type,
                        float(row['Transaction Amount']) if row['Transaction Amount'] else 0,
                        float(row['Account Balance After Transaction']) if row['Account Balance After Transaction'] else None,
                        description,
                        category,
                        'completed'
                    ))
                    transactions_added.add(txn_id)
                except Exception as e:
                    print(f"Error inserting transaction {txn_id}: {e}")
            
            # Insert loan
            loan_id = row['Loan ID']
            if loan_id and loan_id not in loans_added:
                try:
                    cur.execute("""
                        INSERT INTO loans (
                            loan_id, customer_id, loan_amount, loan_type, interest_rate,
                            loan_term, approval_rejection_date, loan_status
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (loan_id) DO NOTHING
                    """, (
                        loan_id,
                        customer_id,
                        float(row['Loan Amount']) if row['Loan Amount'] else None,
                        row['Loan Type'],
                        float(row['Interest Rate']) if row['Interest Rate'] else None,
                        int(row['Loan Term']) if row['Loan Term'] else None,
                        parse_date(row['Approval/Rejection Date']),
                        row['Loan Status']
                    ))
                    loans_added.add(loan_id)
                except Exception as e:
                    print(f"Error inserting loan {loan_id}: {e}")
            
            # Insert feedback
            feedback_id = row['Feedback ID']
            if feedback_id and feedback_id not in feedback_added:
                try:
                    cur.execute("""
                        INSERT INTO feedback (
                            feedback_id, customer_id, feedback_date, feedback_type,
                            resolution_status, resolution_date
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (feedback_id) DO NOTHING
                    """, (
                        feedback_id,
                        customer_id,
                        parse_date(row['Feedback Date']),
                        row['Feedback Type'],
                        row['Resolution Status'],
                        parse_date(row['Resolution Date'])
                    ))
                    feedback_added.add(feedback_id)
                except Exception as e:
                    print(f"Error inserting feedback {feedback_id}: {e}")
            
            if row_num % 10 == 0:
                conn.commit()
        
        conn.commit()
        
        print("\n" + "="*60)
        print("IMPORT COMPLETE!")
        print("="*60)
        print(f"✓ Customers: {len(customers_added)}")
        print(f"✓ Cards: {len(cards_added)}")
        print(f"✓ Transactions: {len(transactions_added)}")
        print(f"✓ Loans: {len(loans_added)}")
        print(f"✓ Feedback: {len(feedback_added)}")
        
        # Show sample data
        print("\n" + "="*60)
        print("SAMPLE DATA (first 3 customers)")
        print("="*60)
        cur.execute("""
            SELECT customer_id, first_name, last_name, email, account_balance, pin 
            FROM customers 
            ORDER BY customer_id::int 
            LIMIT 3
        """)
        for row in cur.fetchall():
            print(f"  ID {row[0]:>4s}: {row[1]} {row[2]:15s} | PIN: {row[5]} | Balance: ${row[4]:.2f}")
        
    cur.close()
    conn.close()


if __name__ == "__main__":
    try:
        import_csv()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
