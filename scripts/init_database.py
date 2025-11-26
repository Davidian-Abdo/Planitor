#!/usr/bin/env python3
"""
Database initialization script for PostgreSQL
"""
import sys
import os
import logging

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def initialize_postgresql_database():
    """Initialize PostgreSQL database with test data"""
    try:
        from backend.database.init import init_database, get_db_session, get_database_stats
        from backend.models.db_models import UserDB
        from backend.auth.password_utils import hash_password
        
        # Initialize database (creates tables)
        init_database()
        logger.info("✅ PostgreSQL database initialized")
        
        # Create test admin user
        db_session = get_db_session()
        
        # Check if admin already exists
        existing_admin = db_session.query(UserDB).filter_by(username='admin').first()
        if not existing_admin:
            admin_user = UserDB(
                username='admin',
                email='admin@construction.com',
                password_hash=hash_password('Admin123!@#'),
                full_name='System Administrator',
                role='admin'
            )
            db_session.add(admin_user)
            db_session.commit()
            logger.info("✅ PostgreSQL admin user created")
            logger.info("   Username: admin")
            logger.info("   Password: Admin123!@#")
        else:
            logger.info("ℹ️  Admin user already exists")
        
        # Show database stats
        stats = get_database_stats()
        logger.info(f"📊 PostgreSQL Database Info:")
        logger.info(f"   - Name: {stats.get('database_name')}")
        logger.info(f"   - Size: {stats.get('database_size')}")
        logger.info(f"   - Tables: {stats.get('table_count')}")
        logger.info(f"   - Connections: {stats.get('active_connections')}")
        
        db_session.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ PostgreSQL database initialization failed: {e}")
        logger.error("Troubleshooting tips:")
        logger.error("1. Check PostgreSQL service is running: services.msc")
        logger.error("2. Verify database 'construction_planner' exists")
        logger.error("3. Check user 'construction_user' has correct permissions")
        logger.error("4. Verify password in database configuration")
        return False

if __name__ == "__main__":
    print("🐘 Construction Project Planner - PostgreSQL Setup")
    print("=" * 50)
    
    if initialize_postgresql_database():
        print("🎉 PostgreSQL setup completed successfully!")
        print("🚀 You can now run: streamlit run app.py")
    else:
        print("💥 PostgreSQL setup failed!")
        sys.exit(1)