"""
Enhanced User registration form compatible with SessionManager
"""
import streamlit as st
from backend.auth.auth_manager import AuthManager

def registration_form_component() -> bool:
    """CORRECTED registration form with proper session management"""
    with st.form("registration_form"):
        st.subheader("👤 Create New Account")
        
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Full Name", placeholder="Enter your full name")
            username = st.text_input("Username", placeholder="Choose a username")
        with col2:
            email = st.text_input("Email", placeholder="your.email@company.com")
            role = st.selectbox("Role", ["Admin", "Directeur", "Ingénieur"], 
                              help="Ingénieur: Basic user, Directeurr: Manager access, Admin: Full system access")
        
        password = st.text_input("Password", type="password", 
                               placeholder="Create a strong password")
        confirm_password = st.text_input("Confirm Password", type="password", 
                                       placeholder="Confirm your password")
        
        agree_terms = st.checkbox("I agree to the terms and conditions")
        
        register_clicked = st.form_submit_button("Create Account", type="primary")
    
    if register_clicked:
        # Validate inputs
        if not all([full_name, username, email, password, confirm_password]):
            st.error("Please fill in all required fields")
            return False
        
        if password != confirm_password:
            st.error("Passwords do not match")
            return False
        
        # ✅ Use enhanced password validation
        from backend.utils.validators import Validator
        is_valid, errors = Validator.validate_user_data({
            'username': username,
            'email': email,
            'password': password
        })
        
        if not is_valid:
            for error in errors:
                st.error(f"❌ {error}")
            return False
        
        if not agree_terms:
            st.error("Please agree to the terms and conditions")
            return False
        
        # ✅ CORRECTED: Use single database session
        try:
            from backend.db.session import get_db_session
            db_session = get_db_session()
            
            # Create AuthManager with the session
            from backend.auth.auth_manager import AuthManager
            auth_manager = AuthManager(db_session)
            
            # Attempt registration
            result = auth_manager.register_user(
                username=username,
                email=email,
                password=password,
                full_name=full_name,
                role=role  # ✅ Use exact role values
            )
            
            if result:
                # ✅ Commit the transaction
                from backend.db.session import safe_commit
                if safe_commit(db_session, "User registration"):
                    st.success("✅ Account created successfully! You can now log in.")
                    
                    # ✅ Correct page redirection
                    st.session_state['current_page'] = "login"
                    return True
                else:
                    st.error("❌ Failed to save user to database")
                    return False
            else:
                st.error("❌ Username or email already exists")
                return False
                
        except Exception as e:
            st.error(f"❌ Registration failed: {str(e)}")
            # ✅ Ensure session is properly closed
            try:
                db_session.rollback()
                db_session.close()
            except:
                pass
            return False
        finally:
            try:
                db_session.close()
            except:
                pass
    
    return False