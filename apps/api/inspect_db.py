#!/usr/bin/env python3
"""
Quick script to inspect the Neon PostgreSQL database schema
"""
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = "postgresql://neondb_owner:npg_B9fYFZWk5Tld@ep-steep-forest-aiuvikcy-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

def inspect_database():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # List all tables
    print("=" * 80)
    print("TABLES IN DATABASE")
    print("=" * 80)
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    tables = cur.fetchall()
    for table in tables:
        print(f"  • {table['table_name']}")
    
    print("\n")
    
    # For each table, show columns and sample data
    for table in tables:
        table_name = table['table_name']
        print("=" * 80)
        print(f"TABLE: {table_name}")
        print("=" * 80)
        
        # Get column info
        cur.execute(f"""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns
            WHERE table_name = '{table_name}'
            ORDER BY ordinal_position;
        """)
        columns = cur.fetchall()
        
        print("\nCOLUMNS:")
        for col in columns:
            max_len = f"({col['character_maximum_length']})" if col['character_maximum_length'] else ""
            print(f"  • {col['column_name']:30s} {col['data_type']}{max_len}")
        
        # Get row count
        cur.execute(f"SELECT COUNT(*) as count FROM {table_name};")
        count = cur.fetchone()['count']
        print(f"\nROW COUNT: {count}")
        
        # Show sample data (first 3 rows)
        if count > 0:
            cur.execute(f"SELECT * FROM {table_name} LIMIT 3;")
            samples = cur.fetchall()
            print(f"\nSAMPLE DATA (first 3 rows):")
            for i, row in enumerate(samples, 1):
                print(f"\n  Row {i}:")
                for key, value in row.items():
                    # Truncate long values
                    val_str = str(value)[:50] if value else "NULL"
                    print(f"    {key:30s}: {val_str}")
        
        print("\n")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    try:
        inspect_database()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
