"""
Targeted debug for user retrieval failure
"""
import sys
import os
import logging
from pathlib import Path

sys.path.append(str(Path(__file__).parent / 'backend'))

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_user_retrieval():
    """Debug exactly why user retrieval fails"""
    logger.info("🔍 DEBUGGING USER RETRIEVAL FAILURE")
    
    from backend.db.session import init_database, get_db_session
    from backend.services.user_service import UserService
    from backend.auth.session_manager import SessionManager
    
    # Initialize
    init_database()
    db_session = get_db_session()
    user_service = UserService(db_session)
    session_manager = SessionManager()
    
    # Test 1: Check what users exist in database
    logger.info("📊 Checking all users in database...")
    all_users = user_service.get_all_users()
    logger.info(f"Found {len(all_users)} users in database:")
    for user in all_users:
        logger.info(f"  - User ID: {user.id}, Username: {user.username}, Email: {user.email}")
    
    # Test 2: Try to get user by ID (simulate what happens after login)
    logger.info("🔑 Testing user retrieval by ID...")
    
    # Try common user IDs that might exist
    test_user_ids = [1, 2, 3, 4, 5, 6, 7, 8]
    
    for user_id in test_user_ids:
        user = user_service.get_user_by_id(user_id)
        if user:
            logger.info(f"✅ FOUND USER: ID={user_id}, Username={user.username}")
        else:
            logger.info(f"❌ NO USER FOUND with ID={user_id}")
    
    # Test 3: Check session manager state
    logger.info("📱 Checking session manager...")
    logger.info(f"Session authenticated: {session_manager.is_authenticated()}")
    logger.info(f"Session user ID: {session_manager.get_user_id()}")
    
    # Test 4: Simulate login and see what user ID gets stored
    logger.info("👤 Testing authentication flow...")
    
    # Try to authenticate with a known user
    from backend.auth.auth_manager import AuthManager
    auth_manager = AuthManager(db_session, user_service)
    
    # If we have users, try to authenticate with the first one
    if all_users:
        test_user = all_users[0]
        logger.info(f"Attempting to authenticate as: {test_user.username}")
        
        auth_result = auth_manager.authenticate_user(test_user.username, "test_password")
        if auth_result:
            logger.info(f"✅ Authentication successful: {auth_result}")
            logger.info(f"Stored user ID: {session_manager.get_user_id()}")
        else:
            logger.info("❌ Authentication failed - wrong password or other issue")
    
    logger.info("🎯 USER RETRIEVAL DEBUG COMPLETED")

if __name__ == "__main__":
    debug_user_retrieval()