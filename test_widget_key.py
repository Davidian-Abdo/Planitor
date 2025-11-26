"""
Test widget key conflicts and management
"""
import streamlit as st
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from backend.utils.widget_manager import WidgetKeyManager

def test_widget_keys():
    """Test widget key generation and conflicts"""
    st.title("🔑 Widget Key Management Test")
    
    # Initialize widget manager
    widget_manager = WidgetKeyManager()
    user_id = 7
    page_context = "test_page"
    
    st.subheader("1. Key Generation Test")
    
    # Generate some test keys
    test_keys = []
    for i in range(5):
        key = widget_manager.generate_key(f"test_button_{i}", page_context, user_id)
        test_keys.append(key)
        st.write(f"Generated key {i}: {key}")
    
    # Test duplicate handling
    st.subheader("2. Duplicate Key Test")
    duplicate_key = widget_manager.generate_key("duplicate_test", page_context, user_id)
    st.write(f"First key: {duplicate_key}")
    
    duplicate_key2 = widget_manager.generate_key("duplicate_test", page_context, user_id)
    st.write(f"Second key (should be different): {duplicate_key2}")
    
    # Test button functionality with managed keys
    st.subheader("3. Buttons with Managed Keys")
    
    for i in range(3):
        button_key = widget_manager.generate_key(f"managed_button_{i}", page_context, user_id)
        if st.button(f"Managed Button {i}", key=button_key):
            st.success(f"✅ Button {i} clicked with key: {button_key}")
    
    # Registry inspection
    st.subheader("4. Registry Inspection")
    stats = widget_manager.get_registry_stats()
    st.json(stats)
    
    # Cleanup test
    if st.button("Cleanup Test Keys"):
        widget_manager.cleanup_page_keys(page_context)
        st.success("✅ Keys cleaned up")
        st.rerun()

if __name__ == "__main__":
    test_widget_keys()