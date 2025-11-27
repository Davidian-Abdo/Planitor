"""
User Registration Page
"""
import streamlit as st
from frontend.components.auth.registration_form import registration_form_component

st.set_page_config(
    page_title="Register ---- Planitor - plan and monitor your constructions",
    page_icon="👤",
    layout="centered"
)

def show(): 
    st.title("👤 Create Account")
    st.markdown("Join the Construction Project Planner platform")
    
    if registration_form_component():
        st.balloons()
        st.success("Account created successfully! You can now log in.")
        if st.button("Go to Login"): 
            st.switch_page('pages/login.py')
            st.session_state['current_page'] = 'login'
        
