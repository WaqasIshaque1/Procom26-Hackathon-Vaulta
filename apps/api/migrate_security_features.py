"""
Database Migration: Add Security Features Schema

Adds:
1. account_frozen column to customers table
2. intl_transactions_enabled column to customers table
3. service_requests table for cheque books, fraud reports, etc.
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def migrate_database():
    print("="*60)
    print("DATABASE MIGRATION: Security Features")
    print("="*60)
    
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    try:
        # Step 1: Add columns to customers table
        print("\n1. Adding security columns to customers table...")
        cur.execute("""
            ALTER TABLE customers 
            ADD COLUMN IF NOT EXISTS account_frozen BOOLEAN DEFAULT FALSE,
            ADD COLUMN IF NOT EXISTS intl_transactions_enabled BOOLEAN DEFAULT TRUE;
        """)
        print("   ✓ Added account_frozen column")
        print("   ✓ Added intl_transactions_enabled column")
        
        # Step 2: Create service_requests table
        print("\n2. Creating service_requests table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS service_requests (
                request_id VARCHAR(50) PRIMARY KEY,
                customer_id VARCHAR(10) REFERENCES customers(customer_id) ON DELETE CASCADE,
                request_type VARCHAR(50) NOT NULL,
                request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(20) DEFAULT 'Pending',
                reference_number VARCHAR(50),
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_service_requests_customer 
            ON service_requests(customer_id);
            
            CREATE INDEX IF NOT EXISTS idx_service_requests_type 
            ON service_requests(request_type);
        """)
        print("   ✓ Created service_requests table")
        print("   ✓ Added indexes")
        
        conn.commit()
        
        # Verify
        print("\n3. Verifying schema changes...")
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'customers' 
            AND column_name IN ('account_frozen', 'intl_transactions_enabled')
            ORDER BY column_name;
        """)
        columns = cur.fetchall()
        for col in columns:
            print(f"   ✓ {col[0]}: {col[1]}")
        
        cur.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_name = 'service_requests';
        """)
        if cur.fetchone():
            print("   ✓ service_requests table exists")
        
        print("\n" + "="*60)
        print("✅ MIGRATION COMPLETE!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    migrate_database()
