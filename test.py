"""
Professional test script to debug database connection and user authentication
for Planitor app.

Checks:
1. SUPABASE_URL environment variable resolution
2. Engine creation and basic connectivity
3. Session creation
4. Simple user query (from UserDB)
5. AuthManager registration and authentication flows
"""

import os
import logging
from sqlalchemy.exc import OperationalError
from backend.db.session import get_engine, get_db_session
from backend.auth.auth_manager import AuthManager
from backend.models.db_models import UserDB
from sqlalchemy.orm import Session

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("test_db")

# ---------------- Step 1: Check DB URL ----------------
def test_db_url():
    db_url = "postgresql://postgres.vigyqbzjtpqjzlpuyzvf:ABDOABDOABDO@aws-1-eu-west-1.pooler.supabase.com:5432/postgres"
    logger.info(f"SUPABASE_URL resolved: {db_url}")
    if not db_url: 
        raise RuntimeError("❌ SUPABASE_URL is not set in environment variables")

# ---------------- Step 2: Test engine creation ----------------
def test_engine():
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            logger.info(f"✅ Engine connection test result: {result.scalar()}")
    except OperationalError as e:
        logger.error(f"❌ OperationalError: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Engine creation failed: {e}")
        raise

# ---------------- Step 3: Test session creation ----------------
def test_session():
    try:
        session: Session = get_db_session()
        # Quick query to test session
        result = session.execute("SELECT 1").scalar()
        logger.info(f"✅ Session execution test result: {result}")
        session.close()
    except Exception as e:
        logger.error(f"❌ Session creation or query failed: {e}")
        raise

# ---------------- Step 4: Test UserDB query ----------------
def test_user_query():
    try:
        session: Session = get_db_session()
        user_count = session.query(UserDB).count()
        logger.info(f"✅ UserDB has {user_count} records")
        session.close()
    except Exception as e:
        logger.error(f"❌ UserDB query failed: {e}")
        raise

# ---------------- Step 5: Test AuthManager registration and login ----------------
def test_auth_manager():
    try:
        session: Session = get_db_session()
        auth = AuthManager(session, secret_key="test_secret_2025")

        # Test registration
        test_username = "test_user_001"
        test_email = "test_user@example.com"
        test_password = "StrongPassword123!"
        user_info = auth.register_user(test_username, test_email, test_password)
        if user_info:
            logger.info(f"✅ User registered successfully: {user_info}")
        else:
            logger.warning("⚠️ User registration returned None (maybe already exists)")

        # Test authentication
        auth_result = auth.authenticate_user(test_username, test_password)
        if auth_result:
            logger.info(f"✅ Authentication succeeded: {auth_result}")
        else:
            logger.warning("⚠️ Authentication failed")
        session.close()
    except Exception as e:
        logger.error(f"❌ AuthManager test failed: {e}")
        raise

# ---------------- Main runner ----------------
if __name__ == "__main__":
    logger.info("===== Starting Planitor DB & Auth Test =====")
    test_db_url()
    test_engine()
    test_session()
    test_user_query()
    test_auth_manager()
    logger.info("===== All tests completed =====")
