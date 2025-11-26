"""
Test basic widget functionality isolated from main app
"""
import streamlit as st
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_basic_widgets():
    """Test if basic Streamlit widgets work"""
    st.title("🔧 Basic Widgets Test")
    
    # Test 1: Simple button
    if st.button("Simple Button Test"):
        st.success("✅ Simple button works!")
    else:
        st.info("Click the simple button above")
    
    # Test 2: Button with callback
    def test_callback():
        st.session_state.test_callback_worked = True
    
    if st.button("Button with Callback", on_click=test_callback):
        st.info("Button clicked")
    
    if st.session_state.get('test_callback_worked'):
        st.success("✅ Button callback works!")
    
    # Test 3: Form submission
    with st.form("test_form"):
        name = st.text_input("Enter name")
        submitted = st.form_submit_button("Submit Form")
        if submitted:
            st.success(f"✅ Form works! Name: {name}")
    
    # Test 4: Session state inspection
    st.subheader("Session State Inspection")
    st.write("Keys in session_state:", list(st.session_state.keys()))
    
    # Test 5: Rerun test
    if st.button("Test Rerun"):
        st.rerun()
        st.success("Rerun completed")

if __name__ == "__main__":
    test_basic_widgets()