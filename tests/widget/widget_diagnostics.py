"""
GLOBAL Streamlit Widget & Form Diagnostics Tool
------------------------------------------------
This script intercepts ALL Streamlit widget creation
and logs duplicates, including full traceback and source.
"""

import streamlit as st
import traceback
import inspect
import uuid

# GLOBAL STORAGES
REGISTERED_KEYS = set()
REGISTERED_FORMS = set()
RUN_ID = uuid.uuid4().hex[:8]


def _trace_origin():
    """Return the call origin for debugging."""
    stack = traceback.format_stack(limit=8)
    return "".join(stack[:-1])


def _log(msg):
    print(f"[WidgetDiag] {msg}")


# ✅ Patch all widget functions dynamically
def _wrap_widget_function(func, func_name):
    def wrapper(*args, **kwargs):
        key = kwargs.get("key", None)

        if key:
            # Detect duplicate widget keys
            if key in REGISTERED_KEYS:
                _log(f"❌ DUPLICATE WIDGET KEY: '{key}' in widget <{func_name}>")
                _log("Origin:\n" + _trace_origin())
            else:
                REGISTERED_KEYS.add(key)
                _log(f"✅ Widget registered: {key}  ({func_name})")

        return func(*args, **kwargs)

    return wrapper


def _wrap_form_function(func):
    def wrapper(*args, **kwargs):
        form_key = kwargs.get("key") or ("form_" + uuid.uuid4().hex[:6])

        if form_key in REGISTERED_FORMS:
            _log(f"❌ DUPLICATE FORM KEY: '{form_key}'")
            _log("Origin:\n" + _trace_origin())
        else:
            REGISTERED_FORMS.add(form_key)
            _log(f"✅ Form registered: {form_key}")

        return func(*args, **kwargs)

    return wrapper


def enable_widget_diagnostics():
    """Activate global Streamlit widget diagnostics."""
    _log("🔍 Widget Diagnostics ENABLED")
    _log(f"Run ID: {RUN_ID}")

    widget_names = [
        "text_input", "selectbox", "date_input", "number_input",
        "text_area", "button", "checkbox", "radio", "slider",
        "multiselect", "file_uploader"
    ]

    # Patch widget functions
    for w in widget_names:
        if hasattr(st, w):
            orig_func = getattr(st, w)
            wrapped = _wrap_widget_function(orig_func, w)
            setattr(st, w, wrapped)

    # Patch st.form
    if hasattr(st, "form"):
        orig_form = st.form
        setattr(st, "form", _wrap_form_function(orig_form))

    _log("✅ Diagnostics successfully patched into Streamlit.")


# Automatically enable when imported
enable_widget_diagnostics()