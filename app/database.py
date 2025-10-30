"""
Database connection module for SQLite
Provides context managers and utility functions for database operations
"""

import sqlite3
from contextlib import contextmanager
from typing import Generator, Dict, List, Any
import os

# Database configuration
DATABASE_PATH = os.getenv('SQLITE_DB_PATH', 'cardiovascular.db')


@contextmanager
def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager for SQLite database connections.
    Automatically commits on success and rolls back on error.
    
    Usage:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM patients")
            results = cursor.fetchall()
    
    Yields:
        sqlite3.Connection: Database connection with row_factory set
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dict-like objects
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def dict_from_row(row: sqlite3.Row) -> Dict[str, Any]:
    """Convert SQLite Row object to dictionary"""
    return dict(zip(row.keys(), row))


def execute_query(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    """Execute a SELECT query and return results as list of dictionaries"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict_from_row(row) for row in rows]


def execute_insert(query: str, params: tuple = ()) -> int:
    """Execute an INSERT query and return the last inserted row ID"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.lastrowid


def execute_update(query: str, params: tuple = ()) -> int:
    """Execute an UPDATE or DELETE query and return number of affected rows"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.rowcount


def test_connection() -> bool:
    """Test database connection and print table information"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
            tables = cursor.fetchall()
            
            print(f"✓ Connected to database: {DATABASE_PATH}")
            print(f"✓ Found {len(tables)} tables:")
            
            for table in tables:
                table_name = table['name']
                cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
                count = cursor.fetchone()['count']
                print(f"  - {table_name}: {count} rows")
            
            return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False


if __name__ == "__main__":
    test_connection()