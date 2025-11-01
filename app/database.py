"""
Database connection module for SQLite and MongoDB
Provides context managers, utility functions, and automatic MongoDB population
"""

import sqlite3
from contextlib import contextmanager
from typing import Generator, Dict, List, Any
import os
from pymongo import MongoClient
from pymongo.database import Database
from urllib.parse import quote_plus
from faker import Faker
import random

# ------------------------------
# Database configuration
# ------------------------------
DATABASE_PATH = os.getenv('SQLITE_DB_PATH', 'cardiovascular.db')

# MongoDB Configuration
username = quote_plus('fndihokubw1_db_user')
password = quote_plus('@Fruits01234')  # your actual password
MONGO_URI = f"mongodb+srv://{username}:{password}@cluster0.o0nb87n.mongodb.net/?retryWrites=true&w=majority"
MONGO_DB_NAME = os.getenv('MONGO_DB', 'cardiovascular_db')

_mongo_client = None
_mongo_db = None

# ------------------------------
# MongoDB Connection & Population
# ------------------------------

def get_mongo_db() -> Database:
    """Get MongoDB database connection (singleton)"""
    global _mongo_client, _mongo_db
    if _mongo_db is None:
        try:
            _mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            _mongo_client.server_info()  # Test connection
            _mongo_db = _mongo_client[MONGO_DB_NAME]
            print(f"✓ Connected to MongoDB: {MONGO_DB_NAME}")
        except Exception as e:
            print(f"✗ MongoDB connection failed: {e}")
            raise
    return _mongo_db

def close_mongo_connection():
    """Close MongoDB connection"""
    global _mongo_client, _mongo_db
    if _mongo_client:
        _mongo_client.close()
        _mongo_client = None
        _mongo_db = None
        print("✓ MongoDB connection closed")

def test_mongo_connection() -> bool:
    """Test MongoDB connection and populate if empty"""
    try:
        db = get_mongo_db()
        collections = db.list_collection_names()
        print(f"✓ MongoDB connected. Found {len(collections)} collections:")
        for col in collections:
            count = db[col].count_documents({})
            print(f"  - {col}: {count} documents")
        
        # Auto-populate if patients or medical_records are missing
        if 'patients' not in collections or 'medical_records' not in collections:
            print("⚠️ MongoDB collections missing. Populating now...")
            populate_mongodb(db)
        return True
    except Exception as e:
        print(f"✗ MongoDB connection test failed: {e}")
        return False

def populate_mongodb(db: Database, n_records: int = 70000):
    """
    Populate MongoDB with dummy patients and medical_records if collections are empty
    """
    fake = Faker()
    patients_collection = db['patients']
    records_collection = db['medical_records']

    if patients_collection.count_documents({}) == 0:
        print(f"Creating {n_records} patient documents...")
        patient_docs = [{
            "patient_id": i,
            "demographics": {
                "age": random.randint(20, 80),
                "gender": random.choice(['male', 'female']),
                "height": random.randint(150, 200),
                "weight": random.randint(50, 120),
                "bmi": round(random.uniform(18, 35), 1)
            },
            "lifestyle": {
                "smoker": random.choice([True, False]),
                "alcohol": random.choice([True, False]),
                "physical_activity": random.choice(['low', 'medium', 'high'])
            }
        } for i in range(1, n_records + 1)]
        patients_collection.insert_many(patient_docs)
        print(f"Inserted {n_records} patient documents into MongoDB")

    if records_collection.count_documents({}) == 0:
        print(f"Creating {n_records} medical record documents...")
        medical_docs = [{
            "patient_id": i,
            "measurements": {
                "blood_pressure": f"{random.randint(100, 140)}/{random.randint(60, 90)}",
                "cholesterol": random.randint(150, 300),
                "glucose": random.randint(70, 140)
            },
            "diagnosis": {
                "has_cardiovascular_disease": random.choice([True, False]),
                "date": fake.date_this_decade().isoformat()
            }
        } for i in range(1, n_records + 1)]
        records_collection.insert_many(medical_docs)
        print(f"Inserted {n_records} medical record documents into MongoDB")

# ------------------------------
# SQLite Utilities
# ------------------------------

@contextmanager
def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
    """SQLite context manager"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def dict_from_row(row: sqlite3.Row) -> Dict[str, Any]:
    return dict(zip(row.keys(), row))

def execute_query(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict_from_row(row) for row in rows]

def execute_insert(query: str, params: tuple = ()) -> int:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.lastrowid

def execute_update(query: str, params: tuple = ()) -> int:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.rowcount

def test_connection() -> bool:
    """Test SQLite and print table info"""
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

# ------------------------------
# Run test on execution
# ------------------------------

if __name__ == "__main__":
    test_connection()
    test_mongo_connection()
