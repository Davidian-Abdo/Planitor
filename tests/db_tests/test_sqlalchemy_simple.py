#!/usr/bin/env python3
"""
Test SQLAlchemy connection with minimal configuration
"""
import os
import sys
from dotenv import load_dotenv

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

load_dotenv()

def test_sqlalchemy_minimal():
    """Test SQLAlchemy with minimal configuration"""
    try:
        from sqlalchemy import create_engine, text
        
        print("🐘 SQLALCHEMY MINIMAL CONFIGURATION TEST")
        print("=" * 50)
        
        # Use the exact same credentials that work with pure psycopg2
        connection_url = "postgresql+psycopg2://postgres:ABDOABDO@localhost:5432/Planitor_db"
        
        print(f"🔗 Connection URL: {connection_url.replace('Pos196699@', '***')}")
        
        # Minimal engine creation
        engine = create_engine(
            connection_url,
            echo=True  # Show SQL
        )
        
        print("🔧 Testing connection...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ SQLALCHEMY CONNECTION SUCCESSFUL!")
            print(f"📊 Version: {version}")
            
        return True
        
    except Exception as e:
        print(f"❌ SQLAlchemy connection failed: {e}")
        print("\n🔧 TROUBLESHOOTING:")
        print("1. Check if SQLAlchemy and psycopg2 versions are compatible")
        print("2. Try different SQLAlchemy connection options")
        print("3. Verify the connection URL format")
        return False

if __name__ == "__main__":
    test_sqlalchemy_minimal()