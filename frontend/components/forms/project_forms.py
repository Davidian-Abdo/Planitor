"""
PROFESSIONAL Project Forms - PRODUCTION READY
Enhanced with session state persistence to prevent rerun issues
"""
import streamlit as st
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, date
import traceback
import logging

logger = logging.getLogger(__name__)

class ProjectBasicInfoForm:
    """Professional project basic information form with session state persistence"""
    
    def __init__(self, db_session=None, form_prefix="basic_info", user_id=None, page_context="project_setup"):
        """
        Initialize professional project form
        
        Args:
            db_session: Database session for data operations
            form_prefix: Unique prefix for widget keys
            user_id: Current user ID for context
            page_context: Page context for widget management
        """
        self.db_session = db_session
        self.form_prefix = form_prefix
        self.user_id = user_id
        self.page_context = page_context
        
        # Initialize widget manager
        from backend.utils.widget_manager import widget_manager
        self.widget_manager = widget_manager
        
        # ✅ INITIALIZE SESSION STATE FOR FORM DATA PERSISTENCE
        self._initialize_form_session_state()
        
        logger.debug(f"✅ ProjectBasicInfoForm initialized for user {user_id}")
    
    def _initialize_form_session_state(self):
        """Initialize session state for form data persistence"""
        form_key = f"basic_form_data_{self.user_id}_{self.page_context}"
        
        if form_key not in st.session_state:
            st.session_state[form_key] = {
                'project_name': 'Professional Construction Project',
                'project_manager': '',
                'start_date': datetime.now().date(),
                'description': '',
                'project_type': 'Commercial',
                'owner': '',
                'location': ''
            }
            logger.debug(f"✅ Form session state initialized: {form_key}")
        
        self.form_data = st.session_state[form_key]
    
    def render(self) -> Optional[Dict[str, Any]]:
        """
        Render professional project information form with session state persistence
        
        Returns:
            Dict with form data if saved, None otherwise
        """
        logger.debug("🔄 Rendering ProjectBasicInfoForm")
        
        st.markdown("### 🏗️ Professional Project Details")
        
        # Professional two-column layout
        col1, col2 = st.columns(2)
        
        with col1:
            # Project Name - ✅ USE SESSION STATE DATA
            project_name_key = self.widget_manager.generate_key("project_name", self.page_context, self.user_id)
            project_name = st.text_input(
                "📋 Project Name *",
                value=self.form_data['project_name'],  # ✅ Session state value
                help="Official name of your construction project",
                placeholder="e.g., Downtown Commercial Tower Construction",
                key=project_name_key
            )
            
            # Project Type - ✅ USE SESSION STATE DATA
            project_type_key = self.widget_manager.generate_key("project_type", self.page_context, self.user_id)
            project_type_options = ['Commercial', 'Residential', 'Industrial', 'school', 'hospital']
            current_type_index = project_type_options.index(self.form_data['project_type']) if self.form_data['project_type'] in project_type_options else 0
            
            project_type = st.selectbox(
                "🏢 Project Type *",
                options=project_type_options,
                index=current_type_index,  # ✅ Session state value
                help="Category of construction project",
                key=project_type_key
            )
            
            # Owner - ✅ USE SESSION STATE DATA
            owner_key = self.widget_manager.generate_key("owner", self.page_context, self.user_id)
            owner = st.text_input(
                "👥 owner/Maitre d'ouvrage",
                value=self.form_data['owner'],  # ✅ Session state value
                help="Name of the project client or project master",
                placeholder="e.g., ABC Development Corporation",
                key=owner_key
            )
            
        with col2:
            # Project Manager - ✅ USE SESSION STATE DATA
            project_manager_key = self.widget_manager.generate_key("project_manager", self.page_context, self.user_id)
            project_manager = st.text_input(
                "👨‍💼 Project Manager *",
                value=self.form_data['project_manager'],  # ✅ Session state value
                help="Lead project manager responsible for delivery",
                placeholder="e.g., Marie Dubois - Senior Project Manager",
                key=project_manager_key
            )
            
            # Start Date - ✅ USE SESSION STATE DATA
            start_date_key = self.widget_manager.generate_key("start_date", self.page_context, self.user_id)
            start_date = st.date_input(
                "📅 Project Start Date *",
                value=self.form_data['start_date'],  # ✅ Session state value
                min_value=date.today(),
                help="Planned commencement date for construction activities",
                key=start_date_key
            )
            
            # Location - ✅ USE SESSION STATE DATA
            location_key = self.widget_manager.generate_key("location", self.page_context, self.user_id)
            location = st.text_input(
                "📍 Project Location",
                value=self.form_data['location'],  # ✅ Session state value
                help="Physical address or location of construction site",
                placeholder="e.g., 123 Main Street, Downtown District",
                key=location_key
            )
        
        # Professional project description - ✅ USE SESSION STATE DATA
        description_key = self.widget_manager.generate_key("professional_description", self.page_context, self.user_id)
        description = st.text_area(
            "📝 Project Description & Scope",
            value=self.form_data['description'],  # ✅ Session state value
            help="Comprehensive description of project scope, objectives, and key deliverables",
            placeholder="Describe the project in detail...",
            height=100,
            key=description_key
        )
        
        # ✅ CRITICAL: UPDATE SESSION STATE WITH CURRENT FORM VALUES ON EVERY RENDER
        # This ensures data persists through Streamlit reruns
        self.form_data.update({
            'project_name': project_name,
            'project_type': project_type,
            'project_manager': project_manager,
            'start_date': start_date,
            'owner': owner,
            'location': location,
            'description': description
        })
        
        # Professional validation and submission
        save_button_key = self.widget_manager.generate_key("save_project_info", self.page_context, self.user_id)
        
        if st.button("💾 Save Professional Project Information", 
                    type="primary", 
                    use_container_width=True,
                    key=save_button_key):
            
            logger.info("💾 Save project information button clicked")
            
            validation_result = self._validate_form_data(
                project_name, project_manager, start_date
            )
            
            if validation_result['is_valid']:
                form_data = {
                    'project_name': project_name.strip(),
                    'project_type': project_type,
                    'project_manager': project_manager.strip(),
                    'start_date': start_date,
                    'owner': owner.strip(),
                    'location': location.strip(),
                    'description': description.strip(),
                    'created_at': datetime.now().isoformat(),
                    'status': 'planned'
                }
                
                logger.info(f"✅ Project basic info validated and prepared: {project_name}")
                
                # ✅ Clear form data after successful save if needed
                # self._clear_form_data()
                
                return form_data
            else:
                for error in validation_result['errors']:
                    st.error(f"❌ {error}")
                logger.warning(f"❌ Project basic info validation failed: {validation_result['errors']}")
        
        return None
    
    def _clear_form_data(self):
        """Clear form data from session state (optional)"""
        form_key = f"basic_form_data_{self.user_id}_{self.page_context}"
        if form_key in st.session_state:
            st.session_state[form_key] = {
                'project_name': '',
                'project_manager': '',
                'start_date': datetime.now().date(),
                'description': '',
                'project_type': 'Commercial',
                'owner': '',
                'location': ''
            }
    
    def _validate_form_data(self, project_name: str, project_manager: str, start_date: date) -> Dict[str, Any]:
        """
        Professional form validation with comprehensive checks
        
        Args:
            project_name: Project name input
            project_manager: Project manager input  
            start_date: Project start date input
            
        Returns:
            Validation results dictionary
        """
        errors = []
        
        # Project name validation
        if not project_name or not project_name.strip():
            errors.append("Project name is required for identification")
        elif len(project_name.strip()) < 4:
            errors.append("Project name should be at least 4 characters for proper identification")
        elif len(project_name.strip()) > 200:
            errors.append("Project name cannot exceed 200 characters")
        
        # Project manager validation
        if not project_manager or not project_manager.strip():
            errors.append("Project manager designation is required for accountability")
        elif len(project_manager.strip()) < 2:
            errors.append("Project manager name should be at least 2 characters")
        
        # Start date validation
        if start_date < date.today():
            errors.append("Project start date cannot be in the past for planning purposes")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }


class ZoneConfigurationForm:
    """Professional zone configuration form with correct zones format"""
    
    def __init__(self, db_session=None, user_id=None, page_context="project_setup"):
        """
        Initialize professional zone configuration form
        
        Args:
            db_session: Database session for data operations
            user_id: Current user ID for context
            page_context: Page context for widget management
        """
        self.db_session = db_session
        self.form_prefix = "zone"
        self.user_id = user_id
        self.page_context = page_context
        
        # Initialize widget manager
        from backend.utils.widget_manager import widget_manager
        self.widget_manager = widget_manager
        
        # ✅ INITIALIZE ZONES SESSION STATE FOR PERSISTENCE
        self._initialize_zones_session_state()
        
        logger.debug(f"✅ ZoneConfigurationForm initialized for user {user_id}")
    
    def _initialize_zones_session_state(self):
        """Initialize zones session state for persistence"""
        # Your existing zones initialization is correct
        if 'project_zones' not in st.session_state:
            st.session_state.project_zones = {}
            logger.debug("✅ project_zones initialized in session state")
        
        # ✅ ADDITIONAL: Initialize zone creation form state
        zone_form_key = f"zone_creation_form_{self.user_id}_{self.page_context}"
        if zone_form_key not in st.session_state:
            st.session_state[zone_form_key] = {
                'zone_name': '',
                'max_floors': 7,
                'zone_sequence': 1,
                'zone_description': ''
            }
        
        self.zone_form_data = st.session_state[zone_form_key]
    
    def render(self) -> None:
        """
        Render complete zone management interface
        """
        logger.debug("🔄 Rendering ZoneConfigurationForm")
        
        st.markdown("### 🏢 Professional Zone Configuration")
        
        # Section 1: Add New Zone Form
        self._render_zone_creation_section()
        
        # Section 2: Current Zones Display & Management
        if st.session_state.project_zones:
            self._render_zones_management_section()
        else:
            st.info("📝 No zones configured yet. Add your first zone above.")
            logger.debug("ℹ️ No zones configured in session state")
    
    def _render_zone_creation_section(self) -> None:
        """
        Render zone creation form with session state persistence
        """
        logger.debug("🔄 Rendering zone creation section")
        
        st.markdown("#### ➕ Add New Zone")
        
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            zone_name_key = self.widget_manager.generate_key("zone_name", self.page_context, self.user_id)
            zone_name = st.text_input(
                "🏷️ Zone Name *",
                value=self.zone_form_data['zone_name'],  # ✅ Session state value
                placeholder="e.g., Tower A, West Wing, Basement Parking",
                help="Unique identifier for this building zone or section",
                key=zone_name_key
            )
        
        with col2:
            max_floors_key = self.widget_manager.generate_key("max_floors", self.page_context, self.user_id)
            max_floors = st.number_input(
                "🏗️ Max Floors *",
                min_value=0, max_value=200, 
                value=self.zone_form_data['max_floors'],  # ✅ Session state value
                help="Total number of floors in this zone",
                key=max_floors_key
            )
        
        with col3:
            zone_sequence_key = self.widget_manager.generate_key("zone_sequence", self.page_context, self.user_id)
            zone_sequence = st.number_input(
                "🔢 Sequence",
                min_value=1, max_value=20, 
                value=self.zone_form_data['zone_sequence'],  # ✅ Session state value
                help="Construction sequence order for this zone",
                key=zone_sequence_key
            )
        
        zone_description_key = self.widget_manager.generate_key("zone_description", self.page_context, self.user_id)
        zone_description = st.text_area(
            "📝 Zone Description",
            value=self.zone_form_data['zone_description'],  # ✅ Session state value
            placeholder="Describe this zone's characteristics...",
            help="Additional information about this zone",
            height=60,
            key=zone_description_key
        )
        
        # ✅ UPDATE ZONE CREATION FORM STATE
        self.zone_form_data.update({
            'zone_name': zone_name,
            'max_floors': max_floors,
            'zone_sequence': zone_sequence,
            'zone_description': zone_description
        })
        
        add_zone_key = self.widget_manager.generate_key("add_zone", self.page_context, self.user_id)
        
        if st.button("➕ Add Professional Zone", 
                    use_container_width=True,
                    key=add_zone_key):
            
            logger.info(f"➕ Add zone button clicked: {zone_name}")
            
            validation_result = self._validate_zone_data(zone_name, max_floors)
            
            if validation_result['is_valid']:
                # ✅ CORRECT FORMAT: {zone_name: {max_floors: x, sequence: y, description: z}}
                st.session_state.project_zones[zone_name.strip()] = {
                    'max_floors': max_floors,
                    'sequence': zone_sequence,
                    'description': zone_description.strip()
                }
                
                # ✅ CLEAR ZONE CREATION FORM AFTER SUCCESSFUL ADD
                self._clear_zone_creation_form()
                
                st.success(f"✅ Zone '{zone_name}' added with {max_floors} floors (Sequence: {zone_sequence})!")
                logger.info(f"✅ Zone added to session state: {zone_name} with {max_floors} floors, sequence {zone_sequence}")
                st.rerun()
            else:
                for error in validation_result['errors']:
                    st.error(f"❌ {error}")
                logger.warning(f"❌ Zone validation failed: {validation_result['errors']}")
    
    def _clear_zone_creation_form(self):
        """Clear zone creation form data"""
        zone_form_key = f"zone_creation_form_{self.user_id}_{self.page_context}"
        st.session_state[zone_form_key] = {
            'zone_name': '',
            'max_floors': 7,
            'zone_sequence': 1,
            'zone_description': ''
        }
        self.zone_form_data = st.session_state[zone_form_key]
    
    def _render_zones_management_section(self):
        """
        Render zones management interface with professional controls
        """
        logger.debug("🔄 Rendering zones management section")
        
        st.markdown("---")
        st.markdown("#### 📋 Current Zones")
        
        # Display zones table
        self._render_zones_table()
        
        # Zone management controls
        self._render_zone_management_controls()
    
    def _render_zones_table(self):
        """
        Render professional zones table with summary metrics
        """
        logger.debug("🔄 Rendering zones table")
        
        zones_data = []
        for zone_name, zone_config in st.session_state.project_zones.items():
            zones_data.append({
                'Zone Name': zone_name,
                'Max Floors': zone_config.get('max_floors', 0),
                'Sequence': zone_config.get('sequence', 1),
                'Description': zone_config.get('description', '')
            })
        
        if zones_data:
            df = pd.DataFrame(zones_data)
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )
            
            # Professional summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                total_zones = len(st.session_state.project_zones)
                st.metric("Total Zones", total_zones)
            with col2:
                total_floors = sum(zone_config.get('max_floors', 0) for zone_config in st.session_state.project_zones.values())
                st.metric("Total Floors", total_floors)
            with col3:
                sequences = [zone_config.get('sequence', 1) for zone_config in st.session_state.project_zones.values()]
                if sequences:
                    st.metric("Sequence Range", f"{min(sequences)}-{max(sequences)}")
                else:
                    st.metric("Sequence Range", "N/A")
            
            logger.debug(f"✅ Zones table rendered with {len(zones_data)} zones")
    
    def _render_zone_management_controls(self):
        """
        Render professional zone management controls
        """
        logger.debug("🔄 Rendering zone management controls")
        
        st.markdown("#### 🛠️ Zone Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            removal_selector_key = self.widget_manager.generate_key("zone_removal_selector", self.page_context, self.user_id)
            zones_to_remove = st.multiselect(
                "Select zones to remove:",
                options=list(st.session_state.project_zones.keys()),
                help="Select zones to remove from configuration",
                key=removal_selector_key
            )
            
            remove_button_key = self.widget_manager.generate_key("remove_zones_btn", self.page_context, self.user_id)
            
            if st.button("🗑️ Remove Selected Zones", 
                        use_container_width=True,
                        key=remove_button_key) and zones_to_remove:
                
                logger.info(f"🗑️ Removing zones: {zones_to_remove}")
                
                for zone in zones_to_remove:
                    del st.session_state.project_zones[zone]
                
                st.success(f"✅ Removed zones: {', '.join(zones_to_remove)}")
                logger.info(f"✅ Zones removed successfully: {zones_to_remove}")
                st.rerun()
        
        with col2:
            clear_button_key = self.widget_manager.generate_key("clear_all_zones_btn", self.page_context, self.user_id)
            
            if st.button("🔄 Clear All Zones", 
                        use_container_width=True, 
                        type="secondary",
                        key=clear_button_key):
                
                confirm_key = self.widget_manager.generate_key("confirm_clear_checkbox", self.page_context, self.user_id)
                if st.checkbox("Confirm clear all zones", key=confirm_key):
                    st.session_state.project_zones = {}
                    st.success("✅ All zones cleared!")
                    logger.info("✅ All zones cleared from session state")
                    st.rerun()
    
    def _validate_zone_data(self, zone_name: str, max_floors: int) -> Dict[str, Any]:
        """
        Professional zone data validation
        
        Args:
            zone_name: Zone name input
            max_floors: Maximum floors input
            
        Returns:
            Validation results dictionary
        """
        errors = []
        
        # Zone name validation
        if not zone_name or not zone_name.strip():
            errors.append("Zone name is required for identification")
        elif len(zone_name.strip()) < 2:
            errors.append("Zone name should be at least 2 characters")
        elif len(zone_name.strip()) > 50:
            errors.append("Zone name cannot exceed 50 characters")
        elif zone_name.strip() in st.session_state.project_zones:
            errors.append(f"Zone '{zone_name}' already exists")
        
        # Max floors validation
        if max_floors < 0:
            errors.append("Maximum floors cannot be negative")
        elif max_floors > 200:
            errors.append("Maximum floors cannot exceed 200 for practical planning")
        elif max_floors == 0:
            errors.append("Maximum floors must be at least 1")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }
    
    def get_zones_data(self) -> Dict[str, Dict[str, Any]]:
        """
        Get current zones data in database-compatible format
        
        Returns:
            Dictionary with zone names as keys and zone config as values
            Format: {zone_name: {'max_floors': int, 'sequence': int, 'description': str}}
        """
        zones_data = st.session_state.project_zones.copy()
        logger.debug(f"📊 Retrieved zones data for saving: {zones_data}")
        return zones_data
    
    def get_zones_count(self) -> int:
        """
        Get total number of configured zones
        
        Returns:
            Integer count of zones
        """
        return len(st.session_state.project_zones)
    
    def get_total_floors(self) -> int:
        """
        Get total floors across all zones
        
        Returns:
            Integer sum of all zone floors
        """
        return sum(zone_config.get('max_floors', 0) for zone_config in st.session_state.project_zones.values())