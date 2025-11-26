"""
Admin Panel - User and System Management
"""
import streamlit as st
from frontend.components.auth.auth_guard import require_role
from backend.services.user_service import UserService

@require_role('admin')
def main():
    st.title("⚙️ Administration Panel")
    st.markdown("User and system management")
    
    tab1, tab2, tab3 = st.tabs(["👥 User Management", "📊 System Metrics", "⚙️ Settings"])
    
    with tab1:
        _render_user_management()
    
    with tab2:
        _render_system_metrics()
    
    with tab3:
        _render_system_settings()

def _render_user_management():
    """Render user management interface"""
    st.subheader("👥 User Management")
    
    user_service = UserService()
    users = user_service.get_all_users()
    
    if users:
        # Display users in a table
        user_data = []
        for user in users:
            user_data.append({
                'ID': user.id,
                'Username': user.username,
                'Email': user.email,
                'Role': user.role,
                'Status': 'Active' if user.is_active else 'Inactive',
                'Last Login': user.last_login
            })
        
        st.dataframe(user_data, use_container_width=True)
    else:
        st.info("No users found")

def _render_system_metrics():
    """Render system metrics"""
    st.subheader("📊 System Metrics")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Users", "25")
    with col2:
        st.metric("Active Projects", "12")
    with col3:
        st.metric("System Uptime", "99.8%")

def _render_system_settings():
    """Render system settings"""
    st.subheader("⚙️ System Settings")
    
    st.text_input("System Name", value="Construction Project Planner")
    st.number_input("Session Timeout (minutes)", value=120, min_value=15, max_value=480)
    st.checkbox("Enable Email Notifications", value=True)
    
    if st.button("Save Settings", type="primary"):
        st.success("Settings saved successfully!")

if __name__ == "__main__":
    main()