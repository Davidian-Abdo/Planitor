"""
Debug Login Process
"""
import sys
import os
from datetime import datetime

def debug_login():
    print("🔧 DEBUG LOGIN PROCESS")
    print("=" * 50)
    
    # Test credentials (use the same as registration test)
    test_username = "testuser_155408"
    test_password = "Test123!"
    
    print(f"Testing login for:")
    print(f"  Username: {test_username}")
    print(f"  Password: {test_password}")
    print()
    
    try:
        from backend.db.session import get_db_session
        from backend.auth.auth_manager import AuthManager
        from backend.db.repositories.user_repo import UserRepository
        from backend.auth.password_utils import verify_password
        
        db_session = get_db_session()
        
        print("1. Checking if user exists in database...")
        user_repo = UserRepository(db_session)
        user = user_repo.get_user_by_username(test_username)
        
        if not user:
            print("❌ User not found in database")
            return
        
        print(f"✅ User found: {user.username} (ID: {user.id})")
        print(f"   Email: {user.email}")
        print(f"   Password hash: {user.password_hash[:50]}...")
        
        print("\n2. Testing password verification...")
        print(f"   Input password: {test_password}")
        print(f"   Stored hash: {user.password_hash[:50]}...")
        
        # Test password verification directly
        is_valid = verify_password(test_password, user.password_hash)
        print(f"   Password verification result: {is_valid}")
        
        if not is_valid:
            print("❌ PASSWORD VERIFICATION FAILED")
            print("   This means the password stored during registration doesn't match")
            
        print("\n3. Testing AuthManager authentication...")
        auth_manager = AuthManager(db_session)
        auth_result = auth_manager.authenticate_user(test_username, test_password)
        
        if auth_result:
            print("✅ AuthManager authentication SUCCESS")
            print(f"   User data: {list(auth_result.keys())}")
        else:
            print("❌ AuthManager authentication FAILED")
            print("   This is what users see as 'Invalid username or password'")
        
        db_session.close()
        
    except Exception as e:
        print(f"❌ Error during login debug: {e}")
        import traceback
        traceback.print_exc()

def test_password_hashing():
    print("\n" + "=" * 50)
    print("🔐 TESTING PASSWORD HASHING CONSISTENCY")
    print("=" * 50)
    
    test_password = "Test123!"
    
    try:
        from backend.auth.password_utils import hash_password, verify_password
        
        print("Testing multiple hashes of the same password...")
        
        # Generate multiple hashes of the same password
        hashes = []
        for i in range(3):
            hash_result = hash_password(test_password)
            hashes.append(hash_result)
            print(f"  Hash {i+1}: {hash_result[:50]}...")
        
        print("\nTesting verification of all hashes...")
        for i, hash_val in enumerate(hashes):
            is_valid = verify_password(test_password, hash_val)
            print(f"  Verify hash {i+1}: {is_valid}")
            
        print("\nTesting wrong password verification...")
        wrong_valid = verify_password("wrongpassword", hashes[0])
        print(f"  Wrong password test: {wrong_valid} (should be False)")
        
    except Exception as e:
        print(f"❌ Password hashing test failed: {e}")

if __name__ == "__main__":
    debug_login()
    test_password_hashing()