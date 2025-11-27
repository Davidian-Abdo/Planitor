"""
frontend/components/forms/login_form.py
Professional Login Form Component with Register
"""

import streamlit as st
import logging


logger = logging.getLogger(__name__)

from backend.db.session import get_db_session
from backend.auth.auth_manager import AuthManager

# Professional login form
def login_form_component():
    db_session = get_db_session()  # get database session
    auth_manager = AuthManager(db_session)  # pass session

    st.title("🏗️ Professional Construction Planner Login")

    with st.form(key="login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        remember_me = st.checkbox("Remember me", value=False)
        
        col1, col2 = st.columns(2)
        with col1:
            login_submit = st.form_submit_button("Login")
        with col2:
            register_submit = st.form_submit_button("Register")
    
    
    # Handle register
    if register_submit:
        st.session_state['current_page'] = 'register'
        st.rerun()  
        
    # Handle login
    if login_submit:
        user_data = auth_manager.authenticate_user(username, password)
        if user_data:
            if 'session_manager' not in st.session_state:
                from backend.auth.session_manager import SessionManager
                st.session_state.session_manager = SessionManager()

            st.session_state.session_manager.create_session(user_data)
            st.session_state['current_page'] = 'project_setup'
            st.rerun()
        else:
            st.error("❌ Invalid username or password")
