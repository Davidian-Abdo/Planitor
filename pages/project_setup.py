import streamlit as st
import pandas as pd
import traceback
from datetime import datetime
import json 
import logging

# Import authentication system
from frontend.components.auth.auth_guard import require_auth

# Import professional components
from frontend.components.forms.project_forms import (
    ZoneConfigurationForm,
    ProjectBasicInfoForm
)

from frontend.components.navigation.sidebar import render_project_selector

logger = logging.getLogger(__name__)

@require_auth("write")
def show(db_session, services, user_id):
    """
    PROFESSIONAL Project Setup - CORRECTED VERSION
    Properly uses service layer as required
    """
    
    # ==================== INITIALIZE SESSION STATE ====================
    _initialize_session_state(user_id)
    
    # ==================== GET SERVICES ====================
    project_service = services['project_service']
    
    logger.info(f"🧱 Project Setup page loaded for user {user_id}")

    try:
        # Get session manager from session state
        session_manager = st.session_state.auth_session_manager
        user_info = _get_user_info(session_manager)
        
        # Professional header
        st.markdown('<div class="main-header">🏗️ Project Setup & Configuration</div>', unsafe_allow_html=True)
        st.caption(f"User: {user_info['username']} | Role: {user_info['role']}")
        
        # Render project selector
        render_project_selector(db_session, user_id)
        
        # ==================== FORM RENDERING WITH SERVICES ====================
        st.markdown("---")
        st.subheader("📋 Project Configuration")
        
        # Create form instances with injected services
        basic_form = ProjectBasicInfoForm(
            project_service=project_service,
            user_id=user_id,
            page_context="project_setup"
        )
        
        zone_form = ZoneConfigurationForm(
            project_service=project_service,
            user_id=user_id, 
            page_context="project_setup"
        )
        
        # Professional tab interface
        tab1, tab2, tab3 = st.tabs([
            "📋 Basic Information", 
            "🏢 Zones & Floors", 
            "⚙️ Advanced Configuration"
        ])
        
        with tab1:
            _render_basic_info_tab(basic_form, user_id)
        
        with tab2:
            _render_zones_config_tab(zone_form, user_id)
        
        with tab3:
            _render_advanced_config_tab(user_id, "project_setup")
        
        _render_save_section(project_service, user_id, "project_setup")
        
    except Exception as e:
        logger.error(f"❌ FATAL Error in project setup: {e}")
        st.error(f"❌ Fatal error loading project setup: {e}")
        st.code(traceback.format_exc())
        
def _initialize_session_state(user_id):
    """Initialize session state for project setup"""
    logger.debug(f"🔄 Initializing session state for user {user_id}")
    
    # Initialize project configuration
    if 'project_config' not in st.session_state:
        st.session_state.project_config = {
            'basic_info': {
                'project_name': 'My Construction Project',
                'project_manager': '',
                'start_date': datetime.now().date(),
                'description': '',
                'project_type': 'Commercial',
                'owner': '',
                'location': ''
            },
            'zones': {},
            'advanced_settings': {
                'work_hours_per_day': 8,
                'acceleration_factor': 1.0,
                'risk_allowance': 0.1
            }
        }
        logger.debug("✅ project_config initialized in session state")
    
    # Initialize zones state
    if 'project_zones' not in st.session_state:
        st.session_state.project_zones = {}
        logger.debug("✅ project_zones initialized in session state")

def _get_user_info(session_manager):
    """Get user information from SessionManager"""
    return {
        'id': session_manager.get_user_id(),
        'username': session_manager.get_username(),
        'role': session_manager.get_user_role(),
        'full_name': session_manager.get_username()
    }

def _render_basic_info_tab(form, user_id):
    """Basic info tab using service layer"""
    st.subheader("📋 Project Basic Information")
    
    try:
        result = form.render()
        
        if result:
            # Update project_config with validated form results
            st.session_state.project_config['basic_info'].update(result)
            st.success("✅ Basic project information updated!")
            logger.info(f"✅ Basic info updated: {result.get('project_name')}")
        
    except Exception as e:
        st.error(f"❌ Basic form render error: {e}")
        logger.error(f"❌ Basic form render failed: {e}")

def _render_zones_config_tab(form, user_id):
    """Zones config tab using service layer"""
    st.subheader("🏢 Building Zones Configuration")

    try:
        form.render()
        logger.debug("✅ Zone form rendered successfully")
        
    except Exception as e:
        st.error(f"❌ Zone form render error: {e}")
        logger.error(f"❌ Zone form render failed: {e}")

def _render_advanced_config_tab(user_id, page_context):
    """Advanced configuration tab"""
    logger.debug("🔄 Rendering advanced config tab")
    
    st.subheader("⚙️ Advanced Project Configuration")
    
    # Check if project_config exists
    if 'project_config' not in st.session_state:
        st.error("❌ Project configuration not initialized")
        return
    
    widget_manager = st.session_state.widget_manager
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Work Configuration")
        
        work_hours = st.number_input(
            "Work Hours Per Day",
            min_value=1,
            max_value=24,
            value=st.session_state.project_config['advanced_settings']['work_hours_per_day'],
            help="Standard working hours per day",
            key=widget_manager.generate_key("work_hours_input", page_context, user_id)
        )
        
        acceleration = st.slider(
            "Acceleration Factor",
            min_value=0.5,
            max_value=3.0,
            value=st.session_state.project_config['advanced_settings']['acceleration_factor'],
            step=0.1,
            help="Factor to accelerate schedule (may require more resources)",
            key=widget_manager.generate_key("acceleration_slider", page_context, user_id)
        )
    
    with col2:
        st.subheader("Risk & Contingency")
        risk_allowance = st.slider(
            "Risk Allowance (%)",
            min_value=0.0,
            max_value=50.0,
            value=st.session_state.project_config['advanced_settings']['risk_allowance'] * 100,
            step=5.0,
            help="Additional time allowance for risks and uncertainties",
            key=widget_manager.generate_key("risk_allowance_slider", page_context, user_id)
        )
    
    # Update advanced settings
    st.session_state.project_config['advanced_settings'].update({
        'work_hours_per_day': work_hours,
        'acceleration_factor': acceleration,
        'risk_allowance': risk_allowance / 100.0
    })
    
    logger.debug("✅ Advanced config updated")

def _render_save_section(project_service, user_id, page_context):
    """Save section using service layer"""
    logger.debug("🔄 Rendering save section")
    
    st.markdown("---")
    st.subheader("💾 Save Configuration")
    
    # Validate required session state exists
    if 'project_zones' not in st.session_state:
        st.error("❌ Zones configuration not initialized")
        return
    
    if 'project_config' not in st.session_state:
        st.error("❌ Project configuration not initialized")
        return
    
    widget_manager = st.session_state.widget_manager
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        save_button_key = widget_manager.generate_key("save_config_btn", page_context, user_id)
        
        if st.button("💾 Save Project Configuration", 
                    type="primary", 
                    use_container_width=True,
                    key=save_button_key):
            logger.info("💾 Save project configuration button clicked")
            _save_project_configuration(project_service, user_id)
    
    with col2:
        export_button_key = widget_manager.generate_key("export_json_btn", page_context, user_id)
        config_json = json.dumps(st.session_state.project_config, indent=2, default=str)
        st.download_button(
            "📥 Export JSON",
            data=config_json,
            file_name=f"project_config_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json",
            use_container_width=True,
            key=export_button_key
        )
    
    with col3:
        upload_key = widget_manager.generate_key("config_upload", page_context, user_id)
        uploaded_config = st.file_uploader(
            "Import Config",
            type=['json'],
            key=upload_key
        )
        
        if uploaded_config:
            try:
                imported_config = json.load(uploaded_config)
                st.session_state.project_config = imported_config
                st.success("✅ Configuration imported successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error importing configuration: {e}")

def _save_project_configuration(project_service, user_id):
    """Save project configuration using service layer"""
    logger.info(f"💾 Saving project configuration for user {user_id}")
    
    # Enhanced validation
    if 'project_zones' not in st.session_state or not st.session_state.project_zones:
        st.error("❌ Please configure at least one zone")
        logger.warning("❌ Save attempted without zones configured")
        return
    
    if 'project_config' not in st.session_state:
        st.error("❌ Project configuration not initialized")
        return
    
    project_name = st.session_state.project_config['basic_info'].get('project_name')
    project_manager = st.session_state.project_config['basic_info'].get('project_manager')
    
    if not project_name or not project_manager:
        st.error("❌ Please complete basic project information")
        logger.warning("❌ Save attempted with incomplete basic info")
        return
    
    try:
        # Get zones data
        zones_data = st.session_state.project_zones.copy()
        
        # Prepare complete project data
        project_data = {
            'name': project_name,
            'description': st.session_state.project_config['basic_info'].get('description', ''),
            'start_date': st.session_state.project_config['basic_info'].get('start_date'),
            'project_type': st.session_state.project_config['basic_info'].get('project_type', 'Commercial'),
            'owner': st.session_state.project_config['basic_info'].get('owner', ''),
            'location': st.session_state.project_config['basic_info'].get('location', ''),
            'zones': zones_data,
            'advanced_settings': st.session_state.project_config.get('advanced_settings', {})
        }
        
        logger.info(f"📊 Project data prepared for saving: {project_data['name']} with {len(zones_data)} zones")
        
        # ✅ USE SERVICE LAYER FOR VALIDATION
        validation_result = project_service.validate_project_configuration(project_data)
        
        if not validation_result['is_valid']:
            for error in validation_result['errors']:
                st.error(f"❌ {error}")
            logger.warning(f"❌ Project validation failed: {validation_result['errors']}")
            return
        
        # Show warnings
        for warning in validation_result['warnings']:
            st.warning(f"⚠️ {warning}")
        
        # ✅ USE SERVICE LAYER FOR SAVING
        with st.spinner("💾 Saving project configuration..."):
            if st.session_state.get('current_project_id'):
                # Update existing project using service
                success = project_service.update_project(user_id, st.session_state.current_project_id, project_data)
                if success:
                    st.success("✅ Project updated successfully!")
                    logger.info(f"✅ Project updated: {project_data['name']} (ID: {st.session_state.current_project_id})")
                    st.rerun()
                else:
                    st.error("❌ Failed to update project")
                    logger.error(f"❌ Project update failed: {project_data['name']}")
            else:
                # Create new project using service
                project_result = project_service.create_project(user_id, project_data)
                if project_result:
                    st.session_state.current_project_id = project_result['id']
                    st.session_state.current_project_name = project_result['name']
                    st.success("✅ Project created successfully!")
                    logger.info(f"✅ Project created: {project_result['name']} (ID: {project_result['id']})")
                    st.rerun()
                else:
                    st.error("❌ Failed to create project")
                    logger.error(f"❌ Project creation failed: {project_data['name']}")
                    
    except Exception as e:
        logger.error(f"❌ Error saving project configuration: {e}")
        st.error(f"❌ Error saving project configuration: {str(e)}")