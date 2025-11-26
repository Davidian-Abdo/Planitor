#!/usr/bin/env python3
"""
Test connection with your specific password
"""
import psycopg2
from psycopg2 import OperationalError

def test_connection():
    """Test connection with your exact password"""
    try:
        print("🐘 TESTING WITH YOUR PASSWORD: Pos196699@")
        print("=" * 50)
        
        # Use your exact credentials
        db_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'Planitor_db',
            'user': 'postgres',
            'password': 'ABDOABDO'  # Your exact password
        }
        
        print("🔧 CONNECTION CONFIG:")
        print(f"   Host: {db_config['host']}")
        print(f"   Port: {db_config['port']}")
        print(f"   Database: {db_config['database']}")
        print(f"   User: {db_config['user']}")
        print(f"   Password: {'*' * len(db_config['password'])}")
        
        print("\n🔗 Attempting connection...")
        connection = psycopg2.connect(**db_config)
        
        cursor = connection.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        
        print(f"✅ SUCCESS! Connected to PostgreSQL")
        print(f"📊 Version: {version.split(',')[0]}")
        
        # Check database
        cursor.execute("SELECT current_database()")
        db_name = cursor.fetchone()[0]
        print(f"📁 Connected to database: {db_name}")
        
        cursor.close()
        connection.close()
        return True
        
    except OperationalError as e:
        print(f"❌ CONNECTION FAILED: {e}")
        print("\n🔧 TROUBLESHOOTING:")
        print("1. Check if PostgreSQL service is running")
        print("2. Verify database 'Planitor_db' exists in pgAdmin")
        print("3. Make sure password 'Pos196699@' is correct")
        print("4. Try connecting in pgAdmin with these exact credentials")
        return False
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        return False

if __name__ == "__main__":
    test_connection()