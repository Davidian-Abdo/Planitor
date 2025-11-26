import streamlit as st
import logging
import traceback
from datetime import datetime

logger = logging.getLogger(__name__)

def debug_form_initialization(form_name, form_prefix):
    """Tracks initialization of forms and key prefix reuse"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    key_name = f"{form_name}:{form_prefix}"

    if "form_instances" not in st.session_state:
        st.session_state.form_instances = {}

    # Detect prefix reuse
    if form_prefix in st.session_state.form_instances.values():
        logger.warning(f"⚠️ {timestamp} DUPLICATE PREFIX DETECTED: '{form_prefix}' used by another form.")
        print(f"[{timestamp}] ⚠️ DUPLICATE PREFIX DETECTED: '{form_prefix}' used by another form.")

    # Detect multiple instantiations of same form
    if key_name in st.session_state.form_instances:
        logger.warning(f"⚠️ {timestamp} FORM RECREATED: {key_name}")
        print(f"[{timestamp}] ⚠️ FORM RECREATED: {key_name}")

    st.session_state.form_instances[key_name] = form_prefix
    print(f"[{timestamp}] ✅ Registered form '{form_name}' with prefix '{form_prefix}'")

def debug_widget_key(key):
    """Detect duplicate widget key usage"""
    timestamp = datetime.now().strftime("%H:%M:%S")

    if "registered_widget_keys" not in st.session_state:
        st.session_state.registered_widget_keys = set()

    if key in st.session_state.registered_widget_keys:
        msg = f"❌ DUPLICATE WIDGET KEY DETECTED: '{key}'"
        logger.error(msg)
        print(f"[{timestamp}] {msg}")
        st.error(msg)
        traceback.print_stack(limit=5)
    else:
        st.session_state.registered_widget_keys.add(key)
        print(f"[{timestamp}] 🧩 Registered widget key: {key}")