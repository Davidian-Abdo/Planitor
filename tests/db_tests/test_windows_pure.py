#!/usr/bin/env python3
"""
Test pure psycopg2 connection on Windows
"""
import psycopg2
from psycopg2 import OperationalError

def test_windows_connection():
    """Test Windows-specific connection"""
    try:
        print("🐘 WINDOWS PURE PSYCOPG2 TEST")
        print("=" * 50)
        
        # Use the exact same connection that worked before
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='Planitor_db',
            user='postgres',
            password='Pos196699@'
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        
        print(f"✅ Pure psycopg2 connection successful!")
        print(f"📊 Version: {version}")
        
        # Test if we can use this connection for SQLAlchemy
        print("\n🔧 Connection details:")
        print(f"   DSN: {conn.dsn}")
        print(f"   Encoding: {conn.encoding}")
        print(f"   Protocol: {conn.protocol}")
        
        cursor.close()
        conn.close()
        return True
        
    except OperationalError as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_windows_connection()