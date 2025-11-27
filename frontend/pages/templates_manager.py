"""
PROFESSIONAL Template Manager - REFACTORED & MODULAR
"""
import streamlit as st
import logging
from sqlalchemy.orm import Session
from typing import Dict , Any
from frontend.components.tabs.resource_library import render_resource_templates_tab
from frontend.components.tabs.task_library import render_task_library_tab
from frontend.components.tabs.template_association import render_template_associations_tab

logger = logging.getLogger(__name__)

def show(db_session: Session, services: Dict[str, Any], user_id: int):
    """DEBUG: Template manager with detailed error tracking"""
    try:
        st.title("🏗️ Gestionnaire de Templates Unifié")
        
        # ✅ DEBUG: Check session state before anything else
        st.write("🔍 DEBUG: Session state keys:", list(st.session_state.keys()))
        
        # ✅ DEBUG: Check if template_context exists
        if 'template_context' in st.session_state:
            st.write("✅ DEBUG: template_context exists in session state")
        else:
            st.write("❌ DEBUG: template_context MISSING from session state")
            # Initialize it immediately
            st.session_state.template_context = {
                'resource_template': None,
                'task_template': None,
                'last_updated': None,
                'initialized': False
            }
            st.write("✅ DEBUG: template_context created in session state")
        
        # Load professional CSS
        load_template_manager_css()
        
        if not services:
            st.error("❌ Erreur d'initialisation des services")
            return

        # Create THREE tabs for unified management
        tab1, tab2, tab3 = st.tabs([
            "📦 Bibliothèque des Ressources",
            "📚 Bibliothèque des Tâches", 
            "🔗 Associations & Validation"
        ])

        # ----------------- Tab 1: Unified Resource Templates -----------------
        with tab1:
            st.write("🔍 DEBUG: Before rendering resource tab")
            render_resource_templates_tab(services, user_id, db_session)
            st.write("🔍 DEBUG: After rendering resource tab")
        
        # ... rest of the tabs ...

    except Exception as e:
        logger.error(f"❌ Error in templates manager page: {e}")
        st.error(f"❌ Erreur lors du chargement du gestionnaire de templates: {e}")
        import traceback
        st.code(traceback.format_exc())


def load_template_manager_css():
    """Load professional CSS styles for template manager with correct path"""
    try:
        css_path = "frontend/styling/template_manager.css"
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        # Fallback inline styles
        st.markdown("""
        <style>
            .template-manager-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 25px;
                border-radius: 15px;
                color: white;
                margin-bottom: 30px;
                box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            }
            .filter-section {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                border-left: 4px solid #007bff;
            }
            .selected-row-actions {
                background: #e7f3ff;
                padding: 15px;
                border-radius: 8px;
                margin: 15px 0;
                border-left: 4px solid #007bff;
            }
            .submit-section {
                background: #d4edda;
                padding: 20px;
                border-radius: 10px;
                margin-top: 20px;
                border-left: 4px solid #28a745;
            }
            .template-card {
                background: white;
                padding: 20px;
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.08);
                margin-bottom: 20px;
                transition: transform 0.2s ease;
            }
            .template-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(0,0,0,0.12);
            }
            .stats-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 12px;
                text-align: center;
                margin: 10px 0;
            }
        </style>
        """, unsafe_allow_html=True)
    except Exception as e:
        logger.error(f"❌ Service initialization error: {e}")
        st.error(f"❌ Erreur d'initialisation des services: {e}")
        return None