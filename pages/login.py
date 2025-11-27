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