#!/usr/bin/env python3
"""
Test Session State Consistency 
Run: python test_session_consistency.py
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
logger = logging.getLogger('SessionConsistency')

def test_session_state_consistency():
    """Test that session state is consistent across all components"""
    logger.info("🔍 Testing Session State Consistency")
    logger.info("=" * 60)
    
    try:
        import streamlit as st
        from backend.auth.session_manager import SessionManager
        
        # Create a test session with exact user data
        test_user_info = {
            'user_id': 7,
            'username': 'N.akkar',
            'email': 'N.akkar@planitor.ma',
            'role': 'Admin',
            'full_name': 'nabil akkar',
            'token': 'test_jwt_token'
        }
        
        session_manager = SessionManager()
        session_created = session_manager.create_session(test_user_info)
        
        if not session_created:
            logger.error("❌ Failed to create test session")
            return False
        
        logger.info("✅ Test session created")
        
        # Test 1: Check SessionManager vs Streamlit session state
        logger.info("🔍 Testing SessionManager vs Streamlit session state...")
        
        sm_authenticated = session_manager.is_authenticated()
        st_authenticated = st.session_state.get('authenticated', False)
        
        logger.info(f"SessionManager.is_authenticated(): {sm_authenticated}")
        logger.info(f"st.session_state.authenticated: {st_authenticated}")
        
        if sm_authenticated == st_authenticated:
            logger.info("✅ Authentication state consistent")
        else:
            logger.error("❌ Authentication state INCONSISTENT!")
            logger.error("   This will cause blank page issues")
            return False
        
        # Test 2: Check user object structure for backward compatibility
        logger.info("🔍 Testing backward compatibility user object...")
        
        user_from_sm = session_manager.get_session_info()
        user_from_st = st.session_state.get('user', {})
        
        logger.info(f"SessionManager user keys: {list(user_from_sm.keys())}")
        logger.info(f"Streamlit user keys: {list(user_from_st.keys()) if user_from_st else 'MISSING'}")
        
        if not user_from_st:
            logger.error("❌ st.session_state.user is MISSING!")
            logger.error("   This will break all existing pages expecting user object")
            return False
        
        # Test 3: Verify critical user object keys
        required_user_keys = ['id', 'username', 'role', 'full_name']
        missing_keys = [key for key in required_user_keys if key not in user_from_st]
        
        if missing_keys:
            logger.error(f"❌ User object missing keys: {missing_keys}")
            logger.error(f"   Current user object: {user_from_st}")
            return False
        else:
            logger.info("✅ User object has all required keys")
        
        # Test 4: Verify exact values in user object
        logger.info("🔍 Verifying exact user values in session state...")
        
        expected_values = {
            'id': 7,
            'username': 'N.akkar',
            'role': 'Admin', 
            'full_name': 'nabil akkar'
        }
        
        all_correct = True
        for key, expected_value in expected_values.items():
            actual_value = user_from_st.get(key)
            if actual_value == expected_value:
                logger.info(f"✅ {key}: {actual_value}")
            else:
                logger.error(f"❌ {key}: expected '{expected_value}', got '{actual_value}'")
                all_correct = False
        
        if not all_correct:
            logger.error("❌ User object values are incorrect!")
            return False
        
        logger.info("=" * 60)
        logger.info("🎉 SESSION STATE CONSISTENCY TEST PASSED!")
        return True
        
    except Exception as e:
        logger.error(f"💥 Session consistency test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_session_state_consistency()
    sys.exit(0 if success else 1)