"""
Test project setup components in isolation
"""
import streamlit as st
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_project_setup_isolated():
    """Test project setup components without dependencies"""
    st.title("🏗️ Project Setup Isolation Test")
    
    # Initialize session state for test
    if 'project_config' not in st.session_state:
        st.session_state.project_config = {
            'basic_info': {'project_name': 'Test Project'},
            'zones': {},
            'advanced_settings': {}
        }
    
    # Test Basic Info Form
    st.subheader("1. Basic Info Form Test")
    project_name = st.text_input("Project Name", key="test_project_name")
    if st.button("Save Basic Info", key="test_save_basic"):
        st.session_state.project_config['basic_info']['project_name'] = project_name
        st.success(f"✅ Basic info saved: {project_name}")
    
    # Test Zone Management
    st.subheader("2. Zone Management Test")
    zone_name = st.text_input("Zone Name", key="test_zone_name")
    if st.button("Add Zone", key="test_add_zone"):
        if zone_name:
            st.session_state.project_config['zones'][zone_name] = 5
            st.success(f"✅ Zone added: {zone_name}")
        else:
            st.error("❌ Zone name required")
    
    # Display current zones
    st.write("Current zones:", st.session_state.project_config['zones'])
    
    # Test Advanced Settings
    st.subheader("3. Advanced Settings Test")
    work_hours = st.slider("Work Hours", 1, 24, 8, key="test_work_hours")
    if st.button("Save Advanced Settings", key="test_save_advanced"):
        st.session_state.project_config['advanced_settings']['work_hours'] = work_hours
        st.success(f"✅ Advanced settings saved: {work_hours} hours")
    
    # Test Save Section
    st.subheader("4. Save Section Test")
    if st.button("💾 Save Configuration", key="test_save_config"):
        st.success("✅ Configuration saved successfully!")
    
    # Session state debug
    st.subheader("🔧 Debug Info")
    st.json(st.session_state.project_config)

if __name__ == "__main__":
    test_project_setup_isolated()