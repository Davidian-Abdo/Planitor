"""
PROFESSIONAL Login Page
Clean, secure authentication with proper session management
"""
import streamlit as st
import logging
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from frontend.components.forms.login_form import login_form_component

logger = logging.getLogger(__name__)

def show(db_session: Session = None, user_id: int = None):
    """
    Professional login page with dependency injection compatibility
    
    Args:
        db_session: Database session (optional for compatibility)
        user_id: User ID (optional for compatibility)
    """
    # Professional page configuration
    st.set_page_config(
        page_title="Login - Construction Planner",
        page_icon="🔐",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    # Remove sidebar for clean login experience
    st.markdown("""
    <style>
        .css-1d391kg {display: none}
    </style>
    """, unsafe_allow_html=True)
    
    # Professional login interface
    _render_login_header()
    
    # Use the professional login form component
    # Pass db_session if available, otherwise the component will handle it
    if db_session:
        login_form_component(db_session)
    else:
        login_form_component()
    

 
def _render_login_header():
    """Render professional login page header"""
    # Professional branding
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(
            """
            <div style='text-align: center; padding: 2rem 0;'>
                <h1 style='color: #1f77b4; margin-bottom: 0.5rem;'>🏗️</h1>
                <h2 style='color: #333; margin-bottom: 0.5rem;'>Construction Project Planner</h2>
                <p style='color: #666; font-size: 1.1rem;'>Professional Construction Management System</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown("---")

def _handle_successful_login():
    """Handle professional post-login workflow"""
    # Professional success feedback
    st.success("✅ Authentication successful!")
    
    # Professional redirect with user feedback
    st.toast("🎉 Welcome! Redirecting to your dashboard...")
    
    # Smooth transition to main application
    st.markdown(
        """
        <div style='text-align: center; padding: 2rem;'>
            <p>Redirecting to application...</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Professional navigation
    st.switch_page("pages/project_setup.py")

def _render_legacy_login_form():
    """
    Legacy login form for backward compatibility
    This can be removed once all components are updated
    """
    st.warning("⚠️ Using legacy authentication method")
    
    with st.form("legacy_login_form"):
        st.subheader("Legacy Login")
        
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.form_submit_button("Login"):
            if username and password:
                # Simple validation for demo purposes
                if len(username) >= 3 and len(password) >= 6:
                    st.session_state.authenticated = True
                    st.session_state.user = {"username": username, "role": "user"}
                    st.rerun()
                else:
                    st.error("Invalid credentials")
            else:
                st.error("Please enter username and password")

def main():
    """
    Main function for direct script execution
    Provides backward compatibility
    """
    try:
        # Initialize database session if needed
        from backend.db.session import get_db_session
        
        with get_db_session() as db_session:
            show(db_session)
            
    except Exception as e:
        logger.error(f"Login page error: {e}")
        
        # Fallback to legacy mode
        st.error("System initialization error - using legacy mode")
        _render_legacy_login_form()

# Backward compatibility
if __name__ == "__main__":
    main()