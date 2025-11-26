"""
Enhanced Authentication guards compatible with SessionManager architecture
"""
import streamlit as st
from functools import wraps
from typing import Callable, Any

def require_auth(access_level: str = "read"):
    """
    Enhanced decorator compatible with new architecture
    
    Args:
        access_level: 'read', 'write', or 'admin'
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(db_session, user_id: int, *args, **kwargs) -> Any:
            # ✅ Use SessionManager instead of old session state
            if 'auth_session_manager' not in st.session_state:
                st.error("🔐 Session not initialized. Please log in.")
                if st.button("Go to Login"):
                    st.switch_page("pages/login.py")
                st.stop()
            
            session_manager = st.session_state.session_manager
            
            # ✅ Check authentication using SessionManager
            if not session_manager.is_authenticated():
                st.error("🔐 Authentication required. Please log in to access this page.")
                if st.button("Go to Login"):
                    st.switch_page("pages/login.py")
                st.stop()
            
            # ✅ Get user role from SessionManager
            user_role = session_manager.get_user_role()
            
            # Check access level
            if access_level == "Admin" and user_role != "Admin":
                st.error("🚫 Administrator access required for this page.")
                st.stop()
            elif access_level == "write" and user_role not in ["Admin", "Directeur"]:
                st.error("🚫 Manager or Admin access required for this page.")
                st.stop()
            
            # ✅ Call the function with injected dependencies
            return func(db_session, user_id, *args, **kwargs)
        return wrapper
    return decorator

def require_role(*allowed_roles):
    """
    Enhanced role-based decorator compatible with new architecture
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(db_session, user_id: int, *args, **kwargs) -> Any:
            # ✅ Use SessionManager for authentication check
            if 'session_manager' not in st.session_state:
                st.error("🔐 Session not initialized.")
                st.switch_page("pages/login.py")
                return
            
            session_manager = st.session_state.session_manager
            
            if not session_manager.is_authenticated():
                st.error("🔐 Authentication required.")
                st.switch_page("pages/login.py")
                return
            
            # ✅ Get user role from SessionManager
            user_role = session_manager.get_user_role()
            
            if user_role not in allowed_roles:
                st.error(f"🚫 Access denied. Required roles: {', '.join(allowed_roles)}")
                st.stop()
            
            # ✅ Call function with injected dependencies
            return func(db_session, user_id, *args, **kwargs)
        return wrapper
    return decorator