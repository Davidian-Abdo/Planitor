"""
Blank Page Root Cause Analysis
Run: python analyze_blank_page.py
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
logger = logging.getLogger('BlankPageAnalysis')

def analyze_blank_page_causes():
    """Analyze potential causes for blank page after login"""
    logger.info("🚨 BLANK PAGE ROOT CAUSE ANALYSIS")
    logger.info("=" * 60)
    
    issues_found = []
    
    try:
        import streamlit as st
        from backend.auth.session_manager import SessionManager
        
        # Test 1: Check if session_manager exists in session state
        logger.info("🔍 1. Checking session_manager in session state...")
        if 'session_manager' not in st.session_state:
            logger.error("❌ session_manager NOT in session state")
            issues_found.append("session_manager missing from session state")
        else:
            logger.info("✅ session_manager exists in session state")
        
        # Test 2: Check authentication state
        logger.info("🔍 2. Checking authentication state...")
        session_manager = SessionManager()
        if session_manager.is_authenticated():
            logger.info("✅ User is authenticated")
        else:
            logger.error("❌ User is NOT authenticated")
            issues_found.append("User not authenticated after login")
        
        # Test 3: Check backward compatibility user object
        logger.info("🔍 3. Checking backward compatibility...")
        user_obj = st.session_state.get('user')
        if user_obj:
            logger.info("✅ Backward compatibility user object exists")
            logger.info(f"   User object: {user_obj}")
        else:
            logger.error("❌ Backward compatibility user object MISSING")
            issues_found.append("st.session_state.user missing - will break existing pages")
        
        # Test 4: Check critical session keys
        logger.info("🔍 4. Checking critical session keys...")
        critical_keys = ['authenticated', 'user_id', 'username', 'role', 'user']
        missing_keys = []
        
        for key in critical_keys:
            if key not in st.session_state:
                missing_keys.append(key)
        
        if missing_keys:
            logger.error(f"❌ Missing session keys: {missing_keys}")
            issues_found.append(f"Missing session keys: {missing_keys}")
        else:
            logger.info("✅ All critical session keys present")
        
        # Test 5: Check app.py dependencies
        logger.info("🔍 5. Checking app.py dependency injection...")
        try:
            from app import ConstructionApp
            app = ConstructionApp()
            logger.info("✅ ConstructionApp can be initialized")
            
            # Test dependency injection method
            if hasattr(app, '_inject_dependencies') and callable(app._inject_dependencies):
                logger.info("✅ _inject_dependencies method exists")
            else:
                logger.error("❌ _inject_dependencies method missing or not callable")
                issues_found.append("Dependency injection method issue in app.py")
                
        except Exception as e:
            logger.error(f"❌ ConstructionApp initialization failed: {e}")
            issues_found.append(f"App initialization failed: {e}")
        
        # Summary
        logger.info("=" * 60)
        logger.info("📊 BLANK PAGE ANALYSIS SUMMARY")
        logger.info("=" * 60)
        
        if issues_found:
            logger.error(f"🚨 Found {len(issues_found)} issues that could cause blank page:")
            for i, issue in enumerate(issues_found, 1):
                logger.error(f"   {i}. {issue}")
            
            logger.info("\n💡 RECOMMENDED FIXES:")
            if "st.session_state.user missing" in str(issues_found):
                logger.info("   • Fix: Ensure SessionManager creates st.session_state.user for backward compatibility")
            if "session_manager missing" in str(issues_found):
                logger.info("   • Fix: Initialize session_manager in app.py before using it")
            if "User not authenticated" in str(issues_found):
                logger.info("   • Fix: Verify login flow creates valid session")
                
            return False
        else:
            logger.info("🎉 No obvious issues found in session state")
            logger.info("💡 The blank page might be caused by:")
            logger.info("   • Frontend component rendering errors")
            logger.info("   • Missing Streamlit pages")
            logger.info("   • JavaScript errors in browser")
            logger.info("   • Check browser console for errors (F12)")
            return True
            
    except Exception as e:
        logger.error(f"💥 Analysis failed: {e}")
        return False

if __name__ == "__main__":
    success = analyze_blank_page_causes()
    sys.exit(0 if success else 1)