
"""
Test individual page loading
"""
import streamlit as st
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_pages():
    st.set_page_config(page_title="Page Test", layout="wide")
    
    st.title("📄 Page Loading Test")
    
    # Initialize minimal services
    try:
        from backend.db.session import get_db_session, init_database
        from backend.services.user_service import UserService
        
        init_database()
        db_session = get_db_session()
        user_service = UserService(db_session)
        
        st.session_state.db_session = db_session
        st.session_state.user_service = user_service
        
        st.success("✅ Services initialized")
        
    except Exception as e:
        st.error(f"❌ Service init failed: {e}")
        return
    
    # Test each page
    pages = {
        "project_setup": "pages.project_setup",
        "work_sequence": "frontend.pages.work_sequence",
        "templates_manager": "frontend.pages.templates_manager", 
        "generate_schedule": "frontend.pages.generate_schedule",
        "task_library": "frontend.pages.task_library",
        "progress_monitoring": "frontend.pages.progress_monitoring",
        "performance_dashboard": "frontend.pages.performance_dashboard",
        "reports_analytics": "frontend.pages.reports_analytics"
    }
    
    for page_name, page_module in pages.items():
        st.header(f"Page: {page_name}")
        
        try:
            module = __import__(page_module, fromlist=['show'])
            
            # Test if show function exists and is callable
            if hasattr(module, 'show') and callable(module.show):
                st.success(f"✅ {page_name} - show() function found")
                
                # Try to render the page
                with st.expander(f"Render {page_name}"):
                    try:
                        module.show(db_session, 1)  # Use test user ID
                        st.success(f"✅ {page_name} rendered successfully")
                    except Exception as e:
                        st.error(f"❌ {page_name} render failed: {e}")
                        st.code(str(e))
            else:
                st.error(f"❌ {page_name} - No show() function found")
                
        except Exception as e:
            st.error(f"❌ {page_name} - Import failed: {e}")
            import traceback
            with st.expander("Traceback"):
                st.code(traceback.format_exc())

if __name__ == "__main__":
    test_pages()