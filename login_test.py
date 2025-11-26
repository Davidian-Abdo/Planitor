# Add this to your debug_login.py or run separately
from datetime import datetime 

def test_register_and_login():
    print("\n" + "=" * 50)
    print("🔄 TEST REGISTER + IMMEDIATE LOGIN")
    print("=" * 50)
    
    timestamp = datetime.now().strftime('%H%M%S')
    username = f"immediate_{timestamp}"
    password = "Test123!"
    
    try:
        from backend.db.session import get_db_session
        from backend.auth.auth_manager import AuthManager
        
        db_session = get_db_session()
        auth_manager = AuthManager(db_session)
        
        print("1. Registering new user...")
        reg_result = auth_manager.register_user(
            username=username,
            email=f"{username}@test.com",
            password=password,
            full_name="Immediate Test",
            role="user"
        )
        
        if reg_result:
            print("✅ Registration successful")
            print(f"   User ID: {reg_result['user_id']}")
            
            print("\n2. Immediately trying to login...")
            login_result = auth_manager.authenticate_user(username, password)
            
            if login_result:
                print("✅ Login successful!")
                print(f"   Welcome {login_result['full_name']}")
            else:
                print("❌ Login FAILED right after registration!")
                print("   This indicates a serious password hashing issue")
        else:
            print("❌ Registration failed")
            
        db_session.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_register_and_login()