"""
PostgreSQL Database Connection for Vaulta
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
from app.core.config import settings
from typing import Optional

# Connection pool for better performance
_pool: Optional[SimpleConnectionPool] = None

def get_pool():
    """Get or create connection pool."""
    global _pool
    if _pool is None:
        _pool = SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            dsn=settings.DATABASE_URL
        )
    return _pool

def get_db_connection():
    """Get a database connection from the pool."""
    pool = get_pool()
    return pool.getconn()

def release_db_connection(conn):
    """Return connection to the pool."""
    pool = get_pool()
    pool.putconn(conn)

async def execute_query(query: str, params: tuple = None, fetch_one: bool = False, fetch_all: bool = True):
    """
    Execute a SQL query and return results (async-safe).
    
    Args:
        query: SQL query string
        params: Query parameters (tuple)
        fetch_one: Return single row
        fetch_all: Return all rows
        
    Returns:
        Query results as dict or list of dicts
    """
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    
    def _execute_sync():
        conn = get_db_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params)
            
            if fetch_one:
                result = cursor.fetchone()
                return dict(result) if result else None
            elif fetch_all:
                results = cursor.fetchall()
                return [dict(row) for row in results]
            else:
                conn.commit()
                return None
        finally:
            release_db_connection(conn)
    
    # Run blocking DB operation in thread pool to avoid blocking event loop
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        result = await loop.run_in_executor(executor, _execute_sync)
    return result
