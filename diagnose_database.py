#!/usr/bin/env python3
"""
Professional Database & Services Diagnostic  
Run: python diagnose_database.py
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
    format='%(asctime)s - %(levelname)-8s - %(name)-20s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger('DBDiagnostic')

class DatabaseDiagnostic:
    def __init__(self):
        self.errors = []
        
    def log_error(self, message):
        logger.error(f"❌ {message}")
        self.errors.append(message)
        
    def log_success(self, message):
        logger.info(f"✅ {message}")
    
    def test_database_connection(self):
        """Test database connection and basic operations"""
        logger.info("🔍 Testing database connection...")
        
        try:
            from backend.db.session import get_db_session, init_database
            
            # Initialize database
            init_database()
            self.log_success("Database initialization successful")
            
            # Get session
            db_session = get_db_session()
            self.log_success("Database session acquired")
            
            # Test basic query
            from sqlalchemy import text
            result = db_session.execute(text("SELECT 1 as test_value"))
            test_value = result.scalar()
            
            if test_value == 1:
                self.log_success("Basic database query successful")
            else:
                self.log_error("Basic database query failed")
                
            # Close session
            db_session.close()
            self.log_success("Database session closed properly")
            
        except Exception as e:
            self.log_error(f"Database connection test failed: {e}")
    
    def test_user_service_with_real_user(self):
        """Test UserService with the actual user"""
        logger.info("🔍 Testing UserService with real user...")
        
        try:
            from backend.db.session import get_db_session
            from backend.services.user_service import UserService
            
            db_session = get_db_session()
            user_service = UserService(db_session)
            
            # Test getting the real user
            user = user_service.get_user_by_id(7)  # Using the real user_id
            
            if user:
                self.log_success(f"User found: {user.username} (ID: {user.id})")
                
                # Verify user data matches
                expected_data = {
                    'username': 'N.akkar',
                    'email': 'N.akkar@planitor.ma', 
                    'role': 'Admin',
                    'full_name': 'nabil akkar'
                }
                
                for field, expected_value in expected_data.items():
                    actual_value = getattr(user, field, None)
                    if actual_value == expected_value:
                        self.log_success(f"User {field} matches: {actual_value}")
                    else:
                        self.log_error(f"User {field} mismatch: expected '{expected_value}', got '{actual_value}'")
                        
            else:
                self.log_error("User with ID 7 not found in database")
                
            db_session.close()
            
        except Exception as e:
            self.log_error(f"UserService test failed: {e}")
    
    def test_authentication_flow(self):
        """Test complete authentication flow"""
        logger.info("🔍 Testing complete authentication flow...")
        
        try:
            from backend.db.session import get_db_session
            from backend.auth.auth_manager import AuthManager
            from backend.auth.session_manager import SessionManager
            
            db_session = get_db_session()
            auth_manager = AuthManager(db_session)
            session_manager = SessionManager()
            
            # Test 1: Try to authenticate (this will fail without real password, but test the flow)
            try:
                # This will likely fail, but we're testing the integration
                user_info = auth_manager.authenticate_user('N.akkar', 'test_password')
                if user_info:
                    self.log_success("Authentication successful")
                else:
                    self.log_warning("Authentication failed (expected without real password)")
            except Exception as auth_error:
                self.log_warning(f"Authentication attempt error: {auth_error}")
            
            # Test 2: Manual session creation (bypass auth for testing)
            manual_user_info = {
                'user_id': 7,
                'username': 'N.akkar',
                'email': 'N.akkar@planitorq;MA',
                'role': 'Admin',
                'full_name': 'nabil akkar',
                'token': 'manual_test_token'
            }
            
            session_created = session_manager.create_session(manual_user_info)
            
            if session_created and session_manager.is_authenticated():
                self.log_success("Manual session creation successful")
                
                # Verify the session data flows to Streamlit state
                import streamlit as st
                if st.session_state.get('authenticated'):
                    self.log_success("Streamlit session state updated correctly")
                else:
                    self.log_error("Streamlit session state NOT updated")
                    
            else:
                self.log_error("Manual session creation failed")
                
            db_session.close()
            
        except Exception as e:
            self.log_error(f"Authentication flow test failed: {e}")
    
    def run_all_tests(self):
        """Run all database diagnostics"""
        logger.info("🚀 Starting Database & Services Diagnostics")
        logger.info("=" * 60)
        
        self.test_database_connection()
        logger.info("")
        
        self.test_user_service_with_real_user()
        logger.info("")
        
        self.test_authentication_flow()
        logger.info("")
        
        # Summary
        logger.info("=" * 60)
        logger.info("📊 DATABASE DIAGNOSTIC SUMMARY")
        logger.info("=" * 60)
        
        if self.errors:
            logger.error(f"❌ {len(self.errors)} ERRORS found:")
            for error in self.errors:
                logger.error(f"   - {error}")
        else:
            logger.info("✅ No database errors found")
            
        if not self.errors:
            logger.info("🎉 Database layer is healthy!")
        else:
            logger.error("💥 Database issues detected that could cause blank page.")

if __name__ == "__main__":
    diagnostic = DatabaseDiagnostic()
    diagnostic.run_all_tests()