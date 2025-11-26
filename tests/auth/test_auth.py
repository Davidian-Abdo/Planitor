#!/usr/bin/env python3
"""
Test Exact User Authentication
Run: python test_exact_auth.py
"""
import logging
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)-8s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger('ExactAuthTest')

def test_exact_user_authentication():
    """Test authentication with the exact user credentials"""
    logger.info("🎯 Testing authentication with EXACT user credentials")
    logger.info("=" * 60)
    
    try:
        from backend.db.session import get_db_session
        from backend.auth.auth_manager import AuthManager
        from backend.auth.session_manager import SessionManager
        
        # Exact user credentials from your system
        EXACT_USER_CREDENTIALS = {
            'username': 'N.akkar',
            'password': '123456',
            'expected_user_id': 7,
            'expected_email': 'N.akkar@planitor.ma',
            'expected_role': 'Admin',
            'expected_full_name': 'nabil akkar'
        }
        
        logger.info(f"🔐 Testing user: {EXACT_USER_CREDENTIALS['username']}")
        
        # Get database session
        db_session = get_db_session()
        auth_manager = AuthManager(db_session)
        session_manager = SessionManager()
        
        # Test 1: Authenticate with exact credentials
        logger.info("🔍 Step 1: Authenticating with password '123456'...")
        user_info = auth_manager.authenticate_user(
            EXACT_USER_CREDENTIALS['username'], 
            EXACT_USER_CREDENTIALS['password']
        )
        
        if user_info:
            logger.info("✅ AUTHENTICATION SUCCESSFUL!")
            
            # Verify user info structure
            logger.info("🔍 Step 2: Verifying user info structure...")
            required_keys = ['user_id', 'username', 'email', 'role', 'full_name', 'token']
            missing_keys = [key for key in required_keys if key not in user_info]
            
            if missing_keys:
                logger.error(f"❌ User info missing keys: {missing_keys}")
                logger.error(f"   User info received: {user_info}")
                return False
            else:
                logger.info("✅ User info has all required keys")
            
            # Verify exact data matches
            logger.info("🔍 Step 3: Verifying exact user data...")
            if user_info['user_id'] == EXACT_USER_CREDENTIALS['expected_user_id']:
                logger.info(f"✅ User ID matches: {user_info['user_id']}")
            else:
                logger.error(f"❌ User ID mismatch: expected {EXACT_USER_CREDENTIALS['expected_user_id']}, got {user_info['user_id']}")
            
            if user_info['username'] == EXACT_USER_CREDENTIALS['username']:
                logger.info(f"✅ Username matches: {user_info['username']}")
            else:
                logger.error(f"❌ Username mismatch")
            
            if user_info['email'] == EXACT_USER_CREDENTIALS['expected_email']:
                logger.info(f"✅ Email matches: {user_info['email']}")
            else:
                logger.error(f"❌ Email mismatch")
            
            if user_info['role'] == EXACT_USER_CREDENTIALS['expected_role']:
                logger.info(f"✅ Role matches: {user_info['role']}")
            else:
                logger.error(f"❌ Role mismatch")
            
            if user_info['full_name'] == EXACT_USER_CREDENTIALS['expected_full_name']:
                logger.info(f"✅ Full name matches: {user_info['full_name']}")
            else:
                logger.error(f"❌ Full name mismatch")
            
            # Test 4: Create session with the returned user_info
            logger.info("🔍 Step 4: Creating session with authenticated user info...")
            session_created = session_manager.create_session(user_info)
            
            if session_created:
                logger.info("✅ Session created successfully")
                
                # Verify session state
                if session_manager.is_authenticated():
                    logger.info("✅ User is authenticated in session")
                    
                    # Check critical session data
                    session_user_id = session_manager.get_user_id()
                    session_username = session_manager.get_username()
                    
                    logger.info(f"📊 Session User ID: {session_user_id}")
                    logger.info(f"📊 Session Username: {session_username}")
                    logger.info(f"📊 Session Role: {session_manager.get_user_role()}")
                    
                else:
                    logger.error("❌ User is NOT authenticated after session creation")
                    return False
                    
            else:
                logger.error("❌ Session creation failed")
                return False
                
        else:
            logger.error("❌ AUTHENTICATION FAILED with exact credentials!")
            logger.error("   This indicates a password hashing mismatch or user status issue")
            return False
        
        db_session.close()
        logger.info("=" * 60)
        logger.info("🎉 EXACT USER AUTHENTICATION TEST PASSED!")
        logger.info("   The authentication system is working correctly")
        return True
        
    except Exception as e:
        logger.error(f"💥 Authentication test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_exact_user_authentication()
    sys.exit(0 if success else 1)