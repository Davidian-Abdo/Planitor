"""
Root-level Debug Registration - No path issues
"""
import sys
import os
import logging
from datetime import datetime

# Set up logging to see everything
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_registration():
    print("🔧 REGISTRATION DEBUG - ROOT LEVEL")
    print("=" * 60)
    
    # Test data with unique timestamp
    timestamp = datetime.now().strftime('%H%M%S')
    test_username = f"testuser_{timestamp}"
    test_email = f"test{timestamp}@test.com"
    test_password = "Test123!"
    test_full_name = "Test User"
    test_role = "user"
    
    print(f"🧪 Test Data:")
    print(f"  Username: {test_username}")
    print(f"  Email: {test_email}")
    print(f"  Password: {test_password}")
    print()
    
    try:
        # Step 1: Test database connection
        print("1. Testing Database Connection...")
        from backend.db.session import get_db_session
        db_session = get_db_session()
        print("   ✅ Database connection successful")
        
        # Step 2: Test repository
        print("2. Testing User Repository...")
        from backend.db.repositories.user_repo import UserRepository
        user_repo = UserRepository(db_session)
        print("   ✅ User repository initialized")
        
        # Step 3: Check for existing users
        print("3. Checking for Existing Users...")
        existing_user = user_repo.get_user_by_username(test_username)
        existing_email_user = user_repo.get_user_by_email(test_email)
        
        print(f"   Existing username check: {existing_user is not None}")
        print(f"   Existing email check: {existing_email_user is not None}")
        
        if existing_user:
            print(f"   ❌ Username already exists: {existing_user.username}")
            return
        if existing_email_user:
            print(f"   ❌ Email already exists: {existing_email_user.email}")
            return
        
        print("   ✅ No duplicate users found")
        
        # Step 4: Test password hashing
        print("4. Testing Password Hashing...")
        from backend.auth.password_utils import hash_password
        try:
            password_hash = hash_password(test_password)
            print(f"   ✅ Password hashed successfully")
            print(f"   Hash: {password_hash[:50]}...")
        except Exception as e:
            print(f"   ❌ Password hashing failed: {e}")
            return
        
        # Step 5: Test direct user creation in repository
        print("5. Testing Direct User Creation (Repository Level)...")
        user_data = {
            "username": test_username,
            "email": test_email,
            "password_hash": password_hash,
            "full_name": test_full_name,
            "role": test_role,
            "is_active": True
        }
        
        print(f"   User data: {user_data}")
        
        try:
            created_user = user_repo.create_user(user_data)
            
            if created_user:
                print(f"   ✅ User created successfully!")
                print(f"   User ID: {created_user.id}")
                print(f"   Username: {created_user.username}")
                print(f"   Email: {created_user.email}")
                print(f"   Created at: {created_user.created_at}")
                
                # Step 6: Verify we can retrieve the user
                print("6. Verifying User Retrieval...")
                retrieved_user = user_repo.get_user_by_username(test_username)
                if retrieved_user:
                    print(f"   ✅ User retrieved successfully: {retrieved_user.username}")
                else:
                    print("   ❌ User created but cannot be retrieved!")
                
                # Step 7: Cleanup
                print("7. Cleaning up test user...")
                db_session.delete(created_user)
                db_session.commit()
                print("   ✅ Test user cleaned up")
                
            else:
                print("   ❌ User creation returned None (no exception thrown)")
                print("   This suggests the create_user method is failing silently")
                
        except Exception as e:
            print(f"   ❌ User creation failed with exception: {e}")
            import traceback
            print("   Full traceback:")
            print(traceback.format_exc())
            db_session.rollback()
        
        db_session.close()
        print("\n🎉 REPOSITORY LEVEL TEST COMPLETED")
        
    except Exception as e:
        print(f"❌ MAJOR ERROR: {e}")
        import traceback
        print("FULL TRACEBACK:")
        print(traceback.format_exc())

def test_service_layer():
    print("\n" + "=" * 60)
    print("🔧 TESTING SERVICE LAYER")
    print("=" * 60)
    
    timestamp = datetime.now().strftime('%H%M%S')
    test_username = f"serviceuser_{timestamp}"
    test_email = f"service{timestamp}@test.com"
    
    try:
        from backend.db.session import get_db_session
        from backend.services.user_service import UserService
        
        db_session = get_db_session()
        user_service = UserService(db_session)
        
        print("Testing UserService.create_user()...")
        user = user_service.create_user(
            username=test_username,
            email=test_email,
            password="Test123!",
            full_name="Service Test User",
            role="user"
        )
        
        if user:
            print(f"   ✅ Service layer user creation successful!")
            print(f"   User: {user.username} ({user.email})")
            
            # Cleanup
            db_session.delete(user)
            db_session.commit()
        else:
            print("   ❌ Service layer user creation returned None")
            
        db_session.close()
        
    except Exception as e:
        print(f"❌ Service layer test failed: {e}")
        import traceback
        print(traceback.format_exc())

def test_auth_manager():
    print("\n" + "=" * 60)
    print("🔧 TESTING AUTH MANAGER")
    print("=" * 60)
    
    timestamp = datetime.now().strftime('%H%M%S')
    test_username = f"authuser_{timestamp}"
    test_email = f"auth{timestamp}@test.com"
    
    try:
        from backend.db.session import get_db_session
        from backend.auth.auth_manager import AuthManager
        
        db_session = get_db_session()
        auth_manager = AuthManager(db_session)
        
        print("Testing AuthManager.register_user()...")
        result = auth_manager.register_user(
            username=test_username,
            email=test_email,
            password="Test123!",
            full_name="Auth Test User",
            role="user"
        )
        
        if result:
            print(f"   ✅ Auth manager registration successful!")
            print(f"   Result keys: {list(result.keys())}")
            print(f"   Username: {result.get('username')}")
            
            # Cleanup - get user by ID and delete
            from backend.db.repositories.user_repo import UserRepository
            user_repo = UserRepository(db_session)
            user = user_repo.get_user_by_username(test_username)
            if user:
                db_session.delete(user)
                db_session.commit()
        else:
            print("   ❌ Auth manager registration returned None")
            
        db_session.close()
        
    except Exception as e:
        print(f"❌ Auth manager test failed: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    debug_registration()
    test_service_layer() 
    test_auth_manager()