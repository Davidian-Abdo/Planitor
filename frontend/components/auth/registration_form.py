"""
Enhanced User registration form compatible with SessionManager
"""
import streamlit as st
from backend.auth.auth_manager import AuthManager

def registration_form_component() -> bool:
    """Enhanced registration form with proper session management"""
    with st.form("registration_form"):
        st.subheader("👤 Create New Account")
        
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Full Name", placeholder="Enter your full name")
            username = st.text_input("Username", placeholder="Choose a username")
        with col2:
            email = st.text_input("Email", placeholder="your.email@company.com")
            role = st.selectbox("Role", ["Ingénieur", "Directeur", "Admin"], 
                              help="Ingénieur: Basic user, Directeur: Manager access, Admin: Full system access")
        
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
        
        # ✅ Use enhanced password validation from SecurityConfig
        from backend.auth_config import validate_password_strength
        password_validation = validate_password_strength(password)
        if not password_validation['is_valid']:
            st.error("Password does not meet security requirements:")
            for issue in password_validation['issues']:
                st.error(f"• {issue}")
            return False
        
        if not agree_terms:
            st.error("Please agree to the terms and conditions")
            return False
        
        # ✅ Enhanced registration with proper error handling
        try:
            from backend.db.session import get_db_session
            with get_db_session() as db_session:
                auth_manager = AuthManager(db_session)
                
                result = auth_manager.register_user(
                    username=username,
                    email=email,
                    password=password,
                    full_name=full_name,
                    role=role.lower()  # ✅ Normalize role case
                )
                
                if result:
                    st.success("✅ Account created successfully! You can now log in.")
                    
                    # ✅ Optional: Auto-login after registration
                    if st.button("🔐 Login Now"):
                        st.switch_page("pages/login.py")
                    
                    return True
                else:
                    st.error("❌ Username or email already exists")
                    return False
                    
        except Exception as e:
            st.error(f"❌ Registration failed: {str(e)}")
            return False
    
    return False