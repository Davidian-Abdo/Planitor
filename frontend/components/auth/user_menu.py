"""
Enhanced User menu component compatible with SessionManager
"""
import streamlit as st

def user_menu_component(db_session, user_id: int):
    """Enhanced user menu with SessionManager integration"""
    
    # ✅ Use SessionManager for authentication check
    if 'session_manager' not in st.session_state:
        return
    
    session_manager = st.session_state.session_manager
    
    if not session_manager.is_authenticated():
        return
    
    # ✅ Get user info from SessionManager
    user_info = {
        'username': session_manager.get_username(),
        'role': session_manager.get_user_role(),
        'full_name': session_manager.get_username()  # Fallback
    }
    
    with st.sidebar:
        st.markdown("---")
        st.markdown(f"### 👤 {user_info['full_name']}")
        st.markdown(f"**Role:** {user_info['role']}")
        
        # ✅ Get session info from SessionManager
        session_info = session_manager.get_session_info()
        if session_info.get('login_time'):
            from datetime import datetime
            login_time = session_info['login_time']
            if isinstance(login_time, str):
                login_time = datetime.fromisoformat(login_time.replace('Z', '+00:00'))
            st.markdown(f"**Last Login:** {login_time.strftime('%Y-%m-%d %H:%M')}")
        else:
            st.markdown("**Last Login:** Never")
        
        # ✅ Show session timeout warning
        timeout_warning = session_manager.get_session_timeout_warning()
        if timeout_warning:
            st.warning(f"⏰ {timeout_warning['message']}")
        
        # ✅ Enhanced logout with SessionManager
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            try:
                session_manager.logout()
                st.success("✅ Logged out successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Logout failed: {e}")
        
        # ✅ Admin panel link with proper role check
        if user_info['role'] == 'admin':
            st.markdown("---")
            if st.button("⚙️ Admin Panel", use_container_width=True):
                st.switch_page("pages/admin.py")