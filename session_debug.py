"""
Debug session manager to see why authentication state is lost
"""
import sys
import os
import logging
from pathlib import Path

sys.path.append(str(Path(__file__).parent / 'backend'))

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_session_manager():
    """Test session manager functionality"""
    logger.info("🔍 DEBUGGING SESSION MANAGER")
    
    from backend.auth.session_manager import SessionManager
    
    # Create session manager
    session_manager = SessionManager()
    
    logger.info("1. Initial session state:")
    logger.info(f"   Authenticated: {session_manager.is_authenticated()}")
    logger.info(f"   User ID: {session_manager.get_user_id()}")
    logger.info(f"   Username: {session_manager.get_username()}")
    
    # Test login
    logger.info("2. Simulating login...")
    session_manager.login(8, "A.daoudi")  # Using your actual user
    
    logger.info("3. After login:")
    logger.info(f"   Authenticated: {session_manager.is_authenticated()}")
    logger.info(f"   User ID: {session_manager.get_user_id()}")
    logger.info(f"   Username: {session_manager.get_username()}")
    
    # Test session persistence
    logger.info("4. Creating new session manager instance (simulating page reload)...")
    session_manager2 = SessionManager()
    
    logger.info("5. New session manager state:")
    logger.info(f"   Authenticated: {session_manager2.is_authenticated()}")
    logger.info(f"   User ID: {session_manager2.get_user_id()}")
    logger.info(f"   Username: {session_manager2.get_username()}")
    
    logger.info("🎯 SESSION DEBUG COMPLETED")

if __name__ == "__main__":
    debug_session_manager()