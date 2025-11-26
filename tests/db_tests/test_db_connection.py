#!/usr/bin/env python3
"""
Test PostgreSQL connection - SQLAlchemy 2.0 compatible
"""
import sys
import os
import logging
import traceback

# Add project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../'))
sys.path.insert(0, project_root)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_postgresql_connection():
    """Test PostgreSQL connection with SQLAlchemy 2.0 syntax"""
    try:
        logger.info("🧪 Testing PostgreSQL connection...")
        
        # Test basic connection
        from backend.db.session import get_db_session
        from sqlalchemy import text  # ← ADD THIS IMPORT
        
        session = get_db_session()
        
        # SQLAlchemy 2.0 requires text() wrapper for raw SQL
        result = session.execute(text("SELECT version()"))  # ← WRAP IN text()
        postgres_version = result.scalar()
        logger.info(f"✅ Connected to: {postgres_version}")
        
        # Test database stats
        from backend.db.session import get_database_stats
        stats = get_database_stats()
        logger.info(f"📊 Database stats: {stats}")
        
        # Test creating a simple table to verify full functionality
        logger.info("🔄 Testing database operations...")
        
        # Create a simple test table if it doesn't exist
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS connection_test (
                id SERIAL PRIMARY KEY,
                test_name VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        session.commit()
        logger.info("✅ Test table created successfully")
        
        # Insert test data
        session.execute(text(
            "INSERT INTO connection_test (test_name) VALUES (:name)"
        ), {"name": "PostgreSQL Connection Test"})
        session.commit()
        logger.info("✅ Test data inserted successfully")
        
        # Query test data
        result = session.execute(text("SELECT COUNT(*) FROM connection_test"))
        count = result.scalar()
        logger.info(f"✅ Test data verified: {count} records")
        
        # Clean up
        session.execute(text("DROP TABLE IF EXISTS connection_test"))
        session.commit()
        logger.info("✅ Test cleanup completed")
        
        session.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ PostgreSQL connection failed: {e}")
        logger.error("🔍 FULL ERROR TRACEBACK:")
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    print("🐘 Local PostgreSQL Connection Test - SQLAlchemy 2.0")
    print("=" * 60)
    
    if test_postgresql_connection():
        print("\n🎉 🎉 🎉 POSTGRESQL CONNECTION SUCCESSFUL! 🎉 🎉 🎉")
        print("🚀 Your database is fully configured and working!")
        print("📁 You can now initialize the database and run the app!")
    else:
        print("\n💥 Connection failed. Please check the errors above.")