"""
Debug User Data Structure
"""
import sys
import os

def debug_user_structure():
    print("🔧 DEBUG USER DATA STRUCTURE")
    print("=" * 50)
    
    try:
        from backend.db.session import get_db_session
        from backend.auth.auth_manager import AuthManager
        
        db_session = get_db_session()
        auth_manager = AuthManager(db_session)
        
        # Test authentication and see what's returned
        print("1. Testing authentication...")
        result = auth_manager.authenticate_user("A.daoudi", "123456")
        
        print(f"2. Authentication result type: {type(result)}")
        if result:
            print(f"   Result keys: {list(result.keys())}")
            print(f"   Full result: {result}")
        else:
            print("   ❌ Authentication returned None")
            
        db_session.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def check_auth_manager():
    print("\n" + "=" * 50)
    print("🔍 CHECKING AUTH MANAGER CODE")
    print("=" * 50)
    
    try:
        # Let's see what the authenticate_user method returns
        from backend.auth.auth_manager import AuthManager
        import inspect
        
        source = inspect.getsource(AuthManager.authenticate_user)
        print("AuthManager.authenticate_user method:")
        print(source)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_user_structure()
    check_auth_manager()