#!/usr/bin/env python3
"""
Test PostgreSQL and pgvector connectivity.

Tests:
1. psycopg2 connection
2. pgvector extension availability
3. Vector operations (CREATE TABLE, INSERT, SELECT with distance)
4. SQLAlchemy connection
"""
import os
import sys
from dotenv import load_dotenv
import psycopg2
from sqlalchemy import create_engine, text

# Colors
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
NC = '\033[0m'

def print_test(name):
    print(f"\n{YELLOW}Testing: {name}{NC}")

def print_success(msg):
    print(f"{GREEN}✓ {msg}{NC}")

def print_error(msg):
    print(f"{RED}✗ {msg}{NC}")

def main():
    # Load environment
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")

    if not db_url:
        print_error("DATABASE_URL not set in .env file")
        sys.exit(1)

    print(f"Database URL: {db_url}")

    # Test 1: psycopg2 connection
    print_test("psycopg2 connection")
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print_success(f"Connected: {version}")
        cursor.close()
    except Exception as e:
        print_error(f"psycopg2 connection failed: {e}")
        sys.exit(1)

    # Test 2: pgvector extension
    print_test("pgvector extension availability")
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
        result = cursor.fetchone()
        if result:
            print_success(f"pgvector extension enabled: {result}")
        else:
            print_error("pgvector extension not found")
            sys.exit(1)
        cursor.close()
    except Exception as e:
        print_error(f"pgvector check failed: {e}")
        sys.exit(1)

    # Test 3: Vector operations
    print_test("Vector operations (CREATE, INSERT, SELECT with distance)")
    try:
        cursor = conn.cursor()

        # Create test table
        cursor.execute("DROP TABLE IF EXISTS test_vectors;")
        cursor.execute("""
            CREATE TABLE test_vectors (
                id SERIAL PRIMARY KEY,
                embedding vector(3)
            );
        """)
        print_success("Created test table with vector column")

        # Insert vectors
        cursor.execute("INSERT INTO test_vectors (embedding) VALUES (%s), (%s), (%s);",
                      ('[1,2,3]', '[4,5,6]', '[1,2,4]'))
        print_success("Inserted test vectors")

        # Query with distance
        cursor.execute("""
            SELECT id, embedding, embedding <-> '[1,2,3]' AS distance
            FROM test_vectors
            ORDER BY distance
            LIMIT 3;
        """)
        results = cursor.fetchall()
        print_success(f"Distance query successful: {len(results)} results")
        for row in results:
            print(f"  ID: {row[0]}, Vector: {row[1]}, Distance: {row[2]}")

        # Cleanup
        cursor.execute("DROP TABLE test_vectors;")
        cursor.close()
        conn.commit()
        print_success("Vector operations test passed")
    except Exception as e:
        print_error(f"Vector operations failed: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()

    # Test 4: SQLAlchemy connection
    print_test("SQLAlchemy connection")
    try:
        engine = create_engine(db_url)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print_success(f"SQLAlchemy connected: {result.fetchone()}")
    except Exception as e:
        print_error(f"SQLAlchemy connection failed: {e}")
        sys.exit(1)

    print(f"\n{GREEN}✅ All tests passed!{NC}\n")

if __name__ == "__main__":
    main()
